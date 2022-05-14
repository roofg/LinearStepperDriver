#!/usr/bin/python
import machine
import _thread

from SeqBuffer import *
from SeqRunner import *


pin_led = machine.Pin(25, machine.Pin.OUT)
pin_en = machine.Pin(19, machine.Pin.OUT)  # GP19 / 25 / Enable pin
pin_dir = machine.Pin(20, machine.Pin.OUT)  # GP20 / 26 / Direction pin
pin_step = machine.Pin(21, machine.Pin.OUT)  # GP21 / 27 / Step pin
pin_en.value(1)

pin_pot = machine.Pin(26, machine.Pin.OUT)
adc = machine.ADC(pin_pot)

adcRangeLowerThreshhold = 400
adcRangeUpperThreshhold = 65536

microStepping = 4  # // 1/4 th micro stepping -> change switches/jumpers on driver board accordingly
stepperRevolutionSteps = 200  # 200 steps per revolution, 1.8 degrees
stepsForFullTurn = 200 * microStepping
interStepPauseFullRotationMicro = float(1000000.0) / float(stepsForFullTurn)  # Full rotation in 1 second

pulsDelta = 1

def core1_thread():
    global lock
    global threadInterchangeVar
    threadInterchangeVar = 1000
    interStepPause = 1000
    utime.sleep_ms(3000)
    pin_dir.value(0)
    nSteps = 2200
    pin_en.value(0)
    while True:
        pin_dir.value(0)
        utime.sleep_ms(100)

        for i in range(nSteps):
            pin_step.value(1)
            utime.sleep_us(pulsDelta)
            pin_step.value(0)
            utime.sleep_us(interStepPause)

        lock.acquire()
        interStepPause = threadInterchangeVar
        lock.release()

        utime.sleep_ms(100)
        pin_dir.value(1)

        for i in range(nSteps):
            pin_step.value(1)
            utime.sleep_us(pulsDelta)
            pin_step.value(0)
            utime.sleep_us(interStepPause)

        lock.acquire()
        interStepPause = threadInterchangeVar
        lock.release()
        gc.collect() #possibliy _thread lib is leaking memory


def core0_thread():
    global lock
    global threadInterchangeVar
    adcRange = float(adcRangeUpperThreshhold - adcRangeLowerThreshhold)
    while True:
        interStepPause = int(checkBounds(float(adc.read_u16() - adcRangeLowerThreshhold) / adcRange) * interStepPauseFullRotationMicro)
        lock.acquire()
        threadInterchangeVar = interStepPause
        lock.release()
        print("InterStepPause core1: {}".format(interStepPause))
        utime.sleep_ms(250)
        gc.collect()

def checkBounds(speedRatio):
    if (speedRatio < 0):
        return 0
    if (speedRatio >= adcRangeUpperThreshhold):
        return 1
    return round(speedRatio, 2)


# create global lock
lock = _thread.allocate_lock()

buf = SeqBuffer()
print(buf)
buf.appendsequence(50, 100)
buf.appendsequence(30, 80)
print(buf.lenthsequence())
(nSteps, timeDeltaMs, direc) = buf.nextsequence()
print(buf.lenthsequence())
print(nSteps)
print(timeDeltaMs)
print(buf.lenthsequence())

#worker_thread = _thread.start_new_thread(core1_thread, ())
#core0_thread()

