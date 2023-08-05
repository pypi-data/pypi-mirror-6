#!/python
# distutils will fix the above

import os
import pdb
import sys
import time
import argparse
import functools
import itertools
import random
import re

VERSION = 1

class VersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global VERSION
        print('fortune.py: Version %g' % pow(1+1.0/VERSION, VERSION))
        sys.exit(0)

def parse_args():
    argparser = argparse.ArgumentParser(prog = "fortune", description = "Fortune cookie program")
    argparser.add_argument('--debug', action = 'store_true')
    argparser.add_argument('--ini', action = 'store', nargs = 1, help = 'configuration file path')
    argparser.add_argument('-a', action = 'store_true', help = 'choose from all fortunes')
    argparser.add_argument('-e', action = 'store_true', help = 'consider all fortune files to be equal size')
    argparser.add_argument('-f', action = 'store_true', help = 'print list of fortune files')
    argparser.add_argument('-l', action = 'store_true', help = 'prefer long fortunes')
    argparser.add_argument('-n', action = 'store', type = int, nargs = 1, help = 'maximum length of a short fortune')
    argparser.add_argument('-o', action = 'store_true', help = 'choose from offensive fortunes')
    argparser.add_argument('-s', action = 'store_true', help = 'prefer short fortunes')
    argparser.add_argument('-w', action = 'store_true', help = 'wait after printing fortune')
    argparser.add_argument('-i', action = 'store_true', help = 'ignore case while searching')
    argparser.add_argument('-m', action = 'store', nargs = 1, help = 'match a regex pattern')
    argparser.add_argument('-c', action = 'store_true', help = 'print the cookie file')
    argparser.add_argument('-v', action = VersionAction, nargs = 0, help = 'print the version')
    argparser.add_argument('file', nargs = '*', help = 'fortune collection to use')
    return argparser.parse_args()

def uncomment(line):
    return line.split('#', maxsplit = 2)[0].strip('\n').strip()

def read_config(args):
    config = {'slen':'160', 'wait':'60', 'data':'datfiles', 'offdata':'datfiles/off'}
    config_path = os.path.join(os.environ['HOME'], 'fortune.ini')
    if args['ini']:
        config_path = args['ini'][0]
    try:
        with open(config_path, 'r', encoding = 'utf8') as fd:
            for line in fd:
                line = uncomment(line)
                if len(line) == 0:
                    continue
                pv = line.split('=', 2)
                if len(pv) == 2:
                    config[pv[0].strip()] = pv[1].strip()
    except:
        pass
    if not os.path.exists(config['data']):
        sys.stderr.write('Data files path (%s) does not exist. Check "data", "offdata" parameters in config file (%s).\n' % (os.path.realpath(config['data']), config_path))
        sys.exit(-1)
    return config

def get_files(config):
    datadir = config['data']
    for e in list(filter(lambda x: x[0]==datadir, os.walk(datadir)))[0][2]:
        yield os.path.join(datadir, e)

def get_off_files(config):
    offdir = config['offdata']
    for e in list(filter(lambda x: x[0]==offdir, os.walk(offdir)))[0][2]:
        yield os.path.join(offdir, e)

def print_files(config):
    for e in get_files(config):
        print(os.path.basename(e))
    for e in get_off_files(config):
        print('off/%s' % os.path.basename(e))
    return

def get_all_files(config, args):
    return itertools.chain(*[get_files(config), get_off_files(config)]) if args['a'] else get_off_files(config) if args['o'] else get_files(config)

def print_cookie(config, args):
    files = get_all_files(config, args)
    if len(args['file']) > 0:
        arg_files = set(args['file'])
        files = filter(lambda f: os.path.basename(f) in arg_files, files)
    eq = args['e']
    sized_files = sorted([(i if eq else os.stat(f).st_size, f) for i, f in enumerate(files)])
    size = len(sized_files) if eq else functools.reduce(lambda x,y: x+y[0], sized_files, 0)
    z = random.randrange(0, size)
    fortunate = sized_files[-1][1]
    for zf in sized_files:
        if zf[0] > z:
            fortunate = zf[1]
            break
    with open(fortunate, 'r', encoding = 'utf8') as fd:
        cookies = fd.read().split("\n%\n")
        shorter, longer = args['s'], args['l']
        if shorter or longer:
            shorty = args['n'][0] if args['n'] else int(config['slen'])
            cookies = list(filter((lambda x: len(x)<=shorty) if shorter else (lambda x: len(x)>shorty), cookies))
        n = random.randrange(0, len(cookies))
        if args['c']:
            print('%s:\n' % fortunate)
        print(cookies[n])
    return

def find_cookie_in_file(pattern, fname, args):
    with open(fname, 'r', encoding = 'utf8') as fd:
        cookies = fd.read().split("\n%\n")
        cookies = filter(lambda c: pattern.search(c), cookies)
        sys.stderr.write('\n%s\n%%' % fname)
        for c in cookies:
            print(c)
            print('%')
    return

def find_cookie(config, args):
    files = get_all_files(config, args)
    pattern = re.compile(args['m'][0], flags = re.IGNORECASE if args['i'] else 0)
    for f in files:
        find_cookie_in_file(pattern, f, args)
    return

def main(argv):
    args = vars(parse_args())
    if args['debug']:
        pdb.set_trace()
    config = read_config(args)
    if args['f']:
        print_files(config)
    elif args['m']:
        find_cookie(config, args)
    else:
        print_cookie(config, args)
    if args['w']:
        time.sleep(int(config['wait']))
    return

if __name__=="__main__":
    main(sys.argv)
