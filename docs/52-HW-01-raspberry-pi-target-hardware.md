# Raspberry Pi target hardware — planned stack

## Scope

Project-level hardware note for the Event Timing Raspberry Pi target. This is deliberately kept
outside the image repository: the image repository owns image creation/installation, while this
document owns planned physical target hardware and mechanical/electrical fit questions.

## Planned components

| Component | Role | Current assessment |
| --- | --- | --- |
| Raspberry Pi Zero / Zero W class board | test target | baseline target class |
| Waveshare 2.13inch e-Paper HAT+ (27467) | local status display + DS3231 RTC | electrically promising |
| Pimoroni Button SHIM (PIM301) | five local buttons + RGB status LED | electrically compatible on shared I2C |
| Pimoroni GPIO Hammer Header male (COM1104) | normal GPIO/HAT header with solderless Pi Zero retention | preferred first fit; underside SHIM uses the short protruding pin tails if clearance is sufficient |
| Raspberry Pi RTC Battery SC1163 / ML2020 | RTC backup candidate | chemistry/voltage suitable; connector/polarity not yet qualified |
| UUGear Zero4U | four-port USB hub below Pi Zero | intended future lower-layer board |
| 3-pin JST-SH UART breakout | serial boot/debug console | must be positioned clear of future Zero4U |

## Electrical bus use

### Waveshare 2.13inch e-Paper HAT+

The HAT+ uses:

- SPI0 for the e-paper display;
- GPIO control lines for reset/DC/busy;
- I2C1 for the onboard DS3231 RTC;
- HAT ID EEPROM on the HAT ID bus.

The schematic identifies the DS3231 at I2C address `0x68`.

### Button SHIM

Button SHIM uses an I2C TCA9554A I/O expander at address `0x3f`.

Therefore the current expected I2C combination is:

```text
I2C1
  +-- Button SHIM   0x3f
  +-- DS3231 RTC    0x68
```

No address conflict is expected between these two boards.

### UART console

The UART console uses GPIO14/TX and GPIO15/RX and is independent from the Waveshare SPI and
Button SHIM I2C buses.

## Mechanical stack direction

Current intended stack follows the proven underside-SHIM arrangement used in the
Electromaker Inky pHAT/Button SHIM Pi Zero build:

```text
top
  Waveshare 2.13inch e-Paper HAT+
  standard male Hammer Header pins
  Raspberry Pi Zero
  Button SHIM flush against the underside, soldered to exposed short pin tails if fit allows
  Zero4U (future, mounted below using pogo contacts)
bottom
```

The Electromaker reference build uses an extra-tall female stacking header, but that extra height
is not a requirement created by the Button SHIM itself. The SHIM PCB is only 0.8 mm thick and is
designed to be soldered directly onto GPIO pins while a HAT/pHAT remains usable above it.

For this test target the preferred first fit is therefore the standard Pimoroni male Hammer Header
(COM1104), installed in its documented orientation with the long pin ends upward. The underside
Button SHIM is soldered to the short pin tails protruding below the Pi **only if** the physical
fit confirms enough exposed length for the 0.8 mm PCB plus a reliable solder joint.

The remaining qualification question is therefore exposed underside pin length, not a need for an
extra-tall header.

Do not select a more complex contact solution before physically fitting the parts. First dry-fit the
Hammer Header, Pi Zero and 0.8 mm Button SHIM and measure the actual exposed tail length and
clearance.

Preferred decision order:

1. direct underside fit, with the SHIM flush against the Pi and soldered to the protruding tails;
2. if direct soldering is undesirable or the exposed tails are marginal, prototype a simple
   spring-loaded 3D-printed retainer using copper tape as the contact surface;
3. only consider dedicated spring contacts, a long-tail header or a custom PCB if the simple
   mechanical solutions prove unreliable.

The copper-tape concept should use the printed part to provide contact pressure; the copper tape is
the conductor, not the spring. This leaves the normal female header fully
available above the Pi for the e-paper HAT and avoids relying on the HAT socket to clamp the SHIM
electrically.

The Button SHIM still projects beyond the board edge so the five buttons remain accessible.

Zero4U also mounts below the Pi Zero and contacts the USB/power test pads with pogo pins. Therefore
the final mechanical qualification must specifically check clearance between the underside Button
SHIM/header soldering and the Zero4U board/standoffs/pogo geometry. The underside-SHIM arrangement
is the preferred direction; Zero4U compatibility remains a physical-fit qualification item.

## UART connector consequence

A JST-SH UART breakout should therefore **not** be permanently mounted directly underneath the
Pi in the area needed by Zero4U.

Preferred direction:

- take GND, GPIO14/TX and GPIO15/RX from the Pi/header;
- use three short wires;
- mount the JST-SH breakout at the side edge of the assembly or on a small mechanical bracket;
- keep the lower Pi surface/test-pad region clear for Zero4U.

This keeps the serial console accessible after the USB hub is added.

## RTC battery

The Waveshare HAT+ contains a DS3231 and exposes a 2-pin battery connector for a rechargeable
3V/3.3V lithium backup battery.

The official Raspberry Pi 5 RTC battery is an ML2020 rechargeable lithium-manganese cell with a
2-pin JST-SH plug, so its chemistry and nominal voltage are plausible for this use.

Compatibility check status:

- **battery chemistry/voltage: verified plausible** — the official Raspberry Pi battery is an
  ML2020 rechargeable lithium-manganese cell, nominal 3.0 V;
- **battery charging range: verified plausible** — Panasonic specifies 2.8–3.2 V for ML2020;
- **Waveshare requirement: verified** — Waveshare specifies a rechargeable 3/3.3 V lithium
  battery on the 2-pin battery header;
- **Waveshare circuit: checked** — the schematic connects BAT1 to DS3231 VBAT and includes a
  3.3 V-to-VBAT charge path through a diode and resistor;
- **physical connector: still open** — Waveshare calls it only a "2PIN JST connector", whereas
  Raspberry Pi explicitly specifies JST-SH for its battery.

Therefore the remaining pre-connection check is mechanical/electrical connector compatibility:
confirm JST series/pitch, keying and polarity against the actual HAT. The Waveshare schematic labels
BAT1 pin 1 as GND and pin 2 as VBAT.

## Qualification order

1. Pi Zero alone: headless boot + UART + SSH.
2. Fit the standard male Hammer Header, measure/check the exposed underside pin tails, and if
   sufficient solder the 0.8 mm Button SHIM underneath; confirm I2C detection/button operation.
3. Add Waveshare HAT+ above the Pi without battery; qualify SPI display and DS3231 RTC.
4. Verify battery connector mechanically/electrically, then add RTC battery.
5. Verify the Pi + underside Button SHIM + top e-paper HAT mechanically.
6. Add Zero4U underneath and re-check:
   - pogo contact alignment;
   - header/standoff clearance;
   - UART connector clearance;
   - USB enumeration;
   - power/current behaviour.
7. Only then treat the complete stack as the target-test hardware baseline.
