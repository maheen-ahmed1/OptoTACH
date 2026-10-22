# tach_v1.0 — parts to buy

> **Current buying list is `tach_v1.0_purchase.csv`** (2026-09-22), built from the
> builder's inventory and grouped by shop. This file is kept for the background notes
> below — why each part matters, pinouts, the C3 experiment — not for quantities.

Board: order the bare PCB only (100 × 100 mm, 2 layers, all through-hole).
Upload `fab/tach_v1.0_gerbers_jlcpcb.zip`.

## Buy from LCSC (accuracy / fake-prone parts)

| Qty | Part | Why LCSC | Suggested item |
|----|------|----------|----------------|
| 2 | 32.768 kHz crystal (3×8 mm cylinder) | Sets the 1-second count window — the only part that sets reading accuracy. 1 spare. | YXC C52082 |
| 2 | CD4060BE (DIP-16) | Clones often fail to start the 32 kHz oscillator | HGSEMI C507159 or TI C5198 |
| 4 | CD4026BE (DIP-16) | Drives the displays; fakes are weak | TI C89909 |
| 2 | PC817 (DIP-4) | Fakes have low output; may not trigger the 555 | Any Sharp/Everlight **DIP-4** listing (C66405 is SMD — not that one) |
| 1 | TCRT5000 | Fakes have a weak IR LED = short sensing range | Vishay C2984661 |
| 2 | 10M, 2 × 220K resistors, 4 × 22pF caps | Crystal oscillator parts; pennies, and a bad one stops it starting | any through-hole |

Shipping costs more than the parts: order the PCB at JLCPCB and combine it with the
LCSC order into one shipment (LCSC support can merge them).

## Buy locally (fakes work fine here)

**ICs** (get DIP sockets for all of them — lets you swap a bad chip without desoldering)

| Qty | Part | Socket |
|----|------|--------|
| 2 | NE555 | DIP-8 |
| 2 | CD4017 | DIP-16 |
| 1 | CD4093 | DIP-14 |
| — | (CD4026 ×4, CD4060 ×2 from LCSC) | DIP-16 ×6 |
| — | (PC817 ×2 from LCSC) | DIP-4 — see below |

**DIP socket count, measured off the board.** 13 ICs, four sizes:

| Socket | Need | Buy | Goes to |
|----|----|----|---------|
| DIP-16 | 8 | **10** | U7, U8 (CD4017), U9, U10 (CD4060), U11-U14 (CD4026) |
| DIP-8 | 2 | **5** | U4, U6 (NE555) — plus 2 to cut down for the PC817s, 1 spare |
| DIP-14 | 1 | **2** | U2 (CD4093) |
| DIP-4 | 2 | 0 | U3, U5 (PC817) — cut from DIP-8, see below |

**Don't hunt for DIP-4 sockets.** They are rarely stocked, and you don't need them: the
PC817 pads on this board are 7.62 mm between rows, the same as a DIP-8 socket, at
2.54 mm pitch. Take a DIP-8 socket, cut two positions off each side with side cutters,
and it drops straight in. That is why the DIP-8 buy quantity is 5, not 2.

Sockets matter most on exactly the parts the LCSC list flags as fake-prone: the CD4026s,
the CD4060s and the PC817s. Being able to swap a suspect chip without desoldering a
16-pin part is worth the few taka.

**Displays (optional).** DS1-DS4 have 5 pins per side with 15.24 mm between rows, which
is not a stock socket size. If you want them swappable, use machined SIP socket strip cut
into 5-pin lengths — two per display, eight pieces total. Otherwise solder them directly;
7-segment displays rarely fail.

**Displays and controls**

| Qty | Part |
|----|------|
| 4 | 0.56" 7-segment display, **common cathode**, red |
| 1 | DIP switch, 4 position |
| 1 | Tactile push button, 6 mm |
| 1 | LED 5 mm (any colour) |
| 1 | 2-pin male header, 2.54 mm (power in, 5–6 V) |

**Semiconductors**

| Qty | Part |
|----|------|
| 2 | NPN switching transistor, **TO-92 plastic** — see note below |
| 3 | 1N4148 |

**Transistor (Q1, Q2) — buy the TO-92 plastic one:**

- **RoboticsBD sells TO-92 plastic** (৳4) — this fits the board.
- **TechShopBD's listing specifies the TO-18 metal can** — that has its 3 leads in a
  triangle, so it will not drop into the 3-in-a-row holes without bending them.
  Ask to see the actual part before buying, or just get the TO-92 from RoboticsBD.
- Any small NPN works here (2N2222A, PN2222A, 2N3904, BC337, S8050). The job is
  switching a few milliamps.
- **Pinout: the square pad is the Emitter, the middle pad is the Base, the third is
  the Collector.** TO-92 pinouts differ between manufacturers, so check yours with a
  multimeter's diode test. If your part's emitter and collector come out the other
  way round, just fit it rotated 180° (flat face the other way) — the base is the
  middle pin on every common variant, so only E and C swap.

**Resistors** (1/4 W, 5% is fine)

| Qty | Value | Qty | Value |
|----|-------|----|-------|
| 28 | 220 Ω (segment resistors) | 1 | 2 kΩ |
| 6 | 1 kΩ | 1 | 6.8 kΩ |
| 2 | 10 kΩ | 1 | 20 kΩ |
| 1 | 200 Ω | 1 | 100 kΩ |
| 2 | 2.2 MΩ | 1 | 220 kΩ |
| 1 | 10 MΩ | | |

Total 45 resistors. The 2.2 MΩ replaces the original's 2 MΩ, which isn't a stocked value.

**Segment resistors are 220 Ω** in the design, the BOM and the silkscreen. TI's datasheet
(page 3-71) gives the CD4026's segment output drive at 5 V as 1.6 mA minimum / 3.2 mA
typical at 2.5 V out. The chip, not the resistor, sets the brightness. 470 Ω would give
roughly 2.2 mA per segment; 220 Ω gives about 3 mA, which is as much as the chip will
provide. Both are safe — the output current-limits itself.

**Run it from 6 V (4 × AA) rather than 5 V.** The CD4026 drives harder at 6 V, so the
digits are noticeably brighter. Everything on the board is rated well past 6 V.

**Capacitors**

| Qty | Value | Type |
|----|-------|------|
| 16 | 100nF (104) | ceramic, 2.5 mm lead pitch |
| 2 | 10nF (103) | ceramic |
| 1 | 1µF (105) | ceramic, **not** electrolytic — this one sees both polarities |
| 4 | 22pF | ceramic (2 from LCSC, 2 spare) |
| 1 | 100µF | electrolytic, 6.3 mm, ≥10 V |
| 1 | 22nF (223) | ceramic — **C3 alternate, see below** |

**C3 — buy both values and try them on the bench.** C3 sets the NE555 (U6) burst
oscillator, and the 100 nF the board is drawn with puts it at 4.8 kHz. Above roughly
4800 RPM a revolution arrives before the previous burst has finished, that revolution is
dropped, and the display settles on a steady, jitter-free **half reading** — 6000 RPM
shows as 3000, with nothing to warn you. 22 nF moves the oscillator to 21.8 kHz and the
ceiling past 21,000 RPM, clear of the 9999 the four digits can show. It changes nothing
else: low-speed accuracy and the ±60 RPM quantisation are identical either way.

The 100 nF is what the schematic, the silkscreen and the BOM all say, so the board is
built that way. Fit the 22 nF when you want to check the high end. C3 sits in a socket
position you can reach — it's the disc cap at board X 179.6, Y 81.0, next to U6.

The BOM lists both: C3 as its own line at 100nF, and a `C3 (alt)` line at 22nF.

## Before soldering everything

The CD4026 segment pinout is now **confirmed against TI's datasheet** (6=f, 7=g, 9=d,
10=a, 11=e, 12=b, 13=c), so the schematic is right. A breadboard test of one digit is
still worth 5 minutes to judge brightness: 5–6 V on pin 16, pin 8 to ground, pin 2 to
ground, pin 3 to +V, pulse pin 1, segments to the display through 220 Ω.

## Mode switch (the table is printed on the board, between U10 and the displays)

| Mode | SW1 switches ON |
|------|-----------------|
| RPM | 2 and 3 |
| RPS | 2 and 4 |
| Counter | 1 only |

In RPM and RPS the display holds each reading for ~3 s and blanks for 1 s while counting.
In Counter mode the display stays on and counts continuously.
