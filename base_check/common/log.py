import logging
import logging.handlers
import sys
import socket
import fcntl
import struct
import errno

_AUDIT = logging.INFO + 1
_TRACE = 5
_loggers = {}
logging.addLevelName(_TRACE, 'TRACE')
logging.Logger.trace = \
    lambda inst, msg, *args, **kwargs: inst.log(_TRACE, msg, *args, **kwargs)


class ColorHandler(logging.StreamHandler):
    LEVEL_COLORS = {
        _TRACE: '\033[00;35m',  # MAGENTA
        logging.DEBUG: '\033[00;32m',  # GREEN
        logging.INFO: '\033[00;36m',  # CYAN
        _AUDIT: '\033[01;36m',  # BOLD CYAN
        logging.WARN: '\033[01;33m',  # BOLD YELLOW
        logging.ERROR: '\033[01;31m',  # BOLD RED
        logging.CRITICAL: '\033[01;31m',  # BOLD RED
    }

    def format(self, record):
        record.color = self.LEVEL_COLORS[record.levelno]
        return logging.StreamHandler.format(self, record)


def getLogger(name=None):
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifaddr = None
    try:
        ifaddr = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError as e:
        if e.errno == errno.ENODEV:
            ifaddr = None
        else:
            raise e
    return ifaddr


def setup(conf):
    log_root = getLogger(None)

    # Remove all handlers
    for handler in list(log_root.handlers):
        log_root.removeHandler(handler)

    log_root.setLevel(_TRACE)
    ifaddr = None
    if hasattr(conf, 'ifname') and conf.ifname is not None:
        ifaddr = get_ip_address(conf.ifname)

    # log to file and standard output
    # file handler's log-level cat be set by config file
    # standard output handler's log-level is fixed to INFO.WARN
    if conf.log_file:
        filelog = logging.handlers.WatchedFileHandler(conf.log_file)
        fmt = '%(asctime)s %(filename)s:%(lineno)s:%(funcName)s' \
              ' - %(levelname)s - %(message)s'
        if ifaddr is not None:
            fmt = '%s: %s' % (ifaddr, fmt)
        formatter = logging.Formatter(fmt)
        filelog.setFormatter(formatter)
        filelog.setLevel(logging.getLevelName(conf.log_file_level))
        log_root.addHandler(filelog)

    streamlog = logging.StreamHandler(sys.stdout)
    fmt = '%(message)s'
    # set log formatter
    formatter = logging.Formatter(fmt)
    streamlog.setFormatter(formatter)
    # set log level
    streamlog.setLevel(logging.getLevelName(conf.log_stdout_level))
    log_root.addHandler(streamlog)


if __name__ == '__main__':
    from cfg import CONF
    CONF(sys.argv[1:])
    setup(CONF)
    LOG = getLogger('test')
    LOG.trace('trace message')
    LOG.debug('debug message')
    LOG.info('info message')
    LOG.warn('warn message')
    LOG.error('error message')
