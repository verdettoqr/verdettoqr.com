# Publishing verdettoqr.com

Static site, built by `build.py` from `logo.svg` and the copy inside the
script; `assets.py` makes the favicons, the Open Graph image, and the hero
screenshot from the icon master and the screen walk in the archive.

## Before the first push

1. In `build.py` set `DRAFT = False` (drops the banner) and `PUBLISH = True`
   (clean URLs in links: `/privacy` instead of `privacy.html`). Set `DATE`
   and the effective dates on the privacy and terms pages. Run
   `python assets.py` then `python build.py`.
2. Roboto ships with the site: `fonts/Roboto-latin.woff2` is the variable
   latin file from Google Fonts (43 KB, every weight, Apache 2.0, license
   in `fonts/LICENSE.txt`), declared by the `@font-face` rule in `build.py`
   and allowed by the content security policy's `font-src 'self'`. Other
   scripts fall back to the system font.
3. Counsel's clearance of the Verdetto mark precedes the push.

## Hosting: GitHub Pages under the verdettoqr account

1. Create the repository `verdettoqr/verdettoqr.com` (public), push this
   folder to `main`.
2. Settings, Pages: source "Deploy from a branch", branch `main`, folder
   `/ (root)`. The `CNAME` file sets the custom domain to `verdettoqr.com`.
3. After DNS resolves (minutes to an hour), tick "Enforce HTTPS".

## GoDaddy DNS (operator does this; the agent never logs in)

Add, leaving every MX and TXT record untouched (they carry the mail):

| Type | Name | Value | TTL |
|---|---|---|---|
| A | @ | 185.199.108.153 | 600 |
| A | @ | 185.199.109.153 | 600 |
| A | @ | 185.199.110.153 | 600 |
| A | @ | 185.199.111.153 | 600 |
| CNAME | www | verdettoqr.github.io | 600 |

Delete GoDaddy's parking `A` record for `@` and any domain-forwarding rule.
The canonical host is the apex, `https://verdettoqr.com`; GitHub redirects
`www` to it once both records exist.

## After it is live

- Google Search Console: add a Domain property for `verdettoqr.com`,
  verify with the DNS TXT record it gives you (add it at GoDaddy), then
  submit `https://verdettoqr.com/sitemap.xml`.
- Bing Webmaster Tools: import the site from Search Console (one click)
  and submit the sitemap there too. Bing's index feeds ChatGPT search,
  Copilot, and DuckDuckGo, so for AI answers it matters as much as Google.
- AI search: `robots.txt` explicitly welcomes GPTBot, OAI-SearchBot,
  ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended, CCBot, and
  Bingbot; `llms.txt` gives models the site in Markdown; every page opens
  with an "In short" answer, and the JSON-LD names the same facts. Keep
  the one-sentence description identical everywhere it appears (site,
  Play listing, GitHub), since consistency across sources is what answer
  engines key on. Check `robots.txt` once a year: crawler names change.
- Play Console: privacy policy URL `https://verdettoqr.com/privacy`,
  website `https://verdettoqr.com`, support email `support@verdettoqr.com`.
- Replace the "Coming soon" label on the home page with Google's official
  Play badge (self-hosted, unmodified, per Google's brand guidelines) and
  the listing link.
- Confirm in a browser that the pages load with no external requests
  (network panel) and that the content security policy reports nothing.
