import cmd
import requests
import argparse
import ConfigParser
import os, errno
import sys

default_base_path = os.path.join(os.path.expanduser("~"), '.pindown')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def prepare_base_dir(dir):
    mkdir_p(dir)
    mkdir_p(os.path.join(dir, 'run'))
    mkdir_p(os.path.join(dir, 'log'))

def add_project():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id", help="project id")
    parser.add_argument("name", help="project name")
    parser.add_argument('--base-dir', help='home directory for pindown to store files etc., default: ~/.pindown',
                                      default=default_base_path)
    opts = parser.parse_args()
    # read our config
    config = ConfigParser.ConfigParser()
    cfg_path = os.path.join(opts.base_dir, 'config.cfg')
    config.read(cfg_path)
    try:
        config.add_section(opts.project_id)
    except ConfigParser.DuplicateSectionError as e:
        pass

    config.set(opts.project_id, 'name', opts.name)
    with open(cfg_path, 'wb') as configfile:
        config.write(configfile)

    print "Added project", opts.project_id

def remove_project():
    pass


def setup():

    supervisorconf = """
[supervisorctl]
serverurl = unix:///tmp/pindown-supervisor.sock

[unix_http_server]
file=/tmp/pindown-supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisord]
minfds = 1024
minprocs = 200
loglevel = info
logfile = __BASE_DIR__/log/pindown-supervisord.log
logfile_maxbytes = 50MB
nodaemon = false
pidfile = __BASE_DIR__/run/pindown-supervisord.pid
logfile_backups = 10

[program:pindown_agent]
command=__PYTHON__ __MODULE__ --base-dir=__BASE_DIR__
stdout_logfile=__BASE_DIR__/log/pindown-agent.log
stderr_logfile=__BASE_DIR__/log/pindown-agent.err
priority=999
startsecs=2
    """

    # TODO: warn if basedir exists
    parser = argparse.ArgumentParser()
    parser.add_argument('user_id', help='user id')
    parser.add_argument('uuid', help='uuid of user')
    parser.add_argument('--base-dir', help='home directory for pindown to store files etc., default: ~/.pindown',
                                      default=default_base_path)
    opts = parser.parse_args()
    try:
        prepare_base_dir(opts.base_dir)
    except OSError as e:
        if e.errno == 13:
            print "ERROR: Permission denied for base path, are you sure you have write access ? maybe need to run with sudo"
            return

    # r = requests.get('http://localhost:9010/preshared_key/%s/%s' % (opts.user_id, opts.uuid))
    r = requests.get('http://pindown.io/preshared_key/%s/%s' % (opts.user_id, opts.uuid))
    if r.status_code == 200:
        path = os.path.join(os.path.realpath(opts.base_dir), 'shared.key')
        f = open(path, 'w')
        f.write(r.content)
        f.close()
    else:
        print "ERROR: Wrong user id or uuid"
        return

    from pindown_agent import client
    client_executable_path = os.path.abspath(client.__file__).replace('.pyc', '.py')
    python_executable_path = sys.executable

    supervisorconf = supervisorconf.replace('__PYTHON__', python_executable_path).replace('__MODULE__', client_executable_path).replace('__BASE_DIR__', opts.base_dir)

    supervisor_conf_path = os.path.join(opts.base_dir, 'supervisor.conf')
    f = open(supervisor_conf_path, 'wb')
    f.write(supervisorconf)
    f.close()

    print "setup completed. now you can add projects"

def run_supervisor():
    from subprocess import Popen
    parser = argparse.ArgumentParser()
    parser.add_argument('--supervisor-path', help='path for supervisord',
                                      default='supervisord')

    parser.add_argument('--base-dir', help='home directory for pindown to store files etc., default: ~/.pindown',
                                      default=default_base_path)
    opts = parser.parse_args()
    print os.path.join(opts.base_dir, 'supervisor.conf')
    cmd = ['supervisord --configuration=%s' % os.path.join(opts.base_dir, 'supervisor.conf')]
    print "running supervisor", cmd[0]
    proc = Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)