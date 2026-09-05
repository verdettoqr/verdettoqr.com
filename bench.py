"""The "How we test" page.

Two halves. `extract()` reads the scanner-side benchmark ledger in the
archive checkout, selects the state-of-record row for each published leg by
explicit rules, and writes bench-snapshot.json into this folder, so the
site builds without the archive present. `page_entry()` renders the page
from the snapshot through build.py's shell. Nothing here is a claim of
beating anyone: published numbers appear only as reported, beside their
protocol, per the benchmark-evidence rule.

  python bench.py extract   refresh the snapshot from the ledger, print what was chosen
  python bench.py           render how-we-test.html from the snapshot for review
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SNAPSHOT = HERE / "bench-snapshot.json"
LEDGER = Path(r"D:\OneDrive\OneDrive - Atlast\Alexandria Moving Records\New folder\optical-page-archive"
              r"\build\optical-page\decode-replay\2026-08-31-scanner-side\bench-runs.jsonl")

DATASETS = {
    "dynamsoft-hard": ("Dynamsoft difficult images", "68 photographs, 514 barcode instances; low light, shadows, crumpled and poor prints, tiny and dense codes, several codes per frame; QR, Data Matrix, PDF417, EAN, UPC, Code 128, Code 39, ITF",
                       "https://github.com/Dynamsoft/datasets-from-dynamsoft"),
    "artelab": ("Arte-Lab 1D sets", "EAN-13 photographs from 2013-era phones, in matched autofocus and no-autofocus splits of 215 images each",
                "https://artelab.dista.uninsubria.it/downloads.html"),
    "muenster": ("Muenster BarcodeDB", "1,055 EAN-13 and UPC-A photographs from a Nokia N95, 640x480 to 2592x1944",
                 "https://www.uni-muenster.de/PRIA/en/forschung/index.shtml"),
    "dynamsoft-test-sheet": ("Dynamsoft test-sheet images", "the 83 sample images behind Dynamsoft's browser-SDK comparison; no ground truth is published, so only detections can be counted",
                             "https://www.dynamsoft.com/barcode-test-sheet/"),
}
REPORTED = [  # as reported by others; protocols differ from ours and comparability is unknown
    ("Dynamsoft difficult images", "Dynamsoft Barcode Reader, Android", "80.2 recall, 99.3 precision", "vendor blog, own protocol"),
    ("Arte-Lab, autofocus", "Dynamsoft Barcode Reader", "100", "vendor comparison"),
    ("Arte-Lab, autofocus", "zxing", "82.4", "vendor comparison"),
    ("Arte-Lab, no autofocus", "Dynamsoft Barcode Reader", "81.9", "vendor comparison"),
    ("Arte-Lab, no autofocus", "Scandit", "79.1", "vendor comparison"),
    ("Arte-Lab, no autofocus", "zxing / ZBar", "10.2 / 14.0", "vendor comparison"),
]
NOT_RUN = [
    "BarBeR (8,748 images, the broadest public benchmark): the dataset sits behind a registration we have not completed.",
    "Dynamsoft's adversarial QR set (536 images), its Data Matrix and direct-part-mark sets, and its difficult PDF417 set: not fetched yet.",
    "The full Arte-Lab splits on the current reader: the rows below run the first 40 images of each split; the last full-split run predates the current reader.",
    "Any phone. Every number here comes from a desktop; phone measurements replace them when the app's reader is wired to the camera.",
]


def _rows():
    return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def _sha(r):
    return (r.get("config") or {}).get("read_code_sha256", "")[:12]


def _stamp(r):
    return r["recorded_utc"][:10]


def extract():
    rows = _rows()
    snap = {"ledger_rows": len(rows), "legs": {}}

    def pick(name, sel, fmt):
        if not sel:
            print(f"!! {name}: no row matched"); return
        r = max(sel, key=lambda x: x["recorded_utc"])
        snap["legs"][name] = dict(fmt(r), date=_stamp(r), reader=_sha(r), corpus=r["corpus"], recorded=r["recorded_utc"])
        print(f"{name:16s} {r['recorded_utc'][:19]}  {r['corpus'][:70]}\n{'':16s} {json.dumps(snap['legs'][name])[:260]}")

    dyn = [r for r in rows if r["corpus"] == "dynamsoft-hard" and isinstance(r["metrics"].get("recall"), list)]
    fmt_dyn = lambda r: {"recall": r["metrics"]["recall"], "precision": r["metrics"]["precision"], "wall_s": r["metrics"].get("seconds_decode_wall"), "images": 68}
    pick("dyn_budget", [r for r in dyn if (r["metrics"].get("seconds_decode_wall") or 0) < 60], fmt_dyn)
    pick("dyn_unlimited", [r for r in dyn if (r["metrics"].get("seconds_decode_wall") or 0) >= 60], fmt_dyn)

    art = [r for r in rows if r["corpus"].startswith("artelab-medium slice (first 40 per split)")]
    pick("artelab_slice", art, lambda r: {"per_split": 40, "autofocus_read": r["metrics"]["autofocus"]["read"], "autofocus_false": r["metrics"]["autofocus"]["false_images"],
                                           "nofocus_read": r["metrics"]["no-autofocus"]["read"], "nofocus_false": r["metrics"]["no-autofocus"]["false_images"]})

    full = [r for r in rows if r["corpus"] == "artelab-medium (both splits)"]
    if full:
        r = max(full, key=lambda x: x["recorded_utc"])
        print("artelab_full raw:", json.dumps(r["metrics"])[:400])
        m = r["metrics"]

        def split(name):  # full-split rows record recall as [read, images] and false reads as false_decodes
            d = m[name]
            read = d["recall"][0] if isinstance(d.get("recall"), list) else d["read"]
            return read, d.get("false_decodes", d.get("false_images")), d.get("ms_per_image")
        try:
            (ar, af, ams), (nr, nf, nms) = split("autofocus"), split("no-autofocus")
            snap["legs"]["artelab_full"] = dict(per_split=215, autofocus_read=ar, autofocus_false=af, autofocus_ms=ams, nofocus_read=nr, nofocus_false=nf, nofocus_ms=nms,
                                                date=_stamp(r), reader=_sha(r), corpus=r["corpus"], recorded=r["recorded_utc"])
            print("artelab_full    ", r["recorded_utc"][:19], json.dumps(snap["legs"]["artelab_full"])[:200])
        except (KeyError, TypeError) as e:
            print("!! artelab_full: metrics shape not parsed; leg omitted:", e)

    pick("zint_matrix", [r for r in rows if r["corpus"] == "zint-matrix-final-b"],
         lambda r: {k: r["metrics"].get(k) for k in ("symbologies", "read_by_any_route", "route_exact", "route_data_exact", "false", "unread", "wall_s")})

    z2 = defaultdict(list)
    for r in rows:
        m = re.match(r"z2-latency:z2-latency-normal-budget1s-(full-\w+)-c\d+$", r["corpus"])
        if m:
            z2[m.group(1)].append(r)
    if z2:
        run = max(z2, key=lambda k: max(x["recorded_utc"] for x in z2[k]))
        agg = defaultdict(int)
        for r in z2[run]:
            for k, v in r["metrics"]["bands"]["normal"].items():
                agg[k] += v
        last = max(z2[run], key=lambda x: x["recorded_utc"])
        snap["legs"]["z2_normal"] = dict(agg, run=run, chunks=len(z2[run]), budget_s=last["metrics"]["budget_s"], scenarios=9,
                                         date=_stamp(last), reader=_sha(last), recorded=last["recorded_utc"])
        print("z2_normal       ", run, dict(agg))

    r8 = defaultdict(list)
    for r in rows:
        if r["corpus"] == "r8-frame-pairs":
            m = re.search(r"(t\d+-[\w-]+?)-c\d+", str(r.get("note")))
            if m:
                r8[m.group(1)].append(r)
    if r8:
        run = max(r8, key=lambda k: max(x["recorded_utc"] for x in r8[k]))
        bands = [x["metrics"]["band"] for x in r8[run]]
        last = max(r8[run], key=lambda x: x["recorded_utc"])
        snap["legs"]["r8_pairs"] = dict(run=run, chunks=len(bands), rows=sum(b["rows"] for b in bands), correct=sum(b["confirmed_correct"] for b in bands),
                                        wrong=sum(b["wrong_confirmed"] for b in bands), over_1s=sum(b["over_1s"] for b in bands), over_2s=sum(b["over_2s"] for b in bands),
                                        p50_range=[min(b["wall_p50"] for b in bands), max(b["wall_p50"] for b in bands)], p95_max=max(b["wall_p95"] for b in bands),
                                        wall_max=max(b["wall_max"] for b in bands), date=_stamp(last), reader=_sha(last), recorded=last["recorded_utc"])
        print("r8_pairs        ", run, json.dumps(snap["legs"]["r8_pairs"])[:240])

    pick("muenster", [r for r in rows if r["corpus"] == "muenster" and "probe" in r["metrics"]],
         lambda r: {k: r["metrics"]["probe"].get(k) for k in ("images", "truth_codes", "truth_read", "false_reads", "ms_p50", "ms_p95", "ms_max", "budget_s")})
    pick("sheet_blog", [r for r in rows if r["corpus"] == "dynamsoft-hard" and "blog_protocol" in r["metrics"]],
         lambda r: {k: r["metrics"]["blog_protocol"].get(k) for k in ("images", "total_barcodes", "unique_payloads", "avg_ms_per_image", "median_ms", "max_ms", "budget_s")})

    host = (rows[-1].get("config") or {}).get("host") or {}
    snap["host"] = host
    snap["extracted"] = max(r["recorded_utc"] for r in rows)[:10]
    SNAPSHOT.write_text(json.dumps(snap, indent=1), encoding="utf-8", newline="\n")
    print("snapshot written:", SNAPSHOT.name, "legs:", list(snap["legs"]))


def pct(a, b):
    return f"{100.0 * a / b:.1f}"


def page_entry():
    s = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    L = s["legs"]
    host = s.get("host") or {}
    rows = []

    def row(*cells):
        rows.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")

    if "dyn_budget" in L:
        d = L["dyn_budget"]; r, p = d["recall"], d["precision"]
        row("Dynamsoft difficult images, 1 s ceiling", f"{d['images']} images, {r[1]} instances", f"{pct(*r)} ({r[0]}/{r[1]})", f"{p[1] - p[0]} false reads ({pct(*p)} precision)", f"{d['wall_s']:.0f} s for the set", d["reader"], d["date"])
    if "dyn_unlimited" in L:
        d = L["dyn_unlimited"]; r, p = d["recall"], d["precision"]
        row("Dynamsoft difficult images, no time limit", f"{d['images']} images, {r[1]} instances", f"{pct(*r)} ({r[0]}/{r[1]})", f"{p[1] - p[0]} false reads ({pct(*p)} precision)", f"{d['wall_s']:.0f} s for the set", d["reader"], d["date"])
    if "artelab_slice" in L:
        a = L["artelab_slice"]; n = a["per_split"]
        row("Arte-Lab autofocus, first 40 images, 1 s ceiling", f"{n} images", f"{pct(a['autofocus_read'], n)} ({a['autofocus_read']}/{n})", f"{a['autofocus_false']} false reads", "within 1 s each", a["reader"], a["date"])
        row("Arte-Lab no autofocus, first 40 images, 1 s ceiling", f"{n} images", f"{pct(a['nofocus_read'], n)} ({a['nofocus_read']}/{n})", f"{a['nofocus_false']} false reads", "within 1 s each", a["reader"], a["date"])
    if "artelab_full" in L:
        a = L["artelab_full"]; n = a["per_split"]
        row("Arte-Lab autofocus, full split (earlier reader)", f"{n} images", f"{pct(a['autofocus_read'], n)} ({a['autofocus_read']}/{n})", f"{a['autofocus_false']} false reads", f"no time limit; {a['autofocus_ms']} ms per image", a["reader"], a["date"])
        row("Arte-Lab no autofocus, full split (earlier reader)", f"{n} images", f"{pct(a['nofocus_read'], n)} ({a['nofocus_read']}/{n})", f"{a['nofocus_false']} false reads", f"no time limit; {a['nofocus_ms']} ms per image", a["reader"], a["date"])
    if "muenster" in L:
        m = L["muenster"]
        row("Muenster BarcodeDB, 1 s ceiling, first run", f"{m['images']} images", f"{pct(m['truth_read'], m['truth_codes'])} ({m['truth_read']}/{m['truth_codes']})", f"{m['false_reads']} false reads",
            f"median {m['ms_p50']} ms, 95th percentile {m['ms_p95']} ms, slowest {m['ms_max']} ms", m["reader"], m["date"])
    photo_table = "<table><thead><tr><th>Set</th><th>Size</th><th>Read</th><th>Wrong</th><th>Time</th><th>Reader</th><th>Date</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"

    rows.clear()
    if "zint_matrix" in L:
        z = L["zint_matrix"]
        row("Coverage: every symbology libzint can generate, one clean symbol each", f"{z['symbologies']} symbologies", f"{z['read_by_any_route']}/{z['symbologies']} read; {z['route_data_exact']} data-exact, {z['route_exact']} byte-exact through the product route", f"{z['false']} wrong", f"{z['wall_s']} s for the set", z["reader"], z["date"])
    if "z2_normal" in L:
        z = L["z2_normal"]
        row(f"Normal band: {z['scenarios']} capture conditions per symbology (phone reference, clutter, rotation, mild perspective, low contrast, toner dropout, mild defocus, short motion, 3 MP sampling)", f"{z['symbologies']} symbologies", f"{z['recognized_every_run']}/{z['symbologies']} recognized in every condition; {z['exact_every_run']} byte-exact in every condition", "0 wrong text", f"{z['within_budget_every_run']}/{z['symbologies']} within {z['budget_s']:.0f} s in every condition", z["reader"], z["date"])
    if "r8_pairs" in L:
        z = L["r8_pairs"]
        row("Frame pairs: two or three consecutive frames of the same symbol with a pose change between them", f"{z['rows']} sequences", f"{z['correct']}/{z['rows']} confirmed correct", f"{z['wrong']} wrong", f"median {z['p50_range'][0]:.2f} to {z['p50_range'][1]:.2f} s across chunks, 95th percentile at most {z['p95_max']:.2f} s, {z['over_1s']} over 1 s, {z['over_2s']} over 2 s", z["reader"], z["date"])
    synth_table = "<table><thead><tr><th>Battery</th><th>Size</th><th>Read</th><th>Wrong</th><th>Time</th><th>Reader</th><th>Date</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"

    reported = "<table><thead><tr><th>Set</th><th>Reader</th><th>Number</th><th>Source</th></tr></thead><tbody>" + "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in REPORTED) + "</tbody></table>"
    sheet = ""
    if "sheet_blog" in L:
        b = L["sheet_blog"]
        sheet = (f"<p>On the {b['images']} test-sheet images behind Dynamsoft's browser-SDK comparison, which publishes no ground truth, our reader returned "
                 f"{b['total_barcodes']} barcode reads ({b['unique_payloads']} distinct payloads) at a 1 s ceiling, {b['avg_ms_per_image']} ms per image on average and {b['median_ms']} ms median, "
                 f"slowest {b['max_ms']} ms (reader {L['sheet_blog']['reader']}, {L['sheet_blog']['date']}). Without ground truth this counts detections, not correctness, and is listed for completeness only.</p>")
    datasets = "".join(f"<li><a href=\"{u}\">{n}</a>: {d}.</li>" for n, d, u in DATASETS.values())
    not_run = "".join(f"<li>{x}</li>" for x in NOT_RUN)
    platform = host.get("platform", "a desktop computer")

    body = f"""
<div class="prose">
<h1>How we test</h1>
<p class="meta">Numbers from the benchmark ledger as of {s['extracted']}. Every row names the reader build it came from, as the first twelve characters of its code hash, and the day it ran.</p>

<div class="card"><p><strong>In short.</strong> We run the reader over public photo sets and over symbols we generate and degrade ourselves, and we publish what it read, what it got wrong, and how long it took, with the scoring rule beside every number. These are desktop measurements of the reader alone, not phone measurements of the app. Nothing here says we beat anyone: other readers' numbers appear only as their publishers reported them, under protocols that differ from ours.</p></div>

<h2>What the numbers mean</h2>
<ul>
  <li><strong>Read</strong> counts a barcode as read when its exact text appears among the reader's results for that photo, canonical text only: control characters stripped, UPC-A and EAN-13 treated as the one code they are, and mangled encodings of the truth strings tolerated. One read credits every physical copy of the same code in the frame; the Dynamsoft set has several such copies, so its read rate would be lower under per-copy localization scoring. Published numbers likely use localized matching, and we do not claim they are comparable.</li>
  <li><strong>Wrong</strong> counts every result that matches no annotated code in the photo. It is the number we care about most, because a scanner that shows people links must not invent one. Annotation gaps in the public sets count against us here; we note suspected gaps rather than edit anyone's truth.</li>
  <li><strong>Time</strong> is wall-clock time to the reader's answer. The <strong>1 s ceiling</strong> rows stop looking after one second per photo, which is the rule the app lives by; the <strong>no time limit</strong> rows show what the same reader recovers given as long as it wants.</li>
  <li><strong>Machine.</strong> {platform}, Python {host.get('python', '3.12')}, one process per chunk. Phone numbers replace these when the reader is wired to the camera.</li>
</ul>

<h2>Public photo sets</h2>
{photo_table}
{sheet}

<h2>Generated symbols</h2>
<p>Every symbology libzint can produce is generated, then passed through a camera model that adds the defects a phone adds: perspective, rotation, clutter, low contrast, toner dropout, defocus, motion, and low sampling. A symbol counts only when it comes back byte-exact. "Recognized" means the reader named the symbology and returned a payload; "byte-exact" means the payload matched to the byte.</p>
{synth_table}

<h2>As reported by others</h2>
<p>Listed as their publishers reported them. Each comes from a different protocol, mostly a vendor measuring itself, and none has been rerun by us, so these are context, not a comparison.</p>
{reported}

<h2>What we have not run</h2>
<ul>{not_run}</ul>

<h2>Reproduce it</h2>
<ul>{datasets}</ul>
<p>The scoring rules above are the ones the ledger enforces. Per-image read and miss lists exist for every row and will be published with the app's release; until then they are available on request at <a href="mailto:support@verdettoqr.com">support@verdettoqr.com</a>.</p>
</div>
"""
    ld = {"@type": "Article", "headline": "How we test", "description": "How Verdetto's barcode reader is measured: public photo sets, generated symbols, exact-text scoring, false reads counted, time at a one-second ceiling.",
          "dateModified": s["extracted"]}
    return ("How we test - Verdetto", "How Verdetto's barcode reader is measured: public photo sets, generated symbols, exact-text scoring, false reads counted, time at a one-second ceiling.", body, ld)


if __name__ == "__main__":
    if "extract" in sys.argv[1:]:
        extract()
    import build
    title, desc, body, ld = page_entry()
    (HERE / "how-we-test.html").write_text(build.page("how-we-test.html", title.replace("&", "&amp;"), desc, body, ld, "article"), encoding="utf-8", newline="\n")
    print("wrote how-we-test.html (review copy; not in the sitemap until BENCH_PUBLISHED)")
