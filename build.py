#!/usr/bin/env python

import sys
import os
import sh

from argparse import ArgumentParser


# Initialize
try:
    token = os.environ['BINSTAR_KEYN']
except KeyError:
    sys.exit("Must set $BINSTAR_KEY")
binstar = sh.Command('binstar').bake(t=token)
conda = sh.Command('conda')


def build_and_publish(path, channel):
    binfile = conda.build("--output", path).strip()
    conda.build(path)
    binstar.upload(binfile, force=True, channel=channel)


def main():
    parser = ArgumentParser()
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-c', '--channel', required=False, default='main')
    parser.add_argument('-s', '--site', required=False, default=None)
    parser.add_argument('-b', '--build_dir', required=False, default='conda')
    args = parser.parse_args()
    
    build_and_publish(args.build_dir, channel=args.channel)
    return 0


if __name__ == '__main__':
    sys.exit(main())
