import time
import board
import digitalio
import pwmio
import analogio

# Motor driver pins
in1 = digitalio.DigitalInOut(board.GP15)
in1.direction = digitalio.Direction.OUTPUT

in2 = digitalio.DigitalInOut(board.GP14)
in2.direction = digitalio.Direction.OUTPUT

ena = pwmio.PWMOut(board.GP13, frequency=25000, duty_cycle=0)

# Potentiometer
pot = analogio.AnalogIn(board.A0)  # GP26

# LEDs for Buttons
LED_forward = digitalio.DigitalInOut(board.GP4)
LED_forward.direction = digitalio.Direction.OUTPUT

LED_backward = digitalio.DigitalInOut(board.GP3)
LED_backward.direction = digitalio.Direction.OUTPUT

# Buttons (pull-up, active low)
button_forward = digitalio.DigitalInOut(board.GP7)
button_forward.direction = digitalio.Direction.INPUT
button_forward.pull = digitalio.Pull.UP

button_reverse = digitalio.DigitalInOut(board.GP2)
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

    #time.sleep(0.05)
