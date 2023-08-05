from subprocess import Popen


class SCProxy(object):
    def __init__(self, host="127.0.0.1", port=8123, cmd="scproxy"):
        self.host = host
        self.port = port
        self.cmd = cmd

    def start(self):
        self.proxy = Popen([self.cmd])  # XXX: implement port

    def stop(self):
        rv = self.proxy.poll()
        if rv is None:
            self.proxy.kill()
        return self.proxy.returncode
