import socket
import Queue
import thread
import commands
import re
import httplib
import urllib
import uuid
import time
import os
import json
from multiprocessing.pool import ThreadPool

from .progress import Progress
from .pyrint import version


class Pyrint:
    def __init__(self, options):
        self.options = options
        if self.options.verbose:
            print('pyrint init....')
        self.go = True
        self.queue = Queue.Queue()
        self.params = urllib.urlencode({'macaddr': self.get_mac_address(), 'token': self.get_token()})
        self.headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/x-www-form-urlencoded'}
        self.printers = []
        if self.options.verbose:
            self._progress = Progress()

    def start(self):
        self.scan()
        if self.options.verbose:
            print("\033[91mSpooler thread starting...\033[0m ended")
        self.spooler = thread.start_new_thread(self.spool, ())
        self.request()

    def __del__(self):
        self.end()

    def end(self):
        self.go = False
        self.queue.put('kill')

    def spool(self):
        while self.go:
            if self.options.verbose:
                print('\033[1m---> Spool Thread\033[0m, size:', self.queue.qsize())
            msg = self.queue.get()
            if self.options.verbose:
                print('\033[1m---> Spool:\033[0m dequeued')
            if msg != 'kill':
                for printer in self.printers:
                    psock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    psock.settimeout(20)
                    if self.options.verbose:
                        print('\033[1m---> Spool:\033[0m connecting to printer at %s...' % printer)
                    psock.connect((printer, 9100))
                    if self.options.verbose:
                        print('\033[1m---> Spool:\033[0m sending to printer...')
                    sent = psock.send(msg)
                    if self.options.verbose:
                        print('\033[1m---> Spool:\033[0m sent')
                    if sent == 0:
                        raise RuntimeError("socket connection broken")
                    psock.close()

    def request(self):
        while self.go:
            if self.options.verbose:
                print('\033[94m---> Request\033[0m begin')
            con = self.get_http_connection()
            try:
                con.request('POST', '/listen', self.params, self.headers)
                response = con.getresponse()

            except socket.timeout:
                if self.options.verbose:
                    print('\033[94m---> Request\033[0m Timout')
                pass

            except Exception as e:
                if self.options.verbose:
                    print('\033[94m---> Request\033[0m', str(e))
                self.log(exception=str(e), source='longpool')

            except httplib.CannotSendRequest:
                if self.options.verbose:
                    print('\033[94m---> Request\033[0m Cannot send request.')
                time.sleep(1)

            else:
                if response.status == 200:
                    data = response.read()
                    self.queue.put_nowait(data)
                    if self.options.verbose:
                        print('\033[94m---> Request\033[0m queue put data, qsize:', self.queue.qsize())

                elif response.status == 204:
                    if self.options.verbose:
                        print('\033[94m---> Request\033[0m (204) No content to print.')

                elif response.status == 401:
                    """
                    What if there are prints in the queue? Cannot quit then.
                    """
                    if self.options.verbose:
                        print('\033[94m---> Request\033[0m (401) Unauthorized request or kill.', self.params)
                    self.log(source="longpool", statuscode=401)
                    self.end()

                else:
                    if self.options.verbose:
                        print('\033[94m---> Request\033[0m', response.status, response.reason)
                    self.log(source="longpool",
                             statuscode=response.status,
                             reason=response.reason)
            finally:
                try:
                    con.close()
                except Exception:
                    pass

    def scan(self):
        pool = ThreadPool(20)
        ip = self.get_ip_address()
        if self.options.verbose:
            self._progress.start()
        broad = re.sub('\d+$', '', ip)
        if self.options.verbose:
            print("--------------------------------\n--------------------------------\n\033[91mScan\033[0m started")
        for x in xrange(1, 21):
            pool.apply_async(self._do_scan, (broad, x*13 + 1))
        pool.close()
        pool.join()
        if self.options.verbose:
            print("")
            for printer in self.printers:
                print("\033[91mScan\033[0m found", printer)
            print("")
            print("\033[91mScan\033[0m ended")
            print("--------------------------------\n--------------------------------\n")
            self._progress.update(False)
            del self._progress
        del pool

    def _do_scan(self, broad, x):
        for i in xrange(x, x+13):
            if i < 255:
                if self.options.verbose:
                    self._progress.update(len(self.printers))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    sock.connect((broad+str(i), 9100))
                except Exception:
                    continue
                else:
                    sock.close()
                    self.printers.append(broad+str(i))
            else:
                break

    def get_ip_address(self):
        return re.search('(\d+\.\d+\.\d+\.\d+)', str(commands.getstatusoutput('ifconfig | grep cast')[1])).groups()[0]

    def get_mac_address(self):
        return '::1'

    def get_token(self):
        f = file(os.path.join(os.path.dirname(__file__), '../.pyrint'), 'r')
        t = f.read()
        f.close()
        return t

    def get_http_connection(self):
        if self.options.https:
            return httplib.HTTPSConnection(self.options.url, timeout=20)
        else:
            return httplib.HTTPConnection(self.options.url, timeout=20)

    def test_print(self, printer):
        if self.options.verbose:
            print('Test: print to', printer)
        psock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        psock.settimeout(20)
        psock.connect((printer, 9100))
        sent = psock.send('\x1b@Bonjour et bienvenue!\x1bd\x0a\x1D\x560')
        if sent == 0:
            raise RuntimeError("socket connection broken")
        psock.close()

    def log(self, **kwargs):
        kwargs['macaddr'] = self.get_mac_address()
        kwargs['device'] = "raspberrypie"
        kwargs['version'] = version
        con = self.get_http_connection()
        con.request('POST', '/log', body=json.dumps(kwargs), headers={"Content-type": "application/json", "Accept": "text/plain"})
        response = con.getresponse()
        if self.options.verbose:
            print('Logger:', response.status, response.reason, response.read())
        con.close()

    def provision(self):
        token = str(uuid.uuid4())
        con = self.get_http_connection()
        kwargs = dict(token=token, macaddr=self.get_mac_address())
        con.request('POST', '/provision', body=json.dumps(kwargs), headers={"Content-type": "application/json", "Accept": "text/plain"})
        response = con.getresponse()
        if self.options.verbose:
            print('Provision:', response.status, response.reason, response.read())
        con.close()
        f = file('../.pyrint', 'w+')
        f.write(token)
        f.close()
