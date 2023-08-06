import argparse
import paste.deploy
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os
import sys

parser = argparse.ArgumentParser(description='Run WSGI applications')
parser.add_argument(
    'config', metavar="CONFIG",
    help="Paste deploy configuratopm")
parser.add_argument(
    '--application', '-a', default='main',
    help='application name in the configuration file')
parser.add_argument(
    '--server', '-s', default='main',
    help='server name in the configuration file')
parser.add_argument(
    '--configuration', '-c', default='main',
    help='configuration name in the configuration file')
parser.add_argument(
    '--logging', '-l', default='main',
    help='logging configuration name in the configuration file')

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args(args)

    config = os.path.abspath(args.config)

    cp = configparser.RawConfigParser()
    cp.read(config)

    def items(section):
        if cp.has_section(section):
            return dict(
                (k, v)
                for (k, v) in cp.items(section)
                if k not in cp.defaults()
                )


    log = items('logging:'+args.logging)
    if log:
        if 'config' in log:
            import ZConfig
            ZConfig.configureLoggers(log['config'])
        else:
            import logging
            if 'level' in log:
                log['level'] = logging.getLevelName(log['level'])
            logging.basicConfig(**log)

    configuration = items('configuration:' + args.configuration)
    if configuration:
        use = configuration.pop('use')
        if use.startswith('egg:'):
            use = use[4:].split('#', 1)
            if len(use) == 2:
                use, rname = use
            else:
                use = use[0]
                rname = 'default'
            import pkg_resources
            use = pkg_resources.load_entry_point(use, 'configuration', rname)
        elif use.startswith('call:'):
            use, expr = use[5:].split(':', 1)
            mod = __import__(use, {}, {}, ['*'])
            use = eval(expr, mod.__dict__)
        else:
            raise ValueError(use)
        use(cp.defaults(), **configuration)

    app = paste.deploy.loadapp('config:'+config, args.application)
    server = paste.deploy.loadserver('config:'+config, args.server)
    sys.setcheckinterval(1000)
    server(app)
