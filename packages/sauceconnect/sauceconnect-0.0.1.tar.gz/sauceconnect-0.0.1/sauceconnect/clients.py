import threading
import Queue

from os import environ

from proxy import SCProxy
from util import create_vm
from libsauceconnect import SauceConnect

class SC(object):

    def __init__(self, user=environ['SAUCE_USERNAME'], api_key=environ['SAUCE_ACCESS_KEY']):
        self.proxy = SCProxy()
        self.proxy.start()

        vm = create_vm(user, api_key)

        self.sc = SauceConnect(vm, self.proxy, user, api_key)

        self.q = Queue.Queue()


    def _scrunner(self):
        rv = self.sc.run()
        self.q.put(rv)

    def start(self):
        self.t = threading.Thread(target=self._scrunner)
        self.t.daemon = True
        self.t.start()

    def stop(self):
        self.sc.stop()

    def __del__(self):
        if hasattr(self, 'sc'):
            self.sc.stop()

        if hasattr(self, 'proxy'):
            self.proxy.stop()


class SCGuard(SC):
    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()
