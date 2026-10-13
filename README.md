# Launch Lead Gen: drainage & irrigation site

A standalone static marketing site for launchleadgen.io. It focuses on exclusive leads for drainage and irrigation contractors. It was split out of the aryosmallbiz repo.

## Build & preview

```sh
python3 src/build.py              # writes site/
cd site && python3 -m http.server 8787
```

Open http://localhost:8787. The build needs no dependencies. Deploy by uploading `site/` to any static host (Netlify, Vercel, Cloudflare Pages or S3). Links are root-relative, so serve the site at the domain root.

## Structure

| Path | What it is |
|---|---|
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
- **Contact email**: `hello@launchleadgen.io`.
- **Contact form**: it validates in the browser but does not send. To connect it, set `data-endpoint` on the form in `build_contact()` to a form backend that accepts a POST of FormData, such as Formspree or a CRM webhook. The newsletter box isn't connected either.
- The hero "New lead" card and the sample lead cards are illustrative and labelled as samples.
