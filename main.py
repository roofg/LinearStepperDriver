#!/usr/bin/python
import machine
import utime
import _thread

pin_led = machine.Pin(25, machine.Pin.OUT)
pin_en = machine.Pin(19, machine.Pin.OUT) # GP19 / 25 / Enable pin
pin_dir = machine.Pin(20, machine.Pin.OUT) # GP20 / 26 / Direction pin
pin_step = machine.Pin(21, machine.Pin.OUT) # GP21 / 27 / Step pin

pin_pot = machine.Pin(26, machine.Pin.OUT)

adcRangeLowerThreshhold = 400;
adcRangeUpperThreshhold = 65536;

microStepping = 16 #// 1/16 th micro stepping -> change switches/jumpers on driver board accordingly
stepperRevolutionSteps = 200 #200 steps per revolution, 1.8 degrees
stepsForFullTurn = 200 * microStepping
toggleStepPinForSingleStep = float(2)
interStepPauseFullRotationMicro = float(1000000.0) / float(stepsForFullTurn) / toggleStepPinForSingleStep #Full rotation in 1 second

nFullRotations = 10 #Number of Rotations to make

def core0_thread():
    global interStepPauseMicro
    interStepPauseMicro = 1000
    pin_en.value(1)
    utime.sleep_ms(1000)
    pin_en.value(0)
    pin_dir.value(0)
    while True:
        pin_dir.value(1)
        utime.sleep_us(interStepPauseFullRotationMicro)
        pin_dir.value(0)
        utime.sleep_us(interStepPauseFullRotationMicro)


def core1_thread():
    global interStepPauseMicro
    adcRange = float(adcRangeUpperThreshhold - adcRangeLowerThreshhold)
    while True:
        adc = machine.ADC(pin_pot)
        speedRatio = checkBounds(float(adc.read_u16() - adcRangeLowerThreshhold) / adcRange)
        print("SpeedRatio = {}".format(speedRatio))
        utime.sleep_ms(100)


def checkBounds(speedRatio):
    if(speedRatio < 0):
        return 0
    if(speedRatio >= adcRangeUpperThreshhold):
        return 1
    return round(speedRatio, 2)


worker_thread = _thread.start_new_thread(core1_thread, ())
core0_thread()
