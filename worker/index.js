// Cloudflare Worker for launchleadgen.io static site.
// Static files in ./site are served directly; only /api/* runs this code.
// POST /api/inquiry forwards the contact form to the existing launchleadgen.io
// WordPress form (Breakdance form 113), so submissions reach the same inbox.

const UPSTREAM = "https://launchleadgen.io/wp-admin/admin-ajax.php";
const FALLBACK = "Please call (210) 441-6650 or email info@launchleadgen.com.";
const SMS_CONSENT = "I Consent to Receive SMS Notifications, Alerts & Occasional Marketing Communication from Launch Lead Gen. Message frequency varies. Message & data rates may apply. You can reply STOP to unsubscribe at any time.*";

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "Cache-Control": "no-store" } });
}

export async function readLimited(response, limit) {
  if (!response.body) return "";
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) {
        await reader.cancel();
        throw new Error("Payload too large");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder().decode(bytes);
}

export async function handleInquiry(request, send = fetch) {
  if (request.method !== "POST") return json({ error: "Use POST." }, 405);
  if (request.headers.get("Origin") !== new URL(request.url).origin) return json({ error: "Please submit from this website." }, 403);
  if (!(request.headers.get("Content-Type") || "").startsWith("application/json")) return json({ error: "Invalid request format." }, 415);

  let fields;
  try {
    fields = JSON.parse(await readLimited(request, 12e3));
  } catch {
    return json({ error: "Please check your request and try again." }, 400);
  }
  if (!fields || typeof fields !== "object" || Array.isArray(fields)) return json({ error: "Invalid request." }, 400);
  if (fields.website) return json({ error: "Unable to submit this request." }, 400); // honeypot

  const limits = { name: 100, company: 160, email: 254, phone: 40, zips: 200, message: 3e3 };
  const clean = {};
  for (const [key, limit] of Object.entries(limits)) {
    if (typeof fields[key] !== "string" || fields[key].length > limit) return json({ error: "Please check your contact details." }, 400);
    clean[key] = fields[key].trim();
  }
  if (clean.name.length < 2 || clean.company.length < 2 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(clean.email) ||
      clean.phone.replace(/\D/g, "").length < 10 || !/^\d{5}(?:[\s,]+\d{5})*$/.test(clean.zips)) {
    return json({ error: "Enter your name, company, email, phone and valid 5-digit ZIP codes." }, 400);
  }
  const services = fields.services;
  if (!Array.isArray(services) || !services.length || services.length > 2 || services.some((s) => !["drainage", "irrigation"].includes(s))) {
    return json({ error: "Choose drainage, irrigation, or both." }, 400);
  }

  const payload = new FormData();
  payload.set("action", "breakdance_form_custom");
  payload.set("form_id", "113");
  payload.set("post_id", "14");
  payload.set("fields[name]", clean.name);
  payload.set("fields[email]", clean.email);
  payload.set("fields[wxhvsv]", clean.phone);
  payload.set("fields[message]", `Territory inquiry from the website\nCompany: ${clean.company}\nServices: ${services.join(", ")}\nZIP codes: ${clean.zips}\n\n${clean.message}`);
  if (fields.smsConsent === true) payload.set("fields[yvqugu]", SMS_CONSENT);

  try {
    const response = await send(UPSTREAM, { method: "POST", body: payload, signal: AbortSignal.timeout(15e3), redirect: "error" });
    const result = JSON.parse(await readLimited(response, 64e3));
    if (!response.ok || result.success !== true) return json({ error: `Your request wasn't accepted. ${FALLBACK}` }, 502);
    return json({ success: true, message: "Got it. We'll check your area and contact you within one business day with availability and pricing." });
  } catch {
    return json({ error: `We couldn't confirm your request was received. ${FALLBACK}` }, 502);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/inquiry") return handleInquiry(request);
    return env.ASSETS.fetch(request);
  },
};
