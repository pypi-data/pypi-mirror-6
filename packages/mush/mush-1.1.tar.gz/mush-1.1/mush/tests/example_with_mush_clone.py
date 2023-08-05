from argparse import ArgumentParser, Namespace
from .configparser import RawConfigParser
from mush import Runner, requires, first, last, attr, item
import logging, os, sqlite3, sys

log = logging.getLogger()

@requires(ArgumentParser)
def base_options(parser):
    parser.add_argument('config', help='Path to .ini file')
    parser.add_argument('--quiet', action='store_true',
                        help='Log less to the console')
    parser.add_argument('--verbose', action='store_true',
                        help='Log more to the console')

@requires(last(ArgumentParser))
def parse_args(parser):
    return parser.parse_args()

class Config(dict): pass

@requires(first(Namespace))
def parse_config(args):
    config = RawConfigParser(dict_type=Config)
    config.read(args.config)
    return Config(config.items('main'))

def setup_logging(log_path, quiet=False, verbose=False):
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)
    if not quiet:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        log.addHandler(handler)

class DatabaseHandler:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
    def __enter__(self):
        return self
    def __exit__(self, type, obj, tb):
        if type:
            log.exception('Something went wrong')
            self.conn.rollback()

base_runner = Runner(ArgumentParser, base_options, parse_args, parse_config)
base_runner.add(setup_logging,
                log_path = item(first(Config), 'log'),
                quiet = attr(first(Namespace), 'quiet'),
                verbose = attr(first(Namespace), 'verbose'))


def args(parser):
    parser.add_argument('path', help='Path to the file to process')

def do(conn, path):
    filename = os.path.basename(path)
    with open(path) as source:
        conn.execute('insert into notes values (?, ?)',
                     (filename, source.read()))
    conn.commit()
    log.info('Successfully added %r', filename)
    
main = base_runner.clone()
main.add(args, ArgumentParser)
main.add(DatabaseHandler, item(Config, 'db'))
main.add(do,
         attr(DatabaseHandler, 'conn'),
         attr(Namespace, 'path'))

if __name__ == '__main__':
    main()
