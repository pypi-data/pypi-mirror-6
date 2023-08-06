#!/usr/bin/env python
import argparse
import logging
import sys
from .styles import toggle_style

parser = argparse.ArgumentParser(usage="%(prog)s [options] args...")

def main(args):
    source = sys.stdin.read()
    return toggle_style(source)
    return 0


def main_entry_point():
    args = parser.parse_args()
    sys.exit(main(args))


if __name__ == "__main__":
    main_entry_point()
