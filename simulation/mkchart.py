"""Render the sweep result as a single-file HTML report with two charts.

Template (not .format) because the page is mostly CSS and JS braces.
Placeholders are $UPPERCASE; there is no '$' anywhere in the CSS or JS.
"""
import json
import os
from string import Template

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "sweep.json")))
built, fixed = d["built"], d["fixed"]

W, H, H2 = 760, 360, 250
PX0, PX1 = 60, W - 18
PY0, PY1 = 22, H - 46
PY0b, PY1b = 22, H2 - 46
XMAX, YMAX, EMAX = 6000.0, 6000.0, 55.0

sx = lambda v: PX0 + (v / XMAX) * (PX1 - PX0)
sy = lambda v: PY1 - (v / YMAX) * (PY1 - PY0)
sy2 = lambda v: PY1b - (min(v, EMAX) / EMAX) * (PY1b - PY0b)


def line_path(rows, key, yf):
    return "".join("%s%.1f,%.1f" % ("M" if i == 0 else "L",
                                    sx(r["true_rpm"]), yf(r[key]))
                   for i, r in enumerate(rows))


ticks = [0, 1000, 2000, 3000, 4000, 5000, 6000]
eticks = [0, 10, 20, 30, 40, 50]
fmt = lambda v: "{:,}".format(v)

vals = {
    "W": W, "H": H, "H2": H2, "PX0": PX0, "PX1": PX1,
    "PY0": PY0, "PY1": PY1, "PY0B": PY0b, "PY1B": PY1b,
    "XMAX": int(XMAX),
    "CEILX": "%.1f" % sx(4800),
    "CEILLX": "%.1f" % (sx(4800) - 6),
    "PY0T": PY0 + 10,
    "XMID": "%.1f" % ((PX0 + PX1) / 2.0),
    "YMID": "%.1f" % ((PY0 + PY1) / 2.0),
    "HT": H - 10, "H2T": H2 - 10,
    "GX": "".join('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>'
                  % (sx(v), PY0, sx(v), PY1) for v in ticks[1:]),
    "GY": "".join('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>'
                  % (PX0, sy(v), PX1, sy(v)) for v in ticks[1:]),
    "GX2": "".join('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d"/>'
                   % (sx(v), PY0b, sx(v), PY1b) for v in ticks[1:]),
    "GY2": "".join('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>'
                   % (PX0, sy2(v), PX1, sy2(v)) for v in eticks[1:]),
    "XLAB": "".join('<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
                    % (sx(v), PY1 + 20, fmt(v)) for v in ticks),
    "YLAB": "".join('<text x="%d" y="%.1f" text-anchor="end" '
                    'dominant-baseline="middle">%s</text>'
                    % (PX0 - 10, sy(v), fmt(v)) for v in ticks),
    "XLAB2": "".join('<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
                     % (sx(v), PY1b + 20, fmt(v)) for v in ticks),
    "YLAB2": "".join('<text x="%d" y="%.1f" text-anchor="end" '
                     'dominant-baseline="middle">%d&#37;</text>'
                     % (PX0 - 10, sy2(v), v) for v in eticks),
    "IDEAL": "M%.1f,%.1f L%.1f,%.1f" % (sx(0), sy(0), sx(6000), sy(6000)),
    "PBUILT": line_path(built, "mean", sy),
    "PFIXED": line_path(fixed, "mean", sy),
    "EBUILT": line_path(built, "worst_pct", sy2),
    "EFIXED": line_path(fixed, "worst_pct", sy2),
    "ROWS": "".join(
        "<tr><td>%.0f</td><td>%s</td><td>%s&ndash;%s</td><td>%s&ndash;%s</td>"
        "<td>%.0f&#37;</td></tr>"
        % (b["f"], fmt(int(b["true_rpm"])), fmt(b["lo"]), fmt(b["hi"]),
           fmt(f["lo"]), fmt(f["hi"]), b["lost_pct"])
        for b, f in zip(built, fixed)
        if b["f"] in (1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 75, 78, 80,
                      82, 85, 90, 95, 100)),
    "DATA": json.dumps([{"rpm": b["true_rpm"], "fixed": f["mean"],
                         "blo": b["lo"], "bhi": b["hi"], "lost": b["lost_pct"]}
                        for b, f in zip(built, fixed)]),
}

TPL = Template("""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tachometer sweep</title>
<style>
.viz-root{color-scheme:light;
  --surface-1:#fcfcfb;--plane:#f9f9f7;--text-primary:#0b0b0b;
  --text-secondary:#52514e;--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;
  --border:rgba(11,11,11,.10);--series-1:#2a78d6;--series-2:#eb6834;
  --critical:#d03b3b}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{
  color-scheme:dark;--surface-1:#1a1a19;--plane:#0d0d0d;--text-primary:#fff;
  --text-secondary:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
  --border:rgba(255,255,255,.10);--series-1:#3987e5;--series-2:#d95926;
  --critical:#d03b3b}}
:root[data-theme="dark"] .viz-root{
  color-scheme:dark;--surface-1:#1a1a19;--plane:#0d0d0d;--text-primary:#fff;
  --text-secondary:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
  --border:rgba(255,255,255,.10);--series-1:#3987e5;--series-2:#d95926;
  --critical:#d03b3b}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--text-primary);
  font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
.viz-root{padding-block:26px;padding-left:18px;padding-right:18px;
  max-width:880px;margin:0 auto}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:14px;margin:26px 0 2px}
p.sub{margin:0 0 4px;color:var(--text-secondary);font-size:13px}
p.cap{margin:2px 0 8px;color:var(--muted);font-size:12px}
.tiles{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 6px}
.tile{background:var(--surface-1);border:1px solid var(--border);
  border-radius:8px;padding:10px 14px;min-width:140px;flex:1}
.tile .k{font-size:11px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.05em}
.tile .v{font-size:20px;margin-top:2px}
.tile .v.bad{color:var(--critical)}
figure{margin:0;background:var(--surface-1);border:1px solid var(--border);
  border-radius:8px;padding:10px 8px 6px}
svg{width:100%;height:auto;display:block;overflow:visible}
.grid line{stroke:var(--grid);stroke-width:1}
.axis line{stroke:var(--axis);stroke-width:1}
.tick text{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.line{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.s1{stroke:var(--series-1)}
.s2{stroke:var(--series-2)}
.ideal{fill:none;stroke:var(--muted);stroke-width:1.5;stroke-dasharray:5 4}
.ceil{stroke:var(--critical);stroke-width:1.5;stroke-dasharray:4 3}
.lbl{font-size:11.5px;fill:var(--text-secondary)}
.axtitle{font-size:11.5px;fill:var(--muted)}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:8px 0 2px;
  font-size:12.5px;color:var(--text-secondary);padding-left:6px}
.legend i{width:14px;height:3px;border-radius:2px;display:inline-block;
  vertical-align:middle;margin-right:6px}
table{border-collapse:collapse;width:100%;font-size:12.5px;
  font-variant-numeric:tabular-nums;margin-top:8px}
th,td{border-bottom:1px solid var(--border);padding:5px 8px;text-align:right}
th:first-child,td:first-child{text-align:left}
th{color:var(--muted);font-weight:500}
details{margin-top:18px}
summary{cursor:pointer;color:var(--text-secondary);font-size:13px}
.note{background:var(--surface-1);border:1px solid var(--border);
  border-left:3px solid var(--critical);border-radius:6px;padding:10px 14px;
  margin:16px 0;font-size:13px}
#tip{position:fixed;pointer-events:none;background:var(--surface-1);
  border:1px solid var(--border);border-radius:6px;padding:7px 10px;
  font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.18);opacity:0;
  transition:opacity .08s;font-variant-numeric:tabular-nums;z-index:9}
.tbl-wrap{overflow-x:auto}
</style>
<div class="viz-root">
<h1>Tachometer counting chain &mdash; 1 to 100 Hz sweep</h1>
<p class="sub">Behavioural simulation of the circuit as built: 1.000 s gate from
the 32.768 kHz chain, &divide;60 burst multiplier, NE555 burst clock at
<b>4800 Hz</b> (R8 1k, R9 1k, C3 100nF). 12 input phases &times; 6 gate windows
at every frequency.</p>

<div class="tiles">
<div class="tile"><div class="k">Usable ceiling</div><div class="v">4800 RPM</div></div>
<div class="tile"><div class="k">Quantisation</div><div class="v">&plusmn;60 RPM</div></div>
<div class="tile"><div class="k">Above ceiling</div><div class="v bad">reads half</div></div>
<div class="tile"><div class="k">Timebase error</div><div class="v">&lt;0.005&#37;</div></div>
</div>

<h2>What the display shows vs. actual speed</h2>
<p class="cap">Dashed grey is a perfect instrument. Below 4800 RPM both traces sit on it.</p>
<figure>
<svg viewBox="0 0 $W $H" role="img" aria-label="Displayed reading versus true RPM">
<g class="grid">$GX$GY</g>
<line class="ceil" x1="$CEILX" y1="$PY0" x2="$CEILX" y2="$PY1"/>
<text class="lbl" x="$CEILLX" y="$PY0T" text-anchor="end">4800 RPM ceiling</text>
<path class="ideal" d="$IDEAL"/>
<path class="line s2" d="$PFIXED"/>
<path class="line s1" d="$PBUILT"/>
<g class="axis"><line x1="$PX0" y1="$PY1" x2="$PX1" y2="$PY1"/>
<line x1="$PX0" y1="$PY0" x2="$PX0" y2="$PY1"/></g>
<g class="tick">$XLAB$YLAB</g>
<text class="axtitle" x="$XMID" y="$HT" text-anchor="middle">true speed (RPM)</text>
<text class="axtitle" x="14" y="$YMID" text-anchor="middle"
 transform="rotate(-90 14 $YMID)">displayed reading</text>
</svg>
<div class="legend">
<span><i style="background:var(--series-1)"></i>As built &mdash; C3 = 100 nF</span>
<span><i style="background:var(--series-2)"></i>C3 = 22 nF</span>
<span><i style="background:var(--muted)"></i>ideal instrument</span>
</div>
</figure>

<div class="note"><b>The failure is silent.</b> Past about 4900 RPM every second
revolution arrives while the previous 12.5 ms burst is still running, so the latch
ignores it. Exactly half the revolutions are dropped and the display settles on a
steady, confident <b>half reading</b> &mdash; 6000 RPM shows as 3000. Nothing
flickers or blanks to warn you.</div>

<h2>Worst-case error</h2>
<p class="cap">At low speed both are limited by the same &plusmn;1 revolution
quantisation; only the behaviour at the ceiling differs.</p>
<figure>
<svg viewBox="0 0 $W $H2" role="img" aria-label="Worst-case error versus true RPM">
<g class="grid">$GX2$GY2</g>
<line class="ceil" x1="$CEILX" y1="$PY0B" x2="$CEILX" y2="$PY1B"/>
<path class="line s2" d="$EFIXED"/>
<path class="line s1" d="$EBUILT"/>
<g class="axis"><line x1="$PX0" y1="$PY1B" x2="$PX1" y2="$PY1B"/>
<line x1="$PX0" y1="$PY0B" x2="$PX0" y2="$PY1B"/></g>
<g class="tick">$XLAB2$YLAB2</g>
<text class="axtitle" x="$XMID" y="$H2T" text-anchor="middle">true speed (RPM)</text>
</svg>
<div class="legend">
<span><i style="background:var(--series-1)"></i>As built</span>
<span><i style="background:var(--series-2)"></i>C3 = 22 nF</span>
</div>
</figure>

<details open><summary>Data table</summary>
<div class="tbl-wrap">
<table><thead><tr><th>Input Hz</th><th>True RPM</th><th>Reads (as built)</th>
<th>Reads (22 nF)</th><th>Revs lost</th></tr></thead>
<tbody>$ROWS</tbody></table>
</div></details>
</div>
<div id="tip"></div>
<script>
var DATA = $DATA, SX0 = $PX0, SX1 = $PX1, XMAX = $XMAX, VBW = $W;
var tip = document.getElementById('tip');
document.querySelectorAll('svg').forEach(function (svg) {
  svg.addEventListener('pointermove', function (e) {
    var r = svg.getBoundingClientRect();
    var vx = (e.clientX - r.left) / r.width * VBW;
    if (vx < SX0 || vx > SX1) { tip.style.opacity = 0; return; }
    var rpm = (vx - SX0) / (SX1 - SX0) * XMAX, best = DATA[0];
    DATA.forEach(function (p) {
      if (Math.abs(p.rpm - rpm) < Math.abs(best.rpm - rpm)) best = p;
    });
    var built = best.blo.toLocaleString() +
      (best.bhi !== best.blo ? '\\u2013' + best.bhi.toLocaleString() : '');
    tip.innerHTML = '<b>' + best.rpm.toLocaleString() + ' RPM</b> actual<br>' +
      'as built: ' + built +
      (best.lost > 0 ? ' <span style="color:var(--critical)">' +
        best.lost + '% lost</span>' : '') +
      '<br>C3 = 22 nF: ' + Math.round(best.fixed).toLocaleString();
    tip.style.left = Math.min(e.clientX + 14, window.innerWidth - 200) + 'px';
    tip.style.top = (e.clientY + 14) + 'px';
    tip.style.opacity = 1;
  });
  svg.addEventListener('pointerleave', function () { tip.style.opacity = 0; });
});
</script>
""")

open(os.path.join(HERE, "sweep_report.html"), "w", encoding="utf-8").write(
    TPL.substitute(vals))
print("wrote sweep_report.html")
