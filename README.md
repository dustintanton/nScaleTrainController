# 🚂 Pico Train Controller

This project uses a Raspberry Pi Pico (or Pico W) to control a DC model train with direction toggling, speed control via potentiometer, and reed switch-based automation triggers. It also includes support for optional sound playback via PWM audio boards.

## Features

- Direction control with toggle buttons (Forward / Reverse)
- PWM motor speed ramping for smooth acceleration/deceleration
- Potentiometer-based speed adjustment
- Reed switch triggers (e.g. for location-based automation)
- LED indicators for active direction
- Optional PWM audio playback (commented out in code)

## Hardware Used

- Raspberry Pi Pico / Pico W  
- H-Bridge motor driver (dual channel)
- Reed switches (for location sensing)
- Potentiometer (for speed input)
- MAX98357A / PWM audio board (optional)
- Buttons & LEDs for control feedback

## Wiring Overview

| Component        | Pin Example |
|------------------|-------------|
| Motor A          | GP12, GP11, GP13 (PWM) |
| Motor B          | GP9, GP8, GP7 (PWM) |
| Potentiometer    | GP26 / A0   |
| Buttons          | GP19 (Forward), GP18 (Reverse) |
| LEDs             | GP17 (Forward), GP16 (Reverse) |
| Reed Switches    | GP0, GP3, GP6, GP10 |
| Audio PWM (opt)  | GP1, GP2, GP4, GP5 |

## How It Works

- Press the **Forward** or **Reverse** button to toggle direction.
- Adjust the **potentiometer** to set desired speed.
- The train **ramps up/down** smoothly when changing speed or stopping.
- **Reed switches** can trigger actions like sounds or speed changes.
- Optional audio system can play `.wav` files on location triggers.

## Notes

- The audio system and second motor channel are set up but currently commented out so they can be implemented by hand.
- The script uses **pull-up buttons**, so active state is `LOW`.
- `wave_file` must remain open while playing audio — it is managed globally.
