# HyperGen website

Next.js + Tailwind + Framer Motion + React Three Fiber landing site.

## Run locally

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000. For a production build run `npm run build`.

## Data integrity

- `data/results.json` is intentionally empty until verified benchmark runs exist.
- `public/data/results.json` is the public download copy; update both together from validated results.
- The trace explorer is explicitly **illustrative**, not a real recorded run. Replace it with versioned trace JSON only after validating it.
- The design-partner form opens a prefilled **public GitHub issue**. Users must sign in to GitHub; submitted contact details are public. Replace this with a verified private intake endpoint before production launch. No submissions are stored by this website.
- The hero CTA scrolls to the benchmark section; it does not run models or ask for API keys.
- Three.js scene is dynamically imported on larger, capable devices only; reduced-motion and low-end mobile receive a static fallback.
- No customer logos, fabricated metrics, or testimonials are included.

## Before public launch

1. Replace public GitHub issue intake with a verified private design-partner contact workflow.
2. Generate and publish real results with trace/evaluator provenance.
3. Replace illustrative trace with recorded and reviewed synthetic trace.
4. Run `npm run build`, keyboard/screen reader checks and mobile QA.
5. Measure Lighthouse scores (90+ is a **target**, not a measured result).
6. Review dependency lockfile and pin versions for reproducible deployments.

Inspired by contemporary premium website composition and motion; no Framer assets, source, or branding were copied.
