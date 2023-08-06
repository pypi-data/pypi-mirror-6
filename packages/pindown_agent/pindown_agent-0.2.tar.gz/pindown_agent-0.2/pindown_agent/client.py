# #!/usr/bin/python
import requests
from keyczar.keys import AesKey
import tornado.ioloop
import tornado.iostream
import socket
import json
import sys
import subprocess
import time
import logging
import base64
import uuid
import argparse
import os
import ConfigParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',)


class Connection(object):

    def __init__(self, stream, base_dir, config, hostid, identifier):
        self.stream = stream
        shared_key_path = os.path.join(base_dir, 'shared.key')
        self.shared_key = open(shared_key_path).read().strip()
        decodedkey = base64.b64decode(self.shared_key)
        self.key = AesKey.Read(decodedkey)
        self.stream.set_close_callback(self.on_close)
        self.hostid = hostid
        self.projects = config.sections()
        self.identifier = identifier

    def on_close(self):
        '''
        connection closed, reconnect or die ??
        we die, upstart or supervisor or whatever should restart us
        '''
        print "connection closed, exiting"
        tornado.ioloop.IOLoop.instance().stop()
        sys.exit(10)

    def heartbeat(self):
        self.stream.write(self.wrap_data(json.dumps({'cmd':'heartbeat'})))

    def wrap_data(self, data):
        data = self.key.Encrypt(data)
        return "$%s\r\n%s\r\n" % (len(data), data)

    def send_request(self):
        logger.debug("connecting...")
        self.stream.write("project_ids:%s\r\n" % ','.join(self.projects) )
        client_data = dict(
            project_ids = ','.join(self.projects),
            host = self.hostid,
            identifier = self.identifier,
            cmd = "identify"
        )
        self.stream.write(self.wrap_data(json.dumps(client_data)))
        self.stream.read_until(b"\r\n", self.on_data)

    def on_data(self, data):
        if data == "\r\n" or not data:
            self.stream.read_until(b"\r\n", self.on_data)
            return
        if data[0] == '$':
            length = int(data[1:-2])
            self.stream.read_bytes(length, self.on_message)
        else:
            print "wrong data"

    def cmd_deploy(self, payload):
        logger.info("running deploy %s", payload)
        env = os.environ.copy()
        env['DEPLOY_ID'] = str(payload.get('deploy_id'))
        env['DEPLOY_PROJECT_NAME'] = str(payload.get('project_name'))
        env['DEPLOY_PROJECT_PATH'] = str(payload.get('project_home'))
        env['DEPLOY_BRANCH'] = str(payload.get('branch'))
        lines = []
        p = subprocess.Popen(payload['deploy_script'], shell=True,
                             stdout=subprocess.PIPE,
                             env=env,
                             stderr=subprocess.STDOUT)
        line_id = 0
        while p.poll() == None:
            line = p.stdout.readline()
            print line
            logger.info(line)
            if line:
                line_id += 1
                ret = dict(line=line,
                            identifier=self.identifier,
                            cmd='deploy_result',
                            deploy_id=payload['deploy_id'],
                            line_id=line_id,
                            ts=time.time())
                self.stream.write(self.wrap_data(json.dumps(ret)))
        retval = p.wait()
        return {'result': 'OK+', 'retval': retval,
                'cmd': 'deploy_finish',
                'ts': time.time(),
                'deploy_id': payload['deploy_id'],
                'output': lines}

    def dispatch_message(self, payload):
        cmds = {
            'deploy': self.cmd_deploy
        }
        try:
            fn = cmds[payload['cmd']]
            return fn(payload)
        except KeyError as e:
            print payload['cmd'], e
            return {'result': 'unknown command'}

    def on_message(self, message):
        message = self.key.Decrypt(message)
        logger.debug("received message [%s]", message)
        try:
            payload = json.loads(message)
            if not 'cmd' in payload:
                self.stream.read_until(b"\r\n", self.on_data)
                return
            ret = self.dispatch_message(payload)
            self.stream.write(self.wrap_data(json.dumps(ret)))
        except Exception as e:
            print message, e
            logger.exception(e)
            self.stream.write(self.wrap_data('error - %s' % e))
        self.stream.read_until(b"\r\n", self.on_data)

def client():
    default_base_path = os.path.join(os.path.expanduser("~"), '.pindown')

    parser = argparse.ArgumentParser()
    parser.add_argument('--base-dir', help='base directory of pindown_agent', default=default_base_path)
    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    cfg_path = os.path.join(args.base_dir, 'config.cfg')
    config.read(cfg_path)

    print config.sections()
    socket_list = []
    try:
        r = requests.get("http://pindown.io/servers/%s" % ','.join(config.sections()))
        logger.debug("status code for sockets list %s", r.status_code)
        socket_list = json.loads(r.content)
    except Exception as e:
        logger.critical("cant get addresses of socket servers, please try again later")
        logger.exception(e)
        return

    hostid = socket.gethostname()

    identifier_path = os.path.join(args.base_dir, 'identifier')
    try:
        f = open(identifier_path, 'r')
        identifier = f.read()
    except:
        identifier = str(uuid.uuid1())
        f = open(identifier_path, 'w')
        f.write(identifier)

    print identifier

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    stream = tornado.iostream.IOStream(s)
    conn = Connection(stream, args.base_dir, config, hostid, identifier=identifier)
    stream.connect((socket_list[0]['ip'], socket_list[0]['port']), conn.send_request)
    # stream.connect(('127.0.0.1', 8010), conn.send_request)

    scheduler = tornado.ioloop.PeriodicCallback(conn.heartbeat, 10000)
    scheduler.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    client()