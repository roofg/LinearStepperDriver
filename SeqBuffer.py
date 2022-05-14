from collections import deque


# Buffer holds tuple of sequence to execute (nSteps, timeDeltaMs)
class SeqBuffer:
    def __init__(self):
        self.buf = deque(tuple(), 200)

    def appendsequence(self, nSteps, timedelta, direc):
        self.buf.append((nSteps, timedelta, direc))

    def nextsequence(self):
        if len(self.buf) > 0:
            return self.buf.popleft()
        return 0, 0, 0

    def lenthsequence(self):
        return len(self.buf)
