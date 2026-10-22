import json
import os
import sys

R8 = 1000.0
R9 = 1000.0
C3 = 100e-9
F_OSC = 1.44 / ((R8 + 2 * R9) * C3)
BURST_N = 60
GATE_LEN = 1.0
GATE_PERIOD = 4.0
DIGITS = 10000


def burst_edges(pulses, f_osc):
    out, lost, busy_until = [], 0, -1.0
    dt = 1.0 / f_osc
    for tp in pulses:
        if tp < busy_until:
            lost += 1
            continue
        for i in range(1, BURST_N + 1):
            out.append(tp + i * dt)
        busy_until = tp + BURST_N * dt
    return out, lost


def run(f, mode, phase, f_osc, windows=6):
    total = GATE_PERIOD * (windows + 1)
    T = 1.0 / f
    n = int((total - phase) / T) + 1
    pulses = [phase + k * T for k in range(max(n, 0))]
    pulses = [t for t in pulses if t <= total]

    if mode == "RPM":
        edges, lost = burst_edges(pulses, f_osc)
    else:
        edges, lost = pulses, 0

    readings = []
    for w in range(1, windows + 1):
        g0 = GATE_PERIOD * w + 3.0
        g1 = g0 + GATE_LEN
        c = 0
        for t in edges:
            if g0 <= t < g1:
                c += 1
            elif t >= g1:
                break
        readings.append(c % DIGITS)
    return readings, lost, len(pulses)


def sweep(f_osc, mode="RPM", phases=12):
    rows = []
    freqs = [x / 2.0 for x in range(2, 201)]
    for f in freqs:
        true_rpm = f * 60.0
        allr, lost_tot, pulse_tot = [], 0, 0
        for p in range(phases):
            phase = (p / float(phases)) * (1.0 / f)
            r, lost, npul = run(f, mode, phase, f_osc)
            allr.extend(r)
            lost_tot += lost
            pulse_tot += npul
        lo, hi = min(allr), max(allr)
        mean = sum(allr) / float(len(allr))
        rows.append({
            "f": f, "true_rpm": true_rpm,
            "lo": lo, "hi": hi, "mean": round(mean, 1),
            "err_lo": round(lo - true_rpm, 1),
            "err_hi": round(hi - true_rpm, 1),
            "worst_pct": round(100.0 * max(abs(lo - true_rpm),
                                           abs(hi - true_rpm)) / true_rpm, 2),
            "lost_pct": round(100.0 * lost_tot / max(pulse_tot, 1), 1),
        })
    return rows


if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    print("f_osc as built = %.0f Hz   burst = %.2f ms   collision ceiling = %.0f RPM"
          % (F_OSC, 1000 * BURST_N / F_OSC, F_OSC))
    built = sweep(F_OSC, "RPM")
    fixed = sweep(1.44 / ((R8 + 2 * R9) * 22e-9), "RPM")
    rps = sweep(F_OSC, "RPS")
    json.dump({"built": built, "fixed": fixed, "rps": rps,
               "f_osc_built": F_OSC,
               "f_osc_fixed": 1.44 / ((R8 + 2 * R9) * 22e-9)},
              open(os.path.join(out, "sweep.json"), "w"), indent=1)

    print("\n  Hz   true RPM   reading lo..hi     worst err   rev lost")
    for r in built:
        if r["f"] in (1, 5, 10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 100):
            print("  %5.1f  %7.0f   %5d..%-5d  %8.2f%%   %5.1f%%"
                  % (r["f"], r["true_rpm"], r["lo"], r["hi"],
                     r["worst_pct"], r["lost_pct"]))
