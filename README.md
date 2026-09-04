# verdettoqr.com

The website for Verdetto: QR & Barcode Scanner, the Android app.
Static pages, no scripts, nothing loaded from another host.

- `build.py` writes the pages from the copy inside it, `logo.svg`, and the
  shared stylesheet; `assets.py` makes the favicons, the share image, and
  the hero screenshot. Run `python assets.py` then `python build.py`.
- `PUBLISH.md` is the hosting and DNS checklist.
- `fonts/` holds Roboto (Apache 2.0, license included).

Served by GitHub Pages at https://verdettoqr.com.
