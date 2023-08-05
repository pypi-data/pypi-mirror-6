from tunnel import TunnelMachine


REST_BASE_URL = "https://saucelabs.com/rest/v1/"
DEFAULT_KGP_PORT = 12345


def create_vm(username, password, domains=None, port=DEFAULT_KGP_PORT,
              boost_mode=False, fast_fail_regexps=None, direct_domains=None,
              shared_tunnel=False, squid_opts=None, metadata=None):

    _domains = domains or ["sauce-connect.proxy"]
    print "Domain is %s" % _domains

    # rest_url, user, password, domains, ssh_port, boost_mode, use_ssh,
    # fast_fail_regexps, direct_domains, shared_tunnel, squid_opts, metadata
    tunnel = TunnelMachine(REST_BASE_URL, username, password, _domains, port,
                           boost_mode, fast_fail_regexps, direct_domains,
                           shared_tunnel, squid_opts, metadata)
    tunnel.ready_wait()
    return tunnel
