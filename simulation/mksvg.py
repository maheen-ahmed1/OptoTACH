import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures")

SURFACE = "#fcfcfb"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
MUTED = "#898781"
INK = "#0b0b0b"
INK2 = "#52514e"
S1 = "#2a78d6"
S2 = "#eb6834"
CRIT = "#d03b3b"

W, H = 780, 400
PX0, PX1 = 66, W - 22
XMAX = 6000.0
TICKS = [0, 1000, 2000, 3000, 4000, 5000, 6000]
fmt = lambda v: "{:,}".format(v)


def sx(v):
    return PX0 + (v / XMAX) * (PX1 - PX0)


def build(rows_built, rows_fixed, key, ymax, yticks, ylabfmt, title, sub,
          ytitle, legend, with_ideal):
    py0, py1 = 34, H - 84

    def sy(v):
        return py1 - (min(v, ymax) / ymax) * (py1 - py0)

    def p(rows):
        return "".join("%s%.1f,%.1f" % ("M" if i == 0 else "L",
                                        sx(r["true_rpm"]), sy(r[key]))
                       for i, r in enumerate(rows))

    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
         'viewBox="0 0 %d %d" font-family="system-ui,-apple-system,Segoe UI,sans-serif">'
         % (W, H, W, H)]
    o.append('<rect width="%d" height="%d" rx="8" fill="%s"/>' % (W, H, SURFACE))
    o.append('<text x="22" y="22" font-size="14" font-weight="600" fill="%s">%s</text>'
             % (INK, title))
    o.append('<text x="22" y="%d" font-size="11.5" fill="%s">%s</text>'
             % (H - 8, MUTED, sub))
    for v in TICKS[1:]:
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s"/>'
                 % (sx(v), py0, sx(v), py1, GRID))
    for v in yticks[1:]:
        o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s"/>'
                 % (PX0, sy(v), PX1, sy(v), GRID))
    o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" '
             'stroke-width="1.5" stroke-dasharray="4 3"/>'
             % (sx(4800), py0, sx(4800), py1, CRIT))
    o.append('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="end">'
             '4800 RPM ceiling</text>' % (sx(4800) - 6, py0 + 11, INK2))
    if with_ideal:
        o.append('<path d="M%.1f,%.1f L%.1f,%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.5" stroke-dasharray="5 4"/>'
                 % (sx(0), sy(0), sx(6000), sy(6000), MUTED))
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round"/>' % (p(rows_fixed), S2))
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round"/>' % (p(rows_built), S1))
    o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s"/>'
             % (PX0, py1, PX1, py1, AXIS))
    o.append('<line x1="%d" y1="%d" x2="%d" y2="%.1f" stroke="%s"/>'
             % (PX0, py0, PX0, py1, AXIS))
    for v in TICKS:
        o.append('<text x="%.1f" y="%d" font-size="11" fill="%s" '
                 'text-anchor="middle">%s</text>' % (sx(v), py1 + 18, MUTED, fmt(v)))
    for v in yticks:
        o.append('<text x="%d" y="%.1f" font-size="11" fill="%s" text-anchor="end" '
                 'dominant-baseline="middle">%s</text>'
                 % (PX0 - 9, sy(v), MUTED, ylabfmt(v)))
    o.append('<text x="%.1f" y="%d" font-size="11.5" fill="%s" text-anchor="middle">'
             'true speed (RPM)</text>' % ((PX0 + PX1) / 2.0, py1 + 36, MUTED))
    ymid = (py0 + py1) / 2.0
    o.append('<text x="16" y="%.1f" font-size="11.5" fill="%s" text-anchor="middle" '
             'transform="rotate(-90 16 %.1f)">%s</text>'
             % (ymid, MUTED, ymid, ytitle))
    lx = PX0
    for (col, lab) in legend:
        o.append('<rect x="%d" y="%d" width="14" height="3" rx="1.5" fill="%s"/>'
                 % (lx, py1 + 56, col))
        o.append('<text x="%d" y="%d" font-size="12" fill="%s">%s</text>'
                 % (lx + 20, py1 + 60, INK2, lab))
        lx += 26 + int(len(lab) * 6.4)
    o.append('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    d = json.load(open(os.path.join(HERE, "sweep.json")))
    b, f = d["built"], d["fixed"]

    a = build(b, f, "mean", 6000.0, TICKS, fmt,
              "Displayed reading vs. true speed",
              "Below 4800 RPM both configurations sit on the ideal line. "
              "Above it, the as-built board reads exactly half.",
              "displayed reading",
              [(S1, "As built (C3 = 100 nF)"), (S2, "C3 = 22 nF"),
               (MUTED, "ideal instrument")], True)
    open(os.path.join(OUT, "reading_vs_true.svg"), "w", encoding="utf-8").write(a)

    e = build(b, f, "worst_pct", 55.0, [0, 10, 20, 30, 40, 50],
              lambda v: "%d%%" % v,
              "Worst-case error vs. true speed",
              "Low-speed error is the +/-1 revolution quantisation, identical for "
              "both (the orange trace lies under the blue below 4800 RPM).",
              "worst-case error",
              [(S1, "As built"), (S2, "C3 = 22 nF")], False)
    open(os.path.join(OUT, "error_vs_true.svg"), "w", encoding="utf-8").write(e)
    print("wrote figures/reading_vs_true.svg and figures/error_vs_true.svg")
