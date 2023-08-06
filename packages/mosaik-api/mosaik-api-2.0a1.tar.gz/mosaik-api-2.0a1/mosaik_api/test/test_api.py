import multiprocessing
import sys

from simpy.io import select as backend
from simpy.io.packet import PacketUTF8 as Packet
from simpy.io.message import Message
import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from example_sim.mosaik import ExampleSim, main as examplesim_main
import mosaik_api


if mosaik_api.PY2:
    import socket
    ConnectionError = socket.error


def test_api():
    api = mosaik_api.Simulator({'models': {'spam': {}}})
    assert api.meta == {
        'api_version': mosaik_api.__version__,
        'models': {'spam': {}},
    }
    assert api.init() == api.meta
    pytest.raises(NotImplementedError, api.create, None, None, None)
    pytest.raises(NotImplementedError, api.step, None, None)
    pytest.raises(NotImplementedError, api.get_data, None)


@pytest.mark.parametrize('error', [True, False])
def test_start_simulation(error):
    env = backend.Environment()

    def mosaik(env):
        sim = ExampleSim()
        try:
            srv_sock = backend.TCPSocket.server(env, ('127.0.0.1', 5555))
            proc = multiprocessing.Process(target=examplesim_main)
            proc.start()

            # Test receiving the welcome message:
            sock = yield srv_sock.accept()
            channel = Message(env, Packet(sock))
            ret = yield channel.send(['init', [], {}])
            assert ret == sim.meta

            if not error:
                # Test sending a command:
                ret = yield channel.send(['step', [0, {}], {}])
                assert ret == 1
            else:
                # Force an error:
                with pytest.raises(ConnectionError):
                    yield channel.send(['foo', [], {}])

        finally:
            srv_sock.close()
            channel.close()
            proc.join()

    with mock.patch.object(sys, 'argv', ['test', '-l', 'debug',
                                         '127.0.0.1:5555']):
        mosaik = env.process(mosaik(env))
        env.run(until=mosaik)


@pytest.mark.parametrize('args', [
    [''],  # No arguments passed
    ['', 'spam'],  # Wrong address format
])
def test_start_simulation_arg_errors(args):
    """Wrong parameters passed on the command line."""
    sim = ExampleSim()
    pytest.raises(SystemExit, mosaik_api.start_simulation, sim)


def test_start_simulation_connection_refused(capsys):
    with mock.patch.object(sys, 'argv', ['test', '127.0.0.1:5555']):
        examplesim_main()
    out, err = capsys.readouterr()
    assert not out
    assert err == ('INFO:mosaik_api:Starting ExampleSim ...\n'
                   'ERROR:mosaik_api:Could not connect to mosaik.\n')


def test_parse_args():
    argv = ['spam', '-l',  'debug', '--bar', 'eggs', 'localhost:1234']
    desc = 'Spam and eggs'
    extra_options = [
        '--foo       Enable foo',
        '--bar BAR   The bar parameter',
    ]
    with mock.patch.object(sys, 'argv', argv):
        args = mosaik_api._parse_args(desc, extra_options)
        assert args == {
            'HOST:PORT': 'localhost:1234',
            '--log-level': 10,
            '--foo': False,
            '--bar': 'eggs',
        }


def test_parse_args_help(capsys):
    argv = ['spam', '--help']
    desc = 'Spam and eggs'
    extra_options = [
        '--foo       Enable foo',
        '--bar BAR   The bar parameter',
    ]
    with mock.patch.object(sys, 'argv', argv):
        with pytest.raises(SystemExit):
            mosaik_api._parse_args(desc, extra_options)

        out, err = capsys.readouterr()
        print(out)
        assert out == (
            'Spam and eggs\n'
            '\n'
            'Usage:\n'
            '    spam [options] HOST:PORT\n'
            '\n'
            'Options:\n'
            '    HOST:PORT   Connect to this address\n'
            '    -l LEVEL, --log-level LEVEL\n'
            '                Log level for simulator (debug, info, warning, error, critical) [default: info]\n'  # NOQA
            '    --foo       Enable foo\n'
            '    --bar BAR   The bar parameter\n'
        )
        assert err == ''


@pytest.mark.parametrize(('addr', 'expected'), [
    ('127.0.0.1:1234', ('127.0.0.1', 1234)),
    ('localhost:1234', ('127.0.0.1', 1234)),
    ('localhost:1234\r\n', ('127.0.0.1', 1234)),
    ('localhost', ValueError),
    ('127.0.0.1', ValueError),
    ('foobar:1234', ValueError),
])
def test_parse_addr(addr, expected):
    if isinstance(expected, tuple):
        ret = mosaik_api._parse_addr(addr)
        assert ret == expected
    else:
        pytest.raises(expected, mosaik_api._parse_addr, addr)
