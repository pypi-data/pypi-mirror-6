import ctypes as ct
import ctypes.util


def _do_find_library(name):
    # First just try to find in system library paths
    try:
        lib = ct.CDLL(name, mode=ct.RTLD_GLOBAL)
        if lib:
            return lib
    except:
        pass

    # Next, try ctypes.util.find_library()
    p = ctypes.util.find_library(name)
    if p:
        lib = ct.CDLL(p, mode=ct.RTLD_GLOBAL)
        return lib

    # Next, python library installation path
    import os
    from distutils.sysconfig import get_python_lib
    try:
        lib = ct.CDLL(os.path.join(get_python_lib(), name),
                      mode=ct.RTLD_GLOBAL)
        return lib
    except:
        pass

    # Last, python search path for modules
    import sys
    for p in sys.path:
        try:
            lib = ct.CDLL(os.path.join(p, name), mode=ct.RTLD_GLOBAL)
            return lib
        except:
            pass

    # Out of ideas
    return None


def _find_library(*names):
    lib = None
    for name in names:
        lib = _do_find_library(name)
        if lib is not None:
            return lib
        if not name.startswith("lib"):
            lib = _do_find_library("lib" + name)
            if lib is not None:
                return lib
        for suffix in [".so", ".dylib", ".dll"]:
            if not name.endswith(suffix):
                lib = _do_find_library(name + suffix)
                if lib is not None:
                    return lib
            if not name.startswith("lib") and not name.endswith(suffix):
                lib = _do_find_library("lib" + name + suffix)
                if lib is not None:
                    return lib
    return lib


_lib = _find_library("sauceconnect")
if _lib is None:
    raise Exception("can't find libsauceconnect")

_sc_new = _lib.sc_new
_sc_new.restype = ct.c_void_p
_sc_new.argtypes = None

_sc_free = _lib.sc_free
_sc_free.restype = None
_sc_free.argtypes = [ct.c_void_p]

_SC_PARAM_IS_SERVER = 0x01
_SC_PARAM_KGP_HOST = 0x02
_SC_PARAM_KGP_PORT = 0x03
_SC_PARAM_EXT_HOST = 0x04
_SC_PARAM_EXT_PORT = 0x05
_SC_PARAM_LOGFILE = 0x06
_SC_PARAM_LOGLEVEL = 0x07
_SC_PARAM_MAX_LOGSIZE = 0x08
_SC_PARAM_CERTFILE = 0x09
_SC_PARAM_KEYFILE = 0x0a
_SC_PARAM_LOCAL_PORT = 0x0b
_SC_PARAM_USER = 0x0c
_SC_PARAM_API_KEY = 0x0d

_sc_get = _lib.sc_get
_sc_get.restype = ct.c_int
_sc_get.argtypes = [ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_size_t]

_sc_set = _lib.sc_set
_sc_set.restype = ct.c_int
_sc_set.argtypes = [ct.c_void_p, ct.c_int, ct.c_void_p]

_sc_init = _lib.sc_init
_sc_init.restype = ct.c_int
_sc_init.argtypes = [ct.c_void_p]

_sc_run = _lib.sc_run
_sc_run.restype = ct.c_int
_sc_run.argtypes = [ct.c_void_p]

_sc_stop = _lib.sc_stop
_sc_stop.restype = ct.c_int
_sc_stop.argtypes = [ct.c_void_p]

_SC_STATUS_RUNNING = 0x01
_SC_STATUS_EXITING = 0x02

_sc_status = _lib.sc_status
_sc_status.restype = ct.c_int
_sc_status.argtypes = [ct.c_void_p]


class SauceConnect(object):
    def __init__(self, vm_tunnel, proxy, user, api_key,
                 local_port=8089):
        self.vm_tunnel = vm_tunnel
        self.proxy = proxy
        self._ctx = _sc_new()
        if self._ctx is None:
            raise Exception("failed to create SauceConnect context")
        for p, v in [(_SC_PARAM_IS_SERVER, 0),
                     (_SC_PARAM_KGP_HOST, vm_tunnel.host),
                     (_SC_PARAM_KGP_PORT, vm_tunnel.ssh_port),
                     (_SC_PARAM_EXT_HOST, proxy.host),
                     (_SC_PARAM_EXT_PORT, proxy.port),
                     (_SC_PARAM_LOCAL_PORT, local_port),
                     (_SC_PARAM_USER, user),
                     (_SC_PARAM_API_KEY, api_key),
                     (_SC_PARAM_LOGLEVEL, 2)]:
            if isinstance(v, int):
                i = ct.c_int(v)
                ret = _sc_set(self._ctx, p, ct.cast(ct.pointer(i),
                                                    ct.c_void_p))
            else:
                s = ct.c_char_p()
                s.value = v
                ret = _sc_set(self._ctx, p, ct.cast(s, ct.c_void_p))
            if ret:
                raise Exception("failed to set %d -> %s" % (p, str(v)))
        if _sc_init(self._ctx):
            raise Exception("failed to initialize the SauceConnect engine")

    def __del__(self):
        if self._ctx:
            _sc_free(self._ctx)
            self._ctx = None

    def run(self):
        return _sc_run(self._ctx)

    def stop(self):
        _sc_stop(self._ctx)
        self.proxy.stop()
        self.vm_tunnel.kill_tunnel()
