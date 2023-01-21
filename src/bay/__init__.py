import argparse
import logging
import sys
from argparse import Namespace
from pathlib import Path

from bay.bay import main
from bay.config import get_config_file_path, load_config
from bay.util import UserError


def parse_args() -> Namespace:
    default_config_path = get_config_file_path()

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'bay_patterns',
        nargs='*',
        default=['*'],
        help='Names and patterns used to match the names of drive bays. If no '
             'names are given, all bays are selected.')

    parser.add_argument(
        '-d', '--device-node',
        dest='print_device_nodes',
        action='store_true',
        help='Instead of printing stable device names, print the path to the '
             'device node itself.')

    parser.add_argument(
        '-t', '--table',
        action='store_true',
        help='Instead of printing just the stable device name, print a table '
             'with a line for each matched drive bay with bay\'s name and all '
             'stable device names.')

    parser.add_argument(
        '-b', '--name-only',
        action='store_true',
        help='For each printed stable device name, print just the last part of '
             'the path.')

    parser.add_argument(
        '-p', '--prefix',
        default='',
        help='Add the specified prefix to all lines printed. This can be '
             'helpful when passing the output as arguments to another command.')

    parser.add_argument(
        '-n', '--part-num',
        type=int,
        metavar='N',
        help='Append `-part<N>\' to the configured paths of symlinks that '
             'identify a drive bay, effectively processing and printing the '
             'paths of partitions instead of whole devices.')

    parser.add_argument(
        '-c', '--config',
        dest='config_path',
        type=Path,
        default=default_config_path,
        help=f'Use the specified config file. Defaults to '
             f'`{default_config_path}\'.')

    args = parser.parse_args()

    if args.table and args.prefix:
        parser.error('--table and --prefix can\'t be combined.')

    return args


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
