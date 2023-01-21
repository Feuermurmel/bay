import argparse
import logging
import sys
from argparse import Namespace

from bay.util import UserError


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser()

    return parser.parse_args()


def main() -> None:
    pass


def entry_point() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    try:
        main(**vars(parse_args()))
    except UserError as e:
        logging.error(f'error: {e}')
        sys.exit(1)
    except KeyboardInterrupt:
        logging.error('Operation interrupted.')
        sys.exit(130)
