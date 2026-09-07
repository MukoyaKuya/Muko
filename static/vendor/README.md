# Vendored browser libraries

Three.js 0.180.0: `three.module.min.js` and its sibling `three.core.min.js`, from
`https://cdn.jsdelivr.net/npm/three@0.180.0/build/`. Keep both files together.
MIT licence: `three.LICENSE.txt`. Used only by the progressively loaded homepage atmosphere.

These minified files are pinned copies of Lucide 1.11.0, HTMX 2.0.0, and GSAP 3.12.2.
They are served from this site so the public page does not depend on third-party script CDNs at runtime.

To update a library, download the exact version from its official release/CDN, review the changelog, update this note, rebuild static assets, and deploy the new manifest.
