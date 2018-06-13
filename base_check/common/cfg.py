import argparse


def _build_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-file', metavar='PATH',
                        default='/tmp/base_check/base_check.log',
                        help='(Optional) Name of log file '
                             'to send logging output to.')
    levels = ['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR']
    parser.add_argument('--log-file-level', metavar='LEVEL',
                        default='DEBUG',
                        choices=levels,
                        help='log level, default DEBUG')
    parser.add_argument('--log-stdout-level', metavar='LEVEL',
                        default='INFO',
                        choices=levels,
                        help='log level, default INFO')
    parser.add_argument('--ifname', metavar='NAME',
                        help='Interface name to get ip address which'
                             ' used to format logging')
    return parser


class Config(object):
    def __init__(self):
        self._parser = _build_argparse()

    def __call__(self, args=None, **kwargs):
        _args = self._parser.parse_args(args)
        self.log_file = _args.log_file
        self.log_file_level = _args.log_file_level
        self.log_stdout_level = _args.log_stdout_level
        self.ifname = _args.ifname


CONF = Config()

if __name__ == '__main__':
    CONF()
    print(CONF.log_file)
    print(CONF.log_level)
