#!/usr/bin/env python2.7

import argparse
import time

from .pyrint import Pyrint

VERSION = version = __version__ = '0.0.1'

parser = argparse.ArgumentParser(description='')
parser.add_argument('--url',
                    dest='url',
                    help='url to queue for print jobs')
parser.add_argument('-v',
                    dest='verbose',
                    nargs='?',
                    const=True,
                    default=False,
                    help='verbose mode')
parser.add_argument("-r",
                    dest="restart",
                    nargs="?",
                    const=True,
                    default=False,
                    help="rolling restarts")
parser.add_argument("--scan",
                    dest="scan",
                    nargs="?",
                    default=False,
                    const=True,
                    help="test: scan for printer only")
parser.add_argument("--print",
                    dest="printer",
                    default=False,
                    help="test: print only")
parser.add_argument("--provision",
                    dest="provision",
                    default=False,
                    help="provision the device for business use")
options = parser.parse_args()


def main():
    lpp = Pyrint()
    try:
        lpp.start()
    except KeyboardInterrupt:
        del lpp
    except Exception as e:
        print type(e), e
        lpp.log(source='lpp', exception=str(e))
        if options.restart:
            time.sleep(60)
            main()

if __name__ == "__main__":
    if options.scan:
        """Scan only for testing"""
        lpp = Pyrint()
        lpp.scan()
        print "Found:", lpp.printers
    elif options.printer:
        """Print test only"""
        lpp = Pyrint()
        lpp.test_print(options.printer)
    elif options.provision:
        lpp = Pyrint()
        lpp.provision()
    else:
        main()
