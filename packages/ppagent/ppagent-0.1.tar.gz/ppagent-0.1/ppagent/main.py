import socket
import json
import argparse
import os
import logging
import sys
import collections
import time
import traceback

from string import Template
from os.path import expanduser


def excepthook(type, value, tb):
    print 'Unhandled exception'
    print 'Type:', type
    print 'Value:', value
    traceback.print_tb(tb)
sys.excepthook = excepthook

logger = logging.getLogger("ppagent")
config_home = expanduser("~/.ppagent/")

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

default_config = '''[
    {"miner":
        {
            "type": "CGMiner"
        }
    }
]'''


class WorkerNotFound(Exception):
    pass


miner_defaults = {
    'CGMiner': {
        'port': 4028,
        'address': '127.0.0.1',
        'collectors': {
            'status': {
                'enabled': True,
                'temperature': True,
                'mhps': True,
                'interval': 60
            },
            'temp': {
                'enabled': True,
                'interval': 60
            },
            'hashrate': {
                'enabled': True,
                'interval': 60
            }
        }
    }
}


class Miner(object):
    """ Represents one mining client. Currently only implementation is CGMiner,
    but in the future other miners could be interfaced with. """

    def __init__(self):
        """ Recieves a dictionary of arguments defined in the miner declaration
        """
        raise NotImplementedError

    def collect(self):
        """ Called at regular intervals to collect information. Should return a
        list of dictionaries that get passed serialized to pass to the
        powerpool collector. Should manage it's only scheduling. """
        raise NotImplementedError


class CGMiner(Miner):
    keys = ['temps', 'hashrates']
    valid_collectors = ['status']

    def __init__(self, collectors, remotes, port=4028, address='127.0.0.1'):
        self.port = port
        self.remotes = remotes
        self.address = address
        # filter our disabled collectors
        self.collectors = dict((k, v) for (k, v) in collectors.items()
                               if v.get('enabled', False))

        self._worker = None
        self.queue = []
        self.authenticated = False
        self.last_devs = []

    def test(self):
        pass

    def reset_timers(self):
        now = int(time.time())
        for coll in self.collectors.values():
            interval = coll['interval']
            coll['next_run'] = ((now // interval) * interval)

    @property
    def worker(self):
        if self._worker is None:
            self._worker = self.fetch_username()
        return self._worker

    def collect(self):
        # trim queue to keep it from growing infinitely while disconnected
        self.queue = self.queue[:10]

        now = int(time.time())
        # if it's time to run, and we have status defined
        if ('status' in self.collectors or
                'temp' in self.collectors or
                'hashrate' in self.collectors):
            ret = self.call_devs()
            mhs, temps = ret

        if 'status' in self.collectors and now >= self.collectors['status']['next_run']:
            conf = self.collectors['status']
            gpus = [{} for _ in temps]
            output = {"type": "cgminer", "gpus": gpus}
            # if it failed to connect we should just skip collection
            if ret is None:
                return
            if conf['temperature']:
                for i, temp in enumerate(temps):
                    output['gpus'][i]['temp'] = temp
            if conf['mhps']:
                for i, mh in enumerate(mhs):
                    output['gpus'][i]['hash'] = mh
            self.queue.append([self.worker, 'status', output, now])

            # set the next time it should run
            conf['next_run'] += conf['interval']

        if 'temp' in self.collectors and now >= self.collectors['temp']['next_run']:
            conf = self.collectors['temp']
            self.queue.append([self.worker, 'temp', temps, now])

            # set the next time it should run
            conf['next_run'] += conf['interval']

        if (mhs and 'hashrate' in self.collectors and
                now >= self.collectors['hashrate']['next_run']):
            conf = self.collectors['hashrate']
            self.queue.append([self.worker, 'hashrate', mhs, now])

            # set the next time it should run
            conf['next_run'] += conf['interval']

    def call(self, command, params=None):
        sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sok.connect((self.address, self.port))
        try:
            sok.send('{"command":"' + command + '"}')
            data = sok.makefile().readline()[:-1]
            retval = json.loads(data)
        except socket.error:
            self._worker = None
            self.authenticated = False
            return None
        finally:
            sok.close()
        return retval

    def fetch_username(self):
        data = self.call('pools')
        for pool in data['POOLS']:
            if pool['Stratum URL'] in self.remotes:
                return pool['User']
        raise WorkerNotFound("Unable to find worker in pool connections")

    def call_devs(self):
        """ Retrieves and parses device information from cgminer """
        data = self.call('devs')
        if 'DEVS' not in data:
            raise Exception()

        temps = [d.get('Temperature') for d in data['DEVS']]
        # we store the last total megahashes internally and report the
        # difference since last run, as opposed to reporting cgminers avg
        # megahash or 5s megahash
        if self.last_devs and len(self.last_devs) == len(data['DEVS']):
            mhs = [round(now['Total MH'] - last['Total MH'], 3)
                   for now, last in zip(data['DEVS'], self.last_devs)]
        else:
            mhs = []
        self.last_devs = data['DEVS']
        return mhs, temps


class AgentSender(object):
    """ Managed interfacing with PowerPool server for relaying information """
    def __init__(self, miners, address='127.0.0.1', port=4444):
        self.address = address
        self.port = port
        self.miners = miners
        self.conn = None

    def connect(self):
        logger.debug("Opening connection to agent server; addr: {0}; port: {1}"
                     .format(self.address, self.port))
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.address, self.port))
        self.conn = conn.makefile()
        logger.debug("Announcing hello message")
        self.conn.write(json.dumps({'method': 'hello', 'params': [0.1]}) + "\n")
        self.conn.flush()

    def reset_connection(self):
        logger.info("Disconnected from remote.")
        self.conn = None
        # reauth required upon connection error
        for miner in self.miners:
            miner.authenticated = False

    def send(self, data):
        logger.debug("Sending {0} to server".format(data))
        try:
            if self.conn is None:
                self.connect()
            self.conn.write(json.dumps(data) + "\n")
            self.conn.flush()
        except (socket.error, Exception):
            self.reset_connection()
            raise

    def recieve(self):
        if self.conn is None:
            return {}

        recv = self.conn.readline(4096)
        if len(recv) > 4000:
            raise Exception("Server returned too large of a string")
        logger.debug("Recieved response from server {0}".format(recv.strip()))
        if not recv:
            self.reset_connection()
            return {}
        return json.loads(recv)

    def loop(self):
        try:
            while True:
                self.transmit()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Shutting down daemon from sigint...")

    def transmit(self):
        # accumulate values to send
        for miner in self.miners:
            if miner.authenticated is False:
                try:
                    username = miner.worker
                except WorkerNotFound:
                    logger.info("Miner not connected to valid pool")
                    continue
                except Exception:
                    logger.info("Unable to connect to miner")
                    continue

                logger.debug("Attempting to authenticate {0}".format(username))
                data = {'method': 'worker.authenticate',
                        'params': [username, ]}
                try:
                    self.send(data)
                except Exception:
                    logger.debug("Failed to communicate with server")
                    time.sleep(5)
                    continue

                retval = self.recieve()
                if retval['error'] is None:
                    logger.info("Successfully authenticated {0}".format(username))
                    miner.authenticated = True
                    miner.reset_timers()
                else:
                    logger.debug(
                        "Failed to authenticate worker {0}, server returned {1}."
                        .format(username, retval))

            if miner.authenticated is True:
                miner.collect()
            else:
                # don't distribute if we're not authenticated...
                continue

            # send all our values that were accumulated
            remaining = []
            for value in miner.queue:
                try:
                    send = {'method': 'stats.submit', 'params': value}
                    logger.info("Transmiting new stats: {0}".format(send))
                    self.send(send)
                except Exception:
                    logger.warn(
                        "Unable to send to remote, probably down temporarily.")
                    time.sleep(5)
                else:
                    # try to get a response from the server. if we fail to
                    # recieve, just wait till next loop to send
                    ret = self.recieve()
                    if ret is None or ret.get('error', True) is not None:
                        logger.warn("Recieved failure result from the server!")
                        remaining.append(value)
            miner.queue[:] = remaining


def install(configs):
    if os.geteuid() != 0:
        print("Please run as root to install...")
        exit(0)

    # where are we running from right now?
    script_path = os.path.realpath(__file__).replace('pyc', 'py')
    print("Detected script in path " + script_path)
    # chroot folder
    script_dir = os.path.join(os.path.split(script_path)[:-1])[0]
    # now build an executable path
    exec_path = "{0} {1}".format(sys.executable, script_path)
    print("Configuring executable path" + script_dir)
    setup_folders('/etc/ppagent/')

    import subprocess
    if configs['type'] == 'upstart':
        upstart = open(os.path.join(script_dir, 'install/upstart.conf')).read().format(exec_path=exec_path, chdir=script_dir)

        path = '/etc/init/ppagent.conf'
        flo = open(path, 'w')
        flo.write(upstart)
        flo.close()
        os.chmod(path, 0644)

        try:
            output = subprocess.check_output('useradd ppagent', shell=True)
        except Exception as e:
            if e.returncode == 9:
                pass
        print("Added ppagent user to run daemon under")

        output = subprocess.check_output('service ppagent start', shell=True)
        print output.strip()
        if 'start' in output:
            print("Started ppagent service!")
    elif configs['type'] == 'sysv':
        sysv = open(os.path.join(script_dir, 'install/initd')).read()
        sysv = Template(sysv).safe_substitute(exec_path=exec_path)

        path = '/etc/init.d/ppagent'
        flo = open(path, 'w')
        flo.write(sysv)
        flo.close()
        os.chmod(path, 0751)
        subprocess.call('/etc/init.d/ppagent start', shell=True)
        subprocess.call('update-rc.d ppagent defaults', shell=True)


def setup_folders(config_home):
    try:
        os.makedirs(config_home, 0751)
        print("Config folder created")
    except OSError as e:
        if e.errno != 17:
            print("Failed to create configuration directory")
            exit(1)
        print("Config directory already created")

    with open(config_home + "config.json", 'w') as f:
        f.write(default_config)
        print("Wrote the default configuration file")


def entry():
    parser = argparse.ArgumentParser(prog='ppagent')
    parser.add_argument('-l',
                        '--log-level',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                        default='INFO')
    parser.add_argument('-a',
                        '--address',
                        default='stratum.simpledoge.com')
    parser.add_argument('-c',
                        '--config',
                        default=os.path.join(config_home, 'ppagent.json'))
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=4444)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    subparsers = parser.add_subparsers(title='main subcommands', dest='action')

    subparsers.add_parser('run', help='start the daemon')
    inst = subparsers.add_parser('install', help='install the upstart script and add user')
    inst.add_argument('type', choices=['upstart', 'sysv'],
                      help='upstart for ubuntu, sysv for debian.')
    args = parser.parse_args()
    configs = vars(args)

    if configs['action'] == 'install':
        try:
            install(configs)
        except Exception:
            print("Installation failed because of an unhandled exception:")
            raise
        exit(0)

    # rely on command line log level until we get all configs parsed
    ch.setLevel(getattr(logging, args.log_level))
    logger.setLevel(getattr(logging, args.log_level))

    # setup or load our configuration file
    try:
        file_configs = json.load(open(configs['config']))
        logger.debug("Loaded JSON config file from {0}".format(configs['config']))
    except (IOError, OSError):
        logger.error("JSON configuration file {0} couldn't be loaded, no miners configured, exiting..."
                     .format(configs['config']), exc_info=True)
        exit(1)

    # setup our collected configs by recursively overriding
    def update(d, u):
        """ Simple recursive dictionary update """
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    # do some processing on the config file
    miners = []
    for section in file_configs:
        title = section.keys()[0]
        content = section.values()[0]
        # process a miner directive
        if title == "miner":
            typ = content.pop('type', 'CGMiner')
            kwargs = {}
            # apply defaults, followed by overriding with config options
            update(kwargs, miner_defaults[typ])
            update(kwargs, content)
            kwargs['remotes'] = [configs['address']]
            # init the miner class with the configs
            miners.append(globals()[typ](**kwargs))
        elif title == "daemon":
            configs.update(content)

    # set our logging level based on the configs
    ch.setLevel(getattr(logging, configs['log_level']))
    logger.setLevel(getattr(logging, configs['log_level']))
    logger.debug(configs)

    sender = AgentSender(miners, configs['address'], configs['port'])
    sender.loop()

if __name__ == "__main__":
    entry()
