"""
Mosaik API for simulations written in Python.

"""
import inspect
import logging
import re
import socket
import sys
import traceback

from simpy._compat import PY2
from simpy.io import select as backend
from simpy.io.packet import PacketUTF8 as Packet
from simpy.io.message import Message
import docopt


if PY2:
    ConnectionError = socket.error
    ConnectionRefusedError = socket.error


__version__ = '2.0a1'
logger = logging.getLogger('mosaik_api')

_HELP = """%(desc)s

Usage:
    %(prog)s [options] HOST:PORT

Options:
    HOST:PORT   Connect to this address
    -l LEVEL, --log-level LEVEL
                Log level for simulator (%(levels)s) [default: info]
%(extra_opts)s
"""
_LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


# NOTE: We don't use an ABC here, because the effort of making it py2 AND py3
# compatible (-> meta classes) outweighs the benefits.
class Simulator(object):
    """This is the high-level mosaik API for simulations."""
    def __init__(self, meta):
        self.meta = {
            'api_version': __version__,
            'models': {},
        }
        """Meta data describing the simulator.

        The *api_version* is the version string of the API implementation.

        *models* is a dictionary describing the models provided by this
        simulator::

            'ModelName': {
                'public': True|False,
                'params': ['param_1', ...],
                'attrs': ['attr_1', ...],
            }

        The entry *public* determines whether a model can be instantiated by
        a user (``True``) or if it is a sub-model that cannot be created
        directly (``False``). *params* is a list of parameter names that can
        be passed to the model when creating it. *attrs* is a list of attribute
        names that can be accessed (reading or writing).

        """

        self.meta.update(meta)
        self.mosaik = None  # Will be an RPC proxy to mosaik

    def configure(self, args, backend, env):
        """This method can be overridden to configure the simulation with the
        command line *args* as created by :func:`~docopt.docopt()`.

        *backend* and *env* are the *simpy.io* backend and environment used
        for networking. You can use them to start extra processes (e.g., a
        web server).

        The default implementation simply ignores them.

        """
        pass

    def finalize(self):
        """This method can be overridden to do some clean-up operations after
        the simulation finished (e.g., shutting down external processes)

        """
        pass

    def init(self, *args, **kwargs):
        """Initialize the simulator and apply additional parameters sent by
        mosaik. Return the meta data :attr:`meta`.

        """
        return self.meta

    def create(self, num, model, model_params):
        """Create *num* instances of *model* using the provided *model_params*

        *num* is an integer for the number of model instances to create.

        *model* needs to be a public entry in the simulator's
        ``meta['models']``.

        *model_params* is a dictionary mapping parameters (from
        ``meta['models'][model]['params']``) to their values.

        Return a list of dictionaries describing the created model instances
        (entities)::

            [
                {
                    'eid': 'eid_1',
                    'type': 'model_name',
                    'rel': ['eid_2', ...],
                },
                ...
            ]

        The entity ID (*eid*) must be unique within a simulator instance. The
        entity's type is usually the same as the original model_name but may
        also be something different. *rel* is a list of related entities.

        """
        raise NotImplementedError

    def step(self, time, inputs):
        """Perform the next simulation step from time *time* using input values
        from *inputs* and return the new simulation time.

        *time* and the time retuned are integers. Their unit is *seconds* (from
        simulation start).

        *inputs* is a dict of dict mapping entity IDs to attributes and
        lists of values (each simulator has do decide on its own how to reduce
        that list (e.g., as its sum, average or maximum)::

            {
                'eid_1: {
                    'attr_1': ['val_1_1', ...],
                    'attr_2': ['val_2_1', ...],
                    ...
                },
                ...
            }

        """
        raise NotImplementedError

    def get_data(self, outputs):
        """Return the data for the requested attributes in *outputs*

        *outputs* is a dict mapping entity IDs to lists of attribute names for
        whose values are requested::

            {
                'eid_1': ['attr_1', 'attr_2', ...],
                ...
            }

        The return value needs to be a dict of dicts mapping entity IDs and
        attribute names to their values::

            {
                'eid_1: {
                    'attr_1': 'val_1',
                    'attr_2': 'val_2',
                    ...
                },
                ...
            }

        """
        raise NotImplementedError


class MosaikProxy(object):
    exposed_meths = [
        'get_progress',
        'get_related_entities',
        'get_data',
    ]

    def __init__(self, channel):
        self._channel = channel

    def __getattr__(self, name):
        if name not in MosaikProxy.exposed_meths:
            raise AttributeError

        def proxy_call(*args, **kwargs):
            return self._channel.send([name, args, kwargs])

        return proxy_call


def start_simulation(simulator, description='', extra_options=None):
    """Start the simulation process for ``simulation``.

    *simulation* is the instance of your API implementation (see
    :class:`Simulation`).

    *description* may override the default description printed with the help on
    the command line.

    *extra_option* may be a list of options for :func:`docopt.docopt` (example:
    ``['-e, --example     Enable example mode']``). Commandline arguments are
    passed to :meth:`Simulation.configure()` so that your API implementation
    can handle them.

    """
    OK, ERR = 0, 1

    args = _parse_args(description or 'Start the simulation service.',
                       extra_options or [])

    logging.basicConfig(level=args['--log-level'])
    sim_name = simulator.__class__.__name__

    try:
        logger.info('Starting %s ...' % sim_name)
        env = backend.Environment()
        simulator.configure(args, backend, env)

        # Setup simpy.io and start the event loop.
        addr = _parse_addr(args['HOST:PORT'])
        sock = backend.TCPSocket.connection(env, addr)
        sock = Message(env, Packet(sock, max_packet_size=1024*1024))
        simulator.mosaik = MosaikProxy(sock)
        proc = env.process(run(sock, simulator))
        env.run(until=proc)
    except ConnectionRefusedError:
        logger.error('Could not connect to mosaik.')
        return ERR
    except (ConnectionError, KeyboardInterrupt):
        pass  # Exit silently.
    except Exception as exc:
        if type(exc) is OSError and exc.errno == 10057:
            # ConnectionRefusedError in Windows O.o
            logger.error('Could not connect to mosaik.')
            return ERR

        print('Error in %s:' % sim_name)
        import simpy._compat as compat
        if compat.PY2:
            compat.print_chain(type(exc), exc, exc.__traceback__)
        else:
            traceback.print_exc()  # Exit loudly
        print('---------%s-' % ('-' * len(sim_name)))
        return ERR
    finally:
        sock.close()
        simulator.finalize()

    return OK


def run(channel, sim):
    """Main simulator process. Send a greating message to mosaik and wait
    for requests to step the simulation, get data or whatever.

    *channel* is a :class:`simpy.io.message.Message` instance.

    *sim* is the instance of an :class:`Simulator` implementation.

    """
    funcs = {
        'init': sim.init,
        'create': sim.create,
        'step': sim.step,
        'get_data': sim.get_data,
    }
    for name, func in funcs.items():
        funcs[name] = get_wrapper(func, channel.env)

    logger.debug('Entering event loop ...')
    while True:
        request = yield channel.recv()
        func, args, kwargs = request.content
        logger.debug('Calling %s(*%s, **%s)' % (func, args, kwargs))
        if func == 'stop':
            break

        func = funcs[func]
        ret = yield func(*args, **kwargs)
        request.succeed(ret)


def get_wrapper(func, env):
    if inspect.isgeneratorfunction(func):
        def wrapper(*args, **kwargs):
            return env.process(func(*args, **kwargs))
    else:
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            return env.event().succeed(ret)
    return wrapper


def _parse_args(desc, extra_options):
    """Fill-in the values into :data:`_HELP` and parse and return the arguments
    using :func:`~docopt.docopt()`.

    """
    log_levels = (l[0] for l in sorted(_LOG_LEVELS.items(),
                                       key=lambda l: l[1]))
    msg = _HELP % {
        'desc': desc,
        'prog': sys.argv[0],
        'levels': ', '.join(log_levels),
        'extra_opts': '\n'.join('    %s' % opt
                                for opt in extra_options),
    }
    args = docopt.docopt(msg)
    args['--log-level'] = _LOG_LEVELS[args['--log-level']]
    return args


def _parse_addr(addr):
    """Parse ``addr`` and returns a ``('host', port)`` tuple.

    If the host does not look like an IP(v4) address, resolve its name
    to an IP address.

    Raise a :exc:`ValueError` if resolving the hostname fails or if the
    address contains no host or port.

    """
    try:
        host, port = addr.strip().split(':')
        # Resolve hostname if it doesn't look like an IP address
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', host):
            host = socket.gethostbyname(host)
        addr = (host, int(port))
        return addr

    except (ValueError):
        raise ValueError('Error parsing "%s"' % addr)

    except (IOError, OSError):
        raise ValueError('Could not resolve "%s"' % addr[0])
