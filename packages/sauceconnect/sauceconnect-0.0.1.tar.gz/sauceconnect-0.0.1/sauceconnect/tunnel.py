import httplib
import json
import logging
import re
import socket
import time
import urllib2
from base64 import b64encode
from contextlib import closing
from functools import wraps


RETRY_REST_WAIT = 10  # seconds
RETRY_REST_MAX = 3
RETRY_PROVISION_MAX = 10
REST_POLL_WAIT = 1  # seconds

FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR) #DEBUG)


class DeleteRequest(urllib2.Request):
    def get_method(self):
        return "DELETE"


class HTTPResponseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "HTTP server responded with '%s' (expected 'OK')" % self.msg


class ShutdownRequestedError(Exception):
    pass


class TunnelMachineError(Exception):
    pass


class TunnelMachineProvisionError(TunnelMachineError):
    pass


class TunnelMachineBootError(TunnelMachineError):
    pass


class TunnelMachine(object):

    _host_search = re.compile("//([^/]+)").search

    def __init__(self, rest_url, user, password,
                 domains, ssh_port, boost_mode, use_ssh,
                 fast_fail_regexps, direct_domains, shared_tunnel,
                 squid_opts, metadata=None):
        self.user = user
        self.password = password
        self.domains = set(domains)
        self.ssh_port = ssh_port
        self.boost_mode = boost_mode
        self.use_ssh = use_ssh
        self.fast_fail_regexps = fast_fail_regexps
        self.direct_domains = direct_domains
        self.shared_tunnel = shared_tunnel
        self.squid_opts = squid_opts
        self.metadata = metadata or dict()

        self.reverse_ssh = None
        self.is_shutdown = False
        self.base_url = "%(rest_url)s/%(user)s/tunnels" % locals()
        self.rest_host = self._host_search(rest_url).group(1)
        self.basic_auth_header = {"Authorization": "Basic %s"
                                  % b64encode("%s:%s" % (user, password))}

        self._set_urlopen(user, password)

        for attempt in xrange(1, RETRY_PROVISION_MAX):
            try:
                self._provision_tunnel()
                break
            except TunnelMachineProvisionError, e:
                logger.warning(e)
                if attempt == RETRY_PROVISION_MAX:
                    raise TunnelMachineError(
                        "!! Could not provision tunnel remote VM. Please "
                        "contact help@saucelabs.com.")

    def _set_urlopen(self, user, password):
        # always send Basic Auth header (HTTPBasicAuthHandler was unreliable)
        opener = urllib2.build_opener()
        opener.addheaders = self.basic_auth_header.items()
        self.urlopen = opener.open

    # decorator
    def _retry_rest_api(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            previous_failed = False
            for attempt in xrange(1, RETRY_REST_MAX + 1):
                try:
                    result = f(*args, **kwargs)
                    if previous_failed:
                        logger.info("Connection succeeded")
                    return result
                except (HTTPResponseError,
                        urllib2.URLError, httplib.HTTPException,
                        socket.gaierror, socket.error), e:
                    logger.warning("Problem connecting to Sauce Labs REST API "
                                   "(%s)", str(e))
                    if attempt == RETRY_REST_MAX:
                        raise TunnelMachineError(
                            "Could not reach Sauce Labs REST API after %d "
                            "tries. Is your network down or firewalled?"
                            % attempt)
                    previous_failed = True
                    logger.debug("Retrying in %ds", RETRY_REST_WAIT)
                    time.sleep(RETRY_REST_WAIT)
                except Exception, e:
                    raise TunnelMachineError(
                        "An error occurred while contacting Sauce Labs REST "
                        "API (%s). Please contact help@saucelabs.com." %
                        str(e))
        return wrapper

    @_retry_rest_api
    def _get_doc(self, url_or_req):
        try:
            with closing(self.urlopen(url_or_req)) as resp:
                if resp.msg != "OK":
                    raise HTTPResponseError(resp.msg)
                return json.loads(resp.read())
        except Exception, ex:
            # Running under Jython, JavaException is raised instead of
            # HTTP Exceptions
            raise HTTPResponseError(unicode(ex))

    def kill_tunnel(self, tunnel_id=None):
        if tunnel_id is None:
            tunnel_id = self.id
        for attempt in xrange(1, 4):  # try a few times, then bail
            logger.debug(
                "Shutting down old tunnel remote VM: %s" % tunnel_id)
            url = "%s/%s" % (self.base_url, tunnel_id)
            doc = self._get_doc(DeleteRequest(url=url))
            if (not doc.get('result') or
                not doc.get('id') == tunnel_id):
                logger.warning("Old tunnel remote VM failed to shut "
                               "down.  Status: %s", doc)
                continue
            doc = self._get_doc(url)
            while doc.get('status') not in ["halting", "terminated"]:
                logger.debug(
                    "Waiting for old tunnel remote VM to start "
                    "halting")
                time.sleep(REST_POLL_WAIT)
                doc = self._get_doc(url)
            break

    def _provision_tunnel(self):
        # Shutdown any tunnel using a requested domain
        kill_list = set()
        for doc in self._get_doc(self.base_url + "?full=1"):
            if not doc.get('domain_names'):
                continue
            if set(doc['domain_names']) & self.domains:
                kill_list.add(doc['id'])
        if kill_list:
            logger.info("Shutting down other tunnel remote VMs using "
                        "requested domains")
            for tunnel_id in kill_list:
                self.kill_tunnel(tunnel_id)

        # Request a tunnel machine
        headers = {"Content-Type": "application/json"}
        data = json.dumps(dict(domain_names=list(self.domains),
                               metadata=self.metadata,
                               ssh_port=self.ssh_port,
                               use_caching_proxy=self.boost_mode,
                               use_kgp=not self.use_ssh,
                               fast_fail_regexps=(
                                   self.fast_fail_regexps.split(',') if
                                   self.fast_fail_regexps else None),
                               direct_domains=(
                                   self.direct_domains.split(',') if
                                   self.direct_domains else None),
                               shared_tunnel=self.shared_tunnel,
                               squid_config=(
                                   self.squid_opts.split(',') if
                                   self.squid_opts else None)))
        logger.info("%s" % data)
        req = urllib2.Request(url=self.base_url, headers=headers, data=data)
        doc = self._get_doc(req)
        if doc.get('error'):
            raise TunnelMachineProvisionError(doc['error'])
        for key in ['id']:
            if not doc.get(key):
                raise TunnelMachineProvisionError(
                    "Document for provisioned tunnel remote VM is missing "
                    "the key or value for '%s'" % key)
        self.id = doc['id']
        self.url = "%s/%s" % (self.base_url, self.id)
        logger.info("Tunnel remote VM is provisioned (%s)" % self.id)

    def ready_wait(self):
        """Wait for the machine to reach the 'running' state."""
        previous_status = None
        while True:
            doc = self._get_doc(self.url)
            status = doc.get('status')
            if status == "running":
                break
            if status in ["halting", "terminated"]:
                if doc.get('user_shut_down'):
                    raise ShutdownRequestedError("Tunnel shut down by user "
                                                 "(or another Sauce Connect "
                                                 "process), quitting")
                else:
                    raise TunnelMachineBootError("Tunnel remote VM was shut "
                                                 "down")
            if status != previous_status:
                logger.info("Tunnel remote VM is %s .." % status)
            previous_status = status
            time.sleep(REST_POLL_WAIT)
        self.host = doc['host']
        logger.info("Tunnel remote VM is running at %s" % self.host)

    def shutdown(self):
        if self.is_shutdown:
            return

        if self.reverse_ssh:
            self.reverse_ssh.stop()

        logger.info("Shutting down tunnel remote VM (please wait)")
        logger.debug("tunnel remote VM ID: %s" % self.id)

        try:
            doc = self._get_doc(DeleteRequest(url=self.url))
        except TunnelMachineError, e:
            logger.warning("Unable to shut down tunnel remote VM")
            logger.debug("Shut down failed because: %s", str(e))
            self.is_shutdown = True  # fuhgeddaboudit
            return
        #assert doc.get('ok')
        assert doc.get('id') == self.id

        previous_status = None
        while True:
            doc = self._get_doc(self.url)
            status = doc.get('status')
            if status == "terminated":
                break
            if status != previous_status:
                logger.info("Tunnel remote VM is %s .." % status)
            previous_status = status
            time.sleep(REST_POLL_WAIT)
        logger.info("Finished shutting down tunnel remote VM")
        self.is_shutdown = True

    # Make us usable with contextlib.closing
    close = shutdown

    def check_running(self):
        doc = self._get_doc(self.url)
        if doc.get('status') == "running":
            return
        raise TunnelMachineError(
            "The tunnel remote VM is no longer running. It may have been "
            "shutdown via the website or by another Sauce Connect script "
            "requesting these domains: %s" % list(self.domains))
