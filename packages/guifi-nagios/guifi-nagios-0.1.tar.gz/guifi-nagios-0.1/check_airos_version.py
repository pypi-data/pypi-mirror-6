#!/usr/bin/env python
"""
Nagios plugin: Check AirOS Firmware Version
"""
import nagiosplugin
import json
import argparse
import paramiko


class AirOSVersion(nagiosplugin.Resource):

    def __init__(self, host, username, password):
        super(AirOSVersion, self).__init__()
        self.host = host
        self.username = username
        self.password = password

    def probe(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(self.host, username=self.username, password=self.password)
            stdin, stdout, stderr = client.exec_command('/usr/www/status.cgi')
            json_data = stdout.read()[30:]  # firts characters are Content-Type header
            data = json.loads(json_data)
            value = data['host']['fwversion']
        except:
            value = None

        return [nagiosplugin.Metric('version', value)]


class VersionContext(nagiosplugin.Context):
    def __init__(self, name, warning=None, critical=None, fmt_metric=None,
                 result_cls=nagiosplugin.result.Result):

        super(VersionContext, self).__init__(name, fmt_metric, result_cls)
        self.warning = warning
        self.critical = critical

    def evaluate(self, metric, resource):
        if metric.value is None:
            return self.result_cls(nagiosplugin.state.Unknown, None, metric)
        if metric.value < self.critical:
            return self.result_cls(nagiosplugin.state.Critical, self.critical, metric)
        elif metric.value < self.warning:
            return self.result_cls(nagiosplugin.state.Warn, self.warning, metric)
        else:
            return self.result_cls(nagiosplugin.state.Ok, None, metric)


class VersionSummary(nagiosplugin.Summary):

    def verbose(self, results):
        version = results[0].metric.value
        if version is None:
            version = 'Unknown'
        return "Version is %s" % version


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-H', '--host', metavar='host', default='',
                      help='hostname or ip of the AirOS device')
    argp.add_argument('-u', '--username', metavar='username', default='',
                      help='user name on the AirOS device')
    argp.add_argument('-p', '--password', metavar='password', default='',
                      help='password on the AirOS device')
    argp.add_argument('-w', '--warning', metavar='value', default='',
                      help='return warning if version is lower than value')
    argp.add_argument('-c', '--critical', metavar='value', default='',
                      help='return critical if version is lower than value')
    argp.add_argument('-t', '--timeout', default=10,
                      help='abort execution after TIMEOUT seconds')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        AirOSVersion(host=args.host, username=args.username, password=args.password),
        VersionContext('version', args.warning, args.critical),
        VersionSummary(),
    )
    check.main(args.verbose, args.timeout)


if __name__ == '__main__':
    main()
