import sys
import time
import threading


class Progress(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.progress = 1
        self.printers = 0
        self.go = True

    def run(self):
        while self.go:
            sys.stdout.flush()
            sys.stdout.write('\r')
            sys.stdout.write("[%-20s] %d%%, found %d" % ('='*int(float(self.progress)/254.0*20.0), int(float(self.progress)/254.0*100.0), self.printers))
            sys.stdout.flush()
            time.sleep(.5)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def update(self, printers):
        if printers is False:
            self.go = False
        else:
            self.progress = self.progress + 1
            self.printers = printers
