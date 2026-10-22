# OptoTACH v1.0 — Hardware Bring-Up & Test Procedure

This guide outlines the staged bench verification procedure for the assembled OptoTACH v1.0 printed circuit board. Following this staged sequence ensures that power-rail faults, component orientation errors, and timing issues are isolated and resolved before all ICs are inserted.

## Required Test Equipment

* Bench DC Power Supply (or 4 × AA 6.0 V battery pack with power lead)
* Digital Multimeter (DMM) with continuity and resistance modes
* 2-Channel Digital Storage Oscilloscope (or logic analyzer)
* Small flathead screwdriver / tweezers for DIP IC socket insertion
* (Optional) Function / Signal Generator capable of producing 10 Hz – 100 Hz 5 V square waves

## Stage 1: Pre-Power Cold Resistance & Continuity Check

Perform these checks with **NO integrated circuits installed in sockets** and **power disconnected**:

1. **Supply Rail Resistance:** Measure DC resistance between the power input terminals `PWR 5-6V` (+ and -).
   * **Expected:** High impedance (> 50 kΩ). If resistance is < 100 Ω, inspect for solder bridges across decoupling capacitors (`C1`–`C14`) or ground pours before applying power.
2. **Reverse Polarity Diode Check:** Probe `D1` with the DMM diode test mode. Confirm forward drop (~0.6 V) and reverse open circuit.
3. **Socket Power Pin Verification:** Check continuity between the board ground terminal and:
   * Pin 7 of DIP-14 socket (`U2`)
   * Pin 8 of DIP-16 sockets (`U7`, `U8`, `U9`, `U10`, `U11`, `U12`, `U13`, `U14`)
   * Pin 1 of DIP-8 sockets (`U4`, `U6`)
   * Pin 2 of DIP-4 optocoupler positions (`U3`, `U5`)

## Stage 2: Power Rail Verification (Unpopulated Sockets)

1. Connect a 5.0 V – 6.0 V DC power supply to the terminal block. Set current limit to 100 mA.
2. Turn on power. Measure voltage at the positive terminal of `C5` (100 µF bulk capacitor).
   * **Expected:** 5.0 V – 6.0 V DC matching supply voltage.
   * **Supply Current:** Current draw with empty sockets should be under 2 mA (primarily bleeder/power indicator LED).
3. Measure VCC at the power pins of all empty IC sockets:
   * Pin 14 of `U2`
   * Pin 16 of `U7`, `U8`, `U9`, `U10`, `U11`, `U12`, `U13`, `U14`
   * Pin 8 and Pin 4 (RESET) of `U4`, `U6`
   * **Expected:** Supply rail within 50 mV of input voltage on every socket.
4. Power down and disconnect power before proceeding.

## Stage 3: Quartz Timebase & Binary Divider Bring-Up

1. **Insert `U9` and `U10` (CD4060BE) into their sockets.** Verify pin 1 orientation facing the notch on the silkscreen.
2. Connect power (6.0 V).
3. Connect an oscilloscope probe (10× mode) to the oscillator test net:
   * **Crystal Oscillator Test:** Probe `U9` pin 9 and pin 10. Confirm 32.768 kHz sinusoidal oscillation. If absent, inspect `Y1` solder joints, `R12` (10 MΩ), `R13` (220 kΩ), and `C12`, `C13` (22 pF).
   * **8 Hz Intermediate Clock:** Probe `U9` pin 1 (output Q12, net `/CLK_8HZ`).
     * **Expected:** Clean 8.0 Hz square wave (50% duty cycle, 0 to 6 V amplitude).
   * **0.5 Hz Half-Second Output:** Probe `U10` pin 7 (output Q4, net `/T_Q4_0.5HZ`).
     * **Expected:** 0.50 Hz square wave (1.0 s HIGH, 1.0 s LOW).
   * **0.25 Hz Gate Base Output:** Probe `U10` pin 5 (output Q5, net `/T_Q5_0.25HZ`).
     * **Expected:** 0.25 Hz square wave (2.0 s HIGH, 2.0 s LOW).
4. Power down.

## Stage 4: Gating Logic & Display Blanking Verification

1. **Insert `U2` (CD4093BE quad Schmitt NAND) into its socket.**
2. Power up. Connect scope channel 1 to `U10` Q4, channel 2 to `U10` Q5, and channel 3 (or probe sequentially) to `/GATE_N` (`U2` pin 3):
   * **Gate Window:** Verify that `/GATE_N` goes LOW for exactly **1.000 second once every 4.000 seconds** (the AND combination of Q4 and Q5).
   * **Display Enable Signal:** Probe net `/DISP_EN` reaching pin 3 of the `CD4026` sockets (`U11`–`U14`).
     * **Expected:** LOW during the 1-second counting window (display blanked), and HIGH for the remaining 3 seconds (display enabled).
   * **Counter Reset Pulse:** Probe net `/RESET` at `C6` (1 µF coupling capacitor).
     * **Expected:** A brief positive-going spike (< 10 ms) at the leading edge of each gate window, zeroing the counters before measurement starts.
3. Power down.

## Stage 5: Display Driver & Counter Chain Bring-Up

1. **Insert `U11`, `U12`, `U13`, and `U14` (CD4026BE counters/decoders) into their sockets.**
2. Set mode switch `SW1` to **Counter Mode (CNT: switch 1 ON, switches 2, 3, 4 OFF)**.
3. Power up.
   * **Initial State:** All four 7-segment displays (`DS1`–`DS4`) should illuminate showing `0 0 0 0`.
   * **Brightness:** All segments should exhibit uniform red illumination across all 4 digits via the onboard 220 Ω current limiting resistor array.
4. **Manual Reset Check:** Press push button `SW2` (`RESET`).
   * The displays should momentarily flicker and reliably hold `0 0 0 0`.
5. **Clocking Test:** Temporarily touch a ground lead through a 10 kΩ resistor to `U11` pin 1 (clock input) to simulate input pulses.
   * Confirm the least-significant digit (`DS1`) increments cleanly: 0 -> 1 -> 2 ... -> 9 -> 0, and carries into `DS2`.
6. Power down.

## Stage 6: Pulse Multiplier Bring-Up (NE555 & CD4017)

1. **Insert `U4`, `U6` (NE555P), `U3`, `U5` (PC817), and `U7`, `U8` (CD4017BE).**
2. Set mode switch `SW1` to **RPM Mode (switch 2 ON, switch 3 ON, switches 1 and 4 OFF)**.
3. Connect oscilloscope channel 1 to `U4` trigger input (optical trigger) and channel 2 to `U6` pin 3 (burst oscillator output, net `/BURST`).
4. Apply a single trigger edge to `U4`:
   * **Oscillator Frequency:** Verify `U6` oscillates at $f \approx 4.8\text{ kHz}$ ($R_8 = 1\text{ k}\Omega, R_9 = 1\text{ k}\Omega, C_3 = 100\text{ nF}$).
   * **Burst Count:** Verify that exactly **60 clock pulses** are emitted per trigger edge before the `CD4017` cascade resets and shuts off `U4`'s latch.
   * **Burst Duration:** The entire 60-pulse burst should complete in approximately **12.5 ms**.

## Stage 7: Optical Sensor & Bench Calibration

1. Ensure Vishay `TCRT5000` is installed with correct lead polarity:
   * IR Emitter: Cathode to square pad.
   * Phototransistor: Collector to ringed pad with pull-up.
2. Aim the sensor at a rotating target (e.g. electric fan or motor shaft) equipped with one strip of white reflective tape against a matte black surface.
3. Maintain a sensing distance of **3 mm to 10 mm**.
4. Observe the 4-digit display:
   * The display should blank for 1 second, then display the stable measured RPM for 3 seconds.
5. **Bench Standard Calibration:**
   * Benchmark the reading against a calibrated commercial tachometer (e.g., Lutron DT-2236).
   * Measured readings should track within $\pm 60\text{ RPM}$ ($\pm 1$ digital count) of the reference instrument.
   * For precision verification, inject a 50.0 Hz square wave directly into the optical trigger input:
     $$\text{Display Readout} = 50.0\text{ Hz} \times 60 = 3,000\text{ RPM}$$

## Troubleshooting Matrix

| Symptom | Probable Cause | Corrective Action |
| :--- | :--- | :--- |
| **Displays remain completely dark** | `D1` reversed, power polarity flipped, or `CD4026` Pin 3 held LOW | Verify 5–6V rail at `C5`; check `U2` Pin 4/Pin 3 output; ensure displays are Common-Cathode |
| **Displays show random rolling numbers** | Gate signal missing or display enable grounded | Check `U2` CD4093 NAND logic; verify `U10` Q4/Q5 divider outputs |
| **Oscillator fails to start (no 8 Hz clock)** | Flux residue across 32.768 kHz crystal or wrong capacitor values | Clean board around `Y1` with isopropanol; verify `C12`, `C13` are 22 pF and `R12` is 10 MΩ |
| **Display reads exactly half at high RPM (>4800 RPM)** | Burst duration collision ($C_3 = 100\text{ nF}$) | Normal theoretical ceiling with 100 nF; install $C_3 = 22\text{ nF}$ to extend ceiling beyond 10,000 RPM |
| **No response to optical marks** | TCRT5000 IR LED reversed or sensing gap too large | Check IR LED emission using a smartphone camera (visible faint purple glow); adjust distance to 3–8 mm |
