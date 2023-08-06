
import re
import os


def collect_servers(service, port, protocol='tcp', separate=True):
    servers = []
    for var in os.environ.keys():
        php_var_rx = re.compile('^%s_(\d+)_PORT_%s_%s$' % (service.upper(), port.upper(), protocol.upper()))
        m = re.match(php_var_rx, var)
        if m:
            host = os.environ.get('%s_%s_PORT_%s_%s_ADDR' % (service.upper(), m.group(1), port.upper(), protocol.upper()))
            port = os.environ.get('%s_%s_PORT_%s_%s_PORT' % (service.upper(), m.group(1), port.upper(), protocol.upper()))

            if separate:
                servers.append({
                    'host': host,
                    'port': port
                })
            else:
                servers.append('%s:%s' % (host, port))
    return servers
