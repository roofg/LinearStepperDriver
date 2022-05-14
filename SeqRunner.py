import utime
import gc


class SeqRunner:
    def __init__(self, seq_buf, pin_en, pin_step, pin_dir):
        self.seq_buf = seq_buf
        self.pin_en = pin_en
        self.pin_step = pin_step
        self.pin_dir = pin_dir
        self.execute = 1
        self.puls_delta = 1
        gc.enable()

    def run(self):
        self.execute = 1
        utime.sleep_ms(3000)
        self.pin_en.value(0)
        while self.execute:
            (nsteps, time_delta, dir) = self.seq_buf.nextsequence()
            self.runsequence(nsteps, time_delta, dir)

    def stop(self):
        self.pin_en.value(1)
        self.execute = 0

    def runsequence(self, nsteps, time_delta, dir):
        self.pin_dir.value(dir)
        for n in range(nsteps):
            self.pin_step.value(1)
            utime.sleep_us(self.puls_delta)
            self.pin_step.value(0)
            utime.sleep_us(self.time_delta)
        gc.collect()
