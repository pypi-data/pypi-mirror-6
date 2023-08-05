import pickle
import random
from os import path
import socket
import subprocess
import sys
import time

from marathoner import MARATHONER_PORT


class MockMediatorSimple(object):
    def run(self):
        n = pickle.load(sys.stdin)
        pickle.dump(n+1, sys.stdout)
        sys.stdout.flush()

        n = pickle.load(sys.stdin)
        pickle.dump(n+1, sys.stderr)
        sys.stderr.flush()


class MockMediatorSock(object):
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', MARATHONER_PORT))
        socket_reader = sock.makefile('r')
        socket_writer = sock.makefile('w')

        n = pickle.load(socket_reader)
        pickle.dump(n+1, socket_writer)
        socket_writer.flush()

        socket_reader.close()
        socket_writer.close()
        sock.close()


def _subprocess(args):
    si = None
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
    return subprocess.Popen(
        args,
        shell=False,
        bufsize=1,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        universal_newlines=True,
        startupinfo=si)


def _test_communication(proc, pin, pout):
    n = random.randint(1, 100)
    print 'Sending %s...' % n
    assert proc.poll() is None
    pickle.dump(n, pin)
    pin.flush()
    m = pickle.load(pout)
    assert m == n+1


def test_mediator():
    print 'Running on platform', sys.platform, 'with python', sys.version
    # check mediator path
    mediator = __import__('marathoner.mediator', fromlist=['mediator']).__file__
    mediator = path.splitext(mediator)[0] + '.py'
    print 'Mediator location:', mediator

    # start simple mediator
    print 'Testing simple mediator'
    proc = _subprocess(['python', path.abspath(__file__), '-simple'])
    _test_communication(proc, proc.stdin, proc.stdout)
    _test_communication(proc, proc.stdin, proc.stderr)
    time.sleep(1.0)
    assert proc.poll() is not None
    print 'Simple mediator passed'

    # start socket mediator
    print 'Openning socket'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', MARATHONER_PORT))
    sock.listen(0)                        # IF IT FAILS, TRY CHANGING THIS TO: sock.listen(1)
    print 'Testing sock mediator'
    proc = _subprocess(['python', path.abspath(__file__), '-sock'])
    assert proc.poll() is None
    time.sleep(1.0)
    assert proc.poll() is None
    conn, addr = sock.accept()
    assert proc.poll() is None
    socket_reader = conn.makefile('r')
    socket_writer = conn.makefile('w')
    _test_communication(proc, socket_writer, socket_reader)
    time.sleep(1.0)
    assert proc.poll() is not None
    print 'Sock mediator passed'


if __name__ == '__main__':
    argv = sys.argv[1:]

    if not argv:
        test_mediator()
    elif argv[0] == '-simple':
        MockMediatorSimple().run()
    elif argv[0] == '-sock':
        MockMediatorSock().run()
