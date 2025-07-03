import time
import board
import digitalio
import pwmio
import analogio
import audiocore
import audiopwmio

# Audio board
#pwm = audiopwmio.PWMAudioOut(board.GP10)

# Location Sensing Reed Switches
reed_pins = [board.GP22, board.GP27, board.GP28, board.GP21]
reed_switches = []

for pin in reed_pins:
    reed = digitalio.DigitalInOut(pin)
    reed.direction = digitalio.Direction.INPUT
    reed.pull = digitalio.Pull.UP  # Pull-up makes open = True (HIGH)
    reed_switches.append(reed)

# Motor driver pins
in1 = digitalio.DigitalInOut(board.GP13)
in1.direction = digitalio.Direction.OUTPUT

in2 = digitalio.DigitalInOut(board.GP12)
in2.direction = digitalio.Direction.OUTPUT

ena = pwmio.PWMOut(board.GP11, frequency=25000, duty_cycle=0)

# Potentiometer
pot = analogio.AnalogIn(board.A0)  # GP26

# LEDs for Buttons
LED_forward = digitalio.DigitalInOut(board.GP17)
LED_forward.direction = digitalio.Direction.OUTPUT

LED_backward = digitalio.DigitalInOut(board.GP16)
LED_backward.direction = digitalio.Direction.OUTPUT

# Buttons (pull-up, active low)
button_forward = digitalio.DigitalInOut(board.GP19)
button_forward.direction = digitalio.Direction.INPUT
button_forward.pull = digitalio.Pull.UP

button_reverse = digitalio.DigitalInOut(board.GP18)
button_reverse.direction = digitalio.Direction.INPUT
button_reverse.pull = digitalio.Pull.UP

# State variables for toggling
forward_on = False
reverse_on = False

# For detecting button press edges
last_forward_state = True
last_reverse_state = True

# Current pwm duty cycle for ramping
current_pwm = 0

# Global audio variable to hold file reference so it stays open while playing
wave_file = None

def play_sound(filename):
    global wave_file
    if pwm.playing:
        pwm.stop()
        wave_file.close()
    wave_file = open(filename, "rb")
    wave = audiocore.WaveFile(wave_file)
    pwm.play(wave)
    print(f"Playing: {filename}")

def read_speed():
    raw = pot.value  # 0–65535
    level = raw // 1000
    if level > 65:
        level = 65
    pwm_value = int((level / 65) * 65535)
    return raw, level, pwm_value

def set_motor_direction(forward):
    if forward:
        in1.value = True
        in2.value = False
        LED_forward.value = True
        LED_backward.value = False
    else:
        in1.value = False
        in2.value = True
        LED_forward.value = False
        LED_backward.value = True

def ramp_pwm(target_pwm, step=1000, delay=0.05):
    global current_pwm
    if target_pwm > current_pwm:
        # Ramp up
        for val in range(current_pwm, target_pwm + 1, step):
            ena.duty_cycle = val
            current_pwm = val
            time.sleep(delay)
    else:
        # Ramp down
        for val in range(current_pwm, target_pwm - 1, -step):
            ena.duty_cycle = val
            current_pwm = val
            time.sleep(delay)

def stop_motor():
    ramp_pwm(0)
    in1.value = False
    in2.value = False

while True:
    raw, level, target_pwm = read_speed()

    current_forward = button_forward.value
    current_reverse = button_reverse.value

    # Toggle forward on button press (active low)
    if last_forward_state and not current_forward:
        forward_on = not forward_on
        if forward_on:
            reverse_on = False

    # Toggle reverse on button press (active low)
    if last_reverse_state and not current_reverse:
        reverse_on = not reverse_on
        if reverse_on:
            forward_on = False

    last_forward_state = current_forward
    last_reverse_state = current_reverse

    if forward_on:
        print(f"[FORWARD] Pot raw: {raw}, level: {level}, Target PWM: {target_pwm}")
        set_motor_direction(True)
        ramp_pwm(target_pwm)
        LED_forward.value = True
        LED_backward.value = False
    elif reverse_on:
        print(f"[REVERSE] Pot raw: {raw}, level: {level}, Target PWM: {target_pwm}")
        set_motor_direction(False)
        ramp_pwm(target_pwm)
        LED_forward.value = False
        LED_backward.value = True
    else:
        print(f"[OFF] Pot raw: {raw}, level: {level}")
        stop_motor()
        LED_forward.value = False
        LED_backward.value = False

    for i, reed in enumerate(reed_switches):
        if not reed.value:  # LOW = triggered
            if i == 0:
                print("Checking buttons or sensors...")
                # Check if audio has finished
                if not pwm.playing:
                    print("Audio done.")
                    wave_file.close()
                    #break  # or start another sound, or loop again
            elif i == 1:
                print("Reed 2 triggered: play station jingle")
            elif i == 2:
                print("Reed 3 triggered: log arrival")
            elif i == 3:
                print("Reed 4 triggered: start timer")
    time.sleep(0.05)
