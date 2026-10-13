# Launch Lead Gen: drainage & irrigation site

A standalone static marketing site for launchleadgen.io. It focuses on exclusive leads for drainage and irrigation contractors. It was split out of the aryosmallbiz repo.

## Build & preview

```sh
python3 src/build.py                     # writes site/
npx wrangler@4 dev                       # serves site/ + the form Worker at http://localhost:8787
```

The build needs no dependencies. Links use clean URLs (`/pricing`, `/blog/...`), which Cloudflare serves from `pricing.html` and similar files, so preview with `wrangler dev` rather than a plain file server. Commit `site/` after every build. CI rebuilds before deploying and warns if the committed copy is stale.

## Deploy (Cloudflare)

`wrangler.jsonc` deploys `site/` plus `worker/index.js` to the Worker named `launchleadgen-site-preview`. Use one of these two options, not both:

1. **Cloudflare Git integration (recommended).** In the Cloudflare dashboard, open Workers & Pages → `launchleadgen-site-preview` → Settings → Builds → Connect. Pick this repo and branch `main`, leave the build command empty, and use the deploy command `npx wrangler deploy`. Every push to `main` then deploys.
2. **GitHub Actions.** Add repository secrets `CLOUDFLARE_API_TOKEN` (a token with "Edit Cloudflare Workers" permission) and `CLOUDFLARE_ACCOUNT_ID`. `.github/workflows/deploy.yml` then deploys on every push to `main`. Without the secrets, the workflow only builds and checks.

To serve launchleadgen.io from this Worker, add the domain under the Worker's Settings → Domains & Routes. Do that only when you're ready to replace the current WordPress site, because the contact form still posts through it (see below).

## Contact form

`/api/inquiry` (in `worker/index.js`) validates the form, rejects cross-site posts and a honeypot field, and forwards each request to the existing WordPress form on launchleadgen.io (Breakdance form 113). Submissions land in the same inbox as today. If the WordPress site goes away, point `UPSTREAM` at a new handler first.

## Structure

| Path | What it is |
|---|---|
| `worker/index.js`, `wrangler.jsonc` | Cloudflare Worker (form endpoint) and deploy config |
| `src/headers.txt` | Security and cache headers, copied to `site/_headers` |
| `src/build.py` | Page templates and copy: home, drainage, irrigation, how it works, pricing, contact, blog, privacy, terms, 404, plus sitemap, robots and favicon. The logo mark is traced in `MARK_LEFT` / `MARK_RIGHT` |
| `src/assets/styles.css` | Brand design system: Navy #102A43, Launch Blue #1268E8, Ice Blue #EAF3FC, Safety Orange #F47721 (calls to action only), Plus Jakarta Sans |
| `src/assets/img/` | Photos cropped from the brand board (low resolution; replace with the original files when available, same names) |
| `src/assets/og.jpg`, `apple-touch-icon.png` | Social share image and touch icon |
| `src/assets/main.js` | Header state, ROI calculator, territory check, form validation, pricing toggle, blog filters, reading progress |
| `src/posts/*.html` | Blog posts: a JSON header comment followed by the article HTML. To publish a post, add a file and rebuild |
| `site/` | Generated output. Don't edit it by hand |

## Before launch: confirm or replace

These are placeholders or assumptions. They are not confirmed business facts:

- **Pricing**: the per-lead starting prices ($89/$79 drainage, $69/$59 irrigation), the plan limits and Territory Lock are proposals.
- **Offer terms**: month-to-month plans, no setup fee, the bad-lead credit policy, delivery in under 60 seconds and going live in about a week.
- **Reviews**: there are no testimonials on the site. Add real, approved client reviews when you have them.
- **Photos**: `crew.jpg` and `foreman.jpg` are upscaled crops from the brand board. Swap in full-resolution originals before launch.
- **Privacy Policy and Terms**: plain-language starting drafts. Have them reviewed before running ads, and update them if you add analytics or ad pixels.
- **Typical job-size ranges** on the home page are broad estimates. They carry a disclaimer.
- **Contact details**: phone (210) 441-6650 and info@launchleadgen.com, taken from the existing preview Worker.
- **Newsletter box**: not connected yet.
- The hero "New lead" card and the sample lead cards are illustrative and labelled as samples.
