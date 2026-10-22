# OptoTACH (tach_v1.0) — accuracy analysis

**Board:** `tach_v1.0` — non-contact optical tachometer, CD4026 variant
**Question asked:** can this board be relied on to read like a shop-bought tachometer?
**Date:** 2026-09-17
**Method:** behavioural simulation of the counting chain, parameters taken from the
project netlist and BOM. Nothing here is assumed — every value is cited to a net or a part.


## 1. Short answer

**No, not as it stands — and no instrument can be guaranteed to 100 %.**

Three things were found. One is a genuine defect, one is a structural limit, and
one is the part a simulation cannot reach.

| # | Finding | Severity |
|---|---|---|
| 1 | Above ~4900 RPM the board reads **exactly half**, steadily, with no warning | **Critical** |
| 2 | Readings quantise to multiples of **60 RPM** (±1 revolution) | Structural |
| 3 | The optical front end has no gain and no threshold adjustment | Highest real-world risk |

Finding 1 is fixable with **one capacitor**. Finding 2 is fixable **mechanically**, by
putting more reflective marks on the shaft. Finding 3 needs a circuit change and is
outside the scope of this simulation.

The timebase — usually the first thing people suspect — is **not** a problem. It
contributes under 0.005 % error.


## 2. How the board actually measures speed

Traced from `tach.net` (exported from the project schematic), not from the article
the design was based on.

### 2.1 Timebase — exact, all-digital

```
Y1 32.768 kHz  ->  U9 (CD4060) Q12   = 8 Hz        [net /CLK_8HZ]
               ->  U10 (CD4060) Q4   = 0.5 Hz      [net /T_Q4_0.5HZ]
               ->  U10 (CD4060) Q5   = 0.25 Hz     [net /T_Q5_0.25HZ]
GATE = Q4 AND Q5  (U2, CD4093)                     [net /GATE_N]
```

Q4 is high for 1 s in every 2; Q5 is high for 2 s in every 4. Both are high for
exactly **1 second once every 4 seconds**. That is the measurement window.

There is **no resistor or capacitor anywhere in the gate path** — it is pure binary
division from the crystal. The only timebase error is the crystal's own.

`C6` (1 µF) couples the gate edge into `/RESET`, which reaches the reset pin of all
four CD4026s, so the counter chain is zeroed at the start of every window.

### 2.2 The ×60 multiplier — also exact

For the display to read RPM directly from a 1-second gate, each revolution must
produce 60 counts. The board does this with a burst generator:

```
sensor pulse  -> U3 (PC817) -> U4 (NE555 as SR latch, /LATCH_Q)
              -> U6 (NE555 astable) gated on          [net /OSC]
              -> Q2 buffer                            [net /BURST]
              -> U7 (CD4017) divide by 10             [net /CO10]
              -> U8 (CD4017), Q6 wired to RESET = divide by 6   [net /DIV6_RST]
              -> U8 Q1 -> /BURST_DONE -> U5 (PC817) -> resets the U4 latch
```

10 × 6 = **60**. The burst is terminated by *counting*, not by timing, so the number
of pulses per revolution is exactly 60 regardless of how fast U6 runs. **The 555's
frequency does not affect the reading** — only how quickly the burst finishes. This
is a genuinely well-built part of the design.

### 2.3 Mode switch

`SW1` is a 4-way DIP. From the netlist:

| Switch | Connects | Selects |
|---|---|---|
| 1 | `/PULSE` → `/CNT_CLK` | **Counter** — free-running, ungated |
| 2 | `/GATE_SEL` → `/GATE` | enables the 1 s gate |
| 3 | `/BURST` → `/GATED_IN` | **RPM** — counts the ×60 burst |
| 4 | `/PULSE` → `/GATED_IN` | **RPS** — counts raw pulses |

So RPM = 2+3, RPS = 2+4, Counter = 1 only — which matches the mode table now on the
silkscreen.

### 2.4 Counter chain

`U14` units → `U13` tens → `U12` hundreds → `U11` thousands, carry-chained, driving
`DS4`…`DS1` right-to-left. Four digits, so the display saturates at 9999.


## 3. What was simulated, and what was not

A SPICE run was **not** used. There are no usable models on this machine for the
CD4026, CD4017, CD4060 or NE555, and more importantly the quantity that decides
accuracy here is *logic timing*, not analogue behaviour.

Instead the counting chain was modelled directly (`sweep.py`):

**Modelled**
- 1.000 s gate opening once every 4 s, derived as in §2.1
- counter reset at the start of each window
- a burst of exactly 60 pulses per revolution at `f_osc`
- the U4 latch: a revolution arriving while a burst is still running is **dropped**,
  because the latch is already set and the new edge does nothing
- partial bursts straddling the gate edges
- 12 different input phases × 6 gate windows at every frequency, so phase-dependent
  behaviour shows up as a min–max range rather than a single number

**Not modelled** — and these matter
- the optical front end (see §6.3)
- component tolerance and drift (see §6.4)
- power supply behaviour, display multiplex loading, contact bounce

`f_osc` is computed from the actual BOM values:

```
R8 = 1 kΩ, R9 = 1 kΩ, C3 = 100 nF          [nets /OSC_DIS, /OSC_TH]
f_osc = 1.44 / ((R8 + 2·R9) · C3)
      = 1.44 / (3000 × 100e-9)  =  4800 Hz
burst duration = 60 / 4800      =  12.5 ms
```


## 4. Results

### 4.1 Displayed reading vs. true speed

![Displayed reading vs true speed](figures/reading_vs_true.svg)

### 4.2 Worst-case error

![Worst-case error vs true speed](figures/error_vs_true.svg)

An interactive version with hover readout is in **`sweep_report.html`** — open it in
a browser and hover either chart.

### 4.3 Data

Ranges are min–max across 12 input phases; a range means the reading is
phase-dependent and will visibly jitter between those values.

| Input Hz | True RPM | As built | C3 = 22 nF | Revs lost |
|---:|---:|:--|:--|---:|
| 1 | 60 | 60–60 | 60–60 | 0.0% |
| 1.5 | 90 | **60–120** | **60–120** | 0.0% |
| 2 | 120 | 120–120 | 120–120 | 0.0% |
| 2.5 | 150 | **120–180** | **120–180** | 0.0% |
| 5 | 300 | 300–300 | 300–300 | 0.0% |
| 10 | 600 | 600–600 | 600–600 | 0.0% |
| 20 | 1,200 | 1,200–1,200 | 1,200–1,200 | 0.0% |
| 30 | 1,800 | 1,800–1,800 | 1,800–1,800 | 0.0% |
| 40 | 2,400 | 2,400–2,400 | 2,400–2,400 | 0.0% |
| 50 | 3,000 | 3,000–3,000 | 3,000–3,000 | 0.0% |
| 60 | 3,600 | 3,600–3,600 | 3,600–3,600 | 0.0% |
| 70 | 4,200 | 4,200–4,200 | 4,200–4,200 | 0.0% |
| 75 | 4,500 | 4,500–4,500 | 4,500–4,500 | 0.0% |
| 78 | 4,680 | 4,680–4,680 | 4,680–4,680 | 0.0% |
| 79 | 4,740 | 4,740–4,740 | 4,740–4,740 | 0.0% |
| 80 | 4,800 | 3,840–4,800 | 4,800–4,800 | 6.0% |
| 81 | 4,860 | **2,401–2,456** | 4,860–4,860 | 50.0% |
| 82 | 4,920 | **2,460–2,460** | 4,920–4,920 | 50.0% |
| 85 | 5,100 | **2,524–2,576** | 5,100–5,100 | 50.0% |
| 90 | 5,400 | **2,700–2,700** | 5,400–5,400 | 50.0% |
| 95 | 5,700 | **2,830–2,870** | 5,700–5,700 | 50.0% |
| 100 | 6,000 | **3,000–3,000** | 6,000–6,000 | 50.0% |

Full 0.5 Hz-resolution data is in `sweep.json`.


## 5. A note on reading this data honestly

The first run of this sweep printed **0.00 % error at every integer frequency**,
which appeared to contradict the ±60 RPM quantisation. It does not.

At an exact integer input frequency, one second contains a whole number of
revolution periods, so the window captures an identical repeating pattern regardless
of phase and the count comes out exact. That is an artefact of sampling the sweep on
integers, **not** a property of the instrument.

Step off the integers — as any real motor does — and the quantisation appears
immediately: 1.5 Hz (90 RPM true) reads either 60 or 120. **Readings always snap to a
multiple of 60 RPM.** Do not read the integer rows as evidence of accuracy.


## 6. Error budget

### 6.1 Timebase — negligible

A 32.768 kHz tuning-fork crystal is typically ±20 ppm at 25 °C. `C4`/`C5` are 22 pF,
giving an effective load of roughly 14–16 pF against a typical 12.5 pF specification,
which pulls the frequency by perhaps another 10–20 ppm. Tuning-fork crystals also
have a parabolic temperature curve of about −0.035 ppm/°C².

Total well under 50 ppm = **0.005 %** — about 0.25 RPM at 5000 RPM. Irrelevant beside
everything else here.

### 6.2 Quantisation — ±60 RPM, structural

A 1-second gate with one mark per revolution can only capture a whole number of
revolutions. That is ±1 revolution = **±60 RPM**:

| True RPM | Error |
|---:|---:|
| 90 | 33 % |
| 300 | 10 % |
| 600 | 5 % |
| 1,200 | 2.5 % |
| 3,000 | 1 % |
| 4,800 | 0.6 % |

No component change improves this. It is set by gate length and marks per revolution.

### 6.3 Optical front end — not simulated, and the biggest real risk

```
R1 = 200 Ω  ->  U1 pin 3   IR LED current ≈ (5 − 1.2)/200 ≈ 19 mA
R2 = 10 kΩ pull-up on the phototransistor collector   [net /SENS_RAW]
             ->  U2 (CD4093) Schmitt inputs 5,6  ->  /PULSE
```

**Good:** the CD4093 is a Schmitt-trigger NAND, so there is real hysteresis and a
clean edge will not chatter.

**Bad:** there is **no amplifier and no threshold adjustment**. Detection is pass/fail
on whether the phototransistor can pull a 10 kΩ pull-up below roughly 1.7 V. That
gives a narrow working window:

- outside roughly 2–5 mm standoff, detection becomes unreliable
- a low-contrast mark (bare or dull shaft) → missed pulses → **under-reads**
- sunlight or IR from fluorescent/LED lighting → false pulses → **over-reads**
- oil or a polished shaft → spurious reflections

A commercial instrument solves this with a gain stage and an adaptive or trimmable
threshold. This board has neither. **In practice this will dominate the error budget
far more than anything in the counting chain.**

### 6.4 Component tolerance on the ceiling

The 4800 RPM ceiling depends on `C3`, a ceramic capacitor with ±10–20 % tolerance
plus temperature and DC-bias coefficients. **The real ceiling on any given board is
somewhere around 4000–6000 RPM**, and it moves with temperature. It must be measured
per board, not assumed.


## 7. Findings

### F1 — Silent half-reading above ~4900 RPM — **critical**

Each revolution starts a 12.5 ms burst. Above 4800 RPM the next revolution arrives
before that burst finishes; the U4 latch is already set, so the edge is ignored and
that revolution is lost entirely.

The simulation shows this settling at **exactly 50 % of revolutions lost**, giving a
**stable, jitter-free half reading**. 6000 RPM displays as 3000. Nothing blanks,
flickers, or otherwise indicates a fault.

This is the worst class of instrument failure: a confident wrong answer inside the
plausible range. A user has no way to detect it from the display.

### F2 — ±60 RPM quantisation — structural

See §6.2. Acceptable above ~3000 RPM (≤1 %), poor below ~600 RPM (≥5 %).

### F3 — No sensor gain or threshold control — highest real-world risk

See §6.3. Not simulated; needs bench testing.


## 8. Recommendations

In order of value.

### R1 — Change C3 from 100 nF to 22 nF

```
f_osc = 1.44 / (3000 × 22e-9) = 21,818 Hz
burst = 60 / 21818            = 2.75 ms
ceiling                        ≈ 21,800 RPM
```

Simulated across the whole 1–100 Hz sweep: **zero revolutions lost, exact readings at
80/85/90/95/100 Hz.** The ceiling moves well clear of the 9999 RPM the four digits can
display, so the silent-half-reading failure is eliminated outright.

This does **not** improve low-speed accuracy — quantisation is unchanged.

*One capacitor. Highest return of anything in this report.*

### R2 — More reflective marks on the shaft

The only way to improve low-speed accuracy. With N marks the display reads N × RPM and
the ceiling divides by N:

| Marks | Quantisation | Display reads | Ceiling (with R1) |
|---:|---:|:--|---:|
| 1 | ±60 RPM | RPM | ~21,800 |
| 2 | ±30 RPM | 2 × RPM | ~10,900 |
| 4 | ±15 RPM | 4 × RPM | ~5,450 |

R1 makes 2 or 4 marks practical; without it, 4 marks would drop the ceiling to
~1200 RPM.

### R3 — Improve the optical front end

Beyond the scope of this analysis, but the honest next step if instrument-grade
behaviour is the goal: a transimpedance or common-emitter gain stage feeding a
comparator with a trimmable threshold, ahead of the existing CD4093.

### R4 — Cheap mitigations, no circuit change

- Use proper retro-reflective tape, not white paint
- Shroud the sensor from ambient light
- Fix the standoff distance with a jig rather than holding it by hand


## 9. How to verify on the bench

Simulation cannot prove your board works. This can:

1. **Bypass the sensor.** Inject a known square wave (signal generator, or any MCU) at
   the `/PULSE` node. 50 Hz must read 3000 RPM. This isolates counting error from
   sensor error; the counting chain should be near-perfect.
2. **Sweep 5 → 100 Hz** and tabulate reading against input. Compare with §4.3. Any
   deviation beyond ±60 RPM below the ceiling indicates a real fault.
3. **Find your board's actual ceiling.** Walk up in 1 Hz steps around 75–85 Hz and note
   where the reading halves. C3's tolerance means this differs per board.
4. **Then test the sensor separately** against a known-speed source. That is where the
   error you actually care about lives.


## 10. Honest comparison

A handheld optical tachometer is typically specified **±(0.05 % + 1 digit)** over
roughly 2.5–99,999 RPM, updating about once per second.

This board as built:

| | This board | Commercial |
|---|---|---|
| Accuracy | ±60 RPM (1–33 %) | ±0.05 % + 1 digit |
| Range | 60–4,800 RPM | 2.5–99,999 RPM |
| Update rate | every 4 s | ~1 s |
| Above range | **reads half, silently** | out-of-range indication |

With **R1 + 2–4 marks**, it lands at roughly ±15–30 RPM across a useful range — a
genuinely decent instrument for motor and fan work, though the 4-second update and
the sensor front end remain real differences.


## 11. Files

All paths relative to this folder (`tach_v1.0/analysis/`).

| File | What it is |
|---|---|
| `TACHOMETER_ACCURACY_REPORT.md` | this report |
| `sweep_report.html` | interactive charts with hover readout |
| `figures/reading_vs_true.svg` | figure 4.1 |
| `figures/error_vs_true.svg` | figure 4.2 |
| `sweep.py` | the simulation — circuit model and sweep |
| `mksvg.py` | renders the standalone SVG figures |
| `mkchart.py` | renders the interactive HTML report |
| `netq.py` | netlist query helper used to trace the circuit |
| `sweep.json` | raw results, 0.5 Hz resolution |
| `tach.net` | the netlist everything was derived from |

### Reproducing

Run with KiCad's bundled Python (it has the `pcbnew` module; plain Python works for
these particular scripts since they only need the stdlib):

```bash
# Navigate to the analysis directory
cd analysis

# Run behavioural model sweep and chart generators
python sweep.py     # writes sweep.json
python mksvg.py     # writes figures/
python mkchart.py   # writes sweep_report.html
```

To re-export the netlist after a schematic change:

```bash
kicad-cli sch export netlist --format kicadsexpr --output analysis/tach.net tach_v1.0.kicad_sch
```

To query it — for example, everything SW1 touches:

```bash
python netq.py tach.net SW1
```

### Changing the model

The parameters that matter are at the top of `sweep.py`:

```python
R8 = 1000.0        # NE555 astable, VCC -> DISCH
R9 = 1000.0        # DISCH -> THRES/TRIG
C3 = 100e-9        # timing capacitor  <- change to 22e-9 for R1
BURST_N  = 60      # CD4017 /10 x CD4017 /6
GATE_LEN = 1.0     # seconds, from the CD4060 chain
```


## 12. Caveats

- This is a **behavioural model**, not SPICE. It captures logic timing exactly and
  analogue behaviour not at all.
- Component values are nominal. §6.4 covers the tolerance consequence.
- The optical front end is **not modelled**, and it is likely the dominant real-world
  error source.
- The model assumes a clean single pulse per mark. Real sensor output with marginal
  contrast may produce multiple edges per mark; the CD4093 hysteresis helps but does
  not guarantee it.
- Findings F1 and F2 follow from the netlist and are firm. F3 is an engineering
  judgement from the topology and needs bench confirmation.
