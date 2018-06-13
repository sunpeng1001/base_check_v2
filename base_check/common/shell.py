"""
Common function to run shell in python
"""
import subprocess
import os
import signal
from threading import Timer


class Shell(object):
    """
    Handles executing commands & recording output.
    """
    def __init__(self, command, timeout):
        self.exception = None
        self.killed = False
        # The os.setsid() is passed in the argument preexec_fn so
        # it's run after the fork() and before  exec() to run the shell.
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

        # Use timer to kill Popen if timeout.
        timer = Timer(timeout, self._kill)
        try:
            timer.start()
            stdout, stderr = self.proc.communicate()
            # remove trailing '\n' character
            self.stdout = stdout.rstrip('\n')
            self.stderr = stderr.rstrip('\n')
        except Exception, e:
            self.exception = e
        finally:
            timer.cancel()

    def _kill(self):
        # Send the signal to all the process groups
        os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
        self.killed = True

    @property
    def returncode(self):
        return self.proc.returncode

    def __bool__(self):
        return self.proc.returncode == os.EX_OK

    __nonzero__ = __bool__


def shell(command, timeout=3600):
    """
    A convenient shortcut for running commands.
    :param command: shell command to run
    :param timeout: max time the shell command can run
    :return: Shell object
    """
    return Shell(command, timeout)


if __name__ == '__main__':
    import logging
    LOG = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] '
                               '- %(levelname)s: %(message)s')

    # script = 'sleep 12 && echo 123'
    script = "find . -name '*.py' | xargs ls -l"
    sh = shell(script)
    if sh:
        LOG.info('"%s" execute success', script)
    LOG.info(sh.stdout)
    LOG.info(sh.stderr)
    LOG.info(sh.returncode)
