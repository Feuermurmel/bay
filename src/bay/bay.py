import fnmatch
import functools
import glob
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Iterator

from bay.config import Config, load_config

bay_paths_root_dir = Path('/dev/disk/by-path')
resolve_pattern_root_dir = Path('/dev/disk/by-id')


@functools.lru_cache(None)
def get_device_node(path: Path) -> 'Path | None':
    try:
        return path.resolve(True)
    except FileNotFoundError:
        return None


@dataclass
class StableNameInfo:
    stable_name: Path
    device_node: Path


@functools.lru_cache(None)
def get_stable_name_infos(pattern: str) -> List[StableNameInfo]:
    absolute_pattern = str(resolve_pattern_root_dir / pattern)
    infos: List[StableNameInfo] = []

    for i in sorted(glob.glob(absolute_pattern, recursive=True)):
        stable_name = Path(i)
        device_node = get_device_node(stable_name)

        if device_node is not None:
            infos.append(StableNameInfo(stable_name, device_node))

    return infos


def get_stable_patterns(config: Config, bay_name: str):
    for p, c in reversed(config.bay.items()):
        if fnmatch.fnmatchcase(bay_name, p):
            return c.stable_patterns

    return ['*']


def iter_stable_names(device_node: Path, patterns: List[str]) -> Iterator[Path]:
    return (
        i.stable_name
        for p in patterns
        for i in get_stable_name_infos(p)
        if i.device_node == device_node)


def get_first_stable_name(device_node: Path, patterns: List[str]) -> 'Path | None':
    try:
        return next(iter_stable_names(device_node, patterns))
    except StopIteration:
        return None


def get_matched_bay_names(config: Config, pattern: str) -> List[str]:
    matched_names = [n for n in config.bays if fnmatch.fnmatchcase(n, pattern)]

    if not matched_names:
        logging.warning(
            f'warning: Pattern `{pattern}\' does not match the names of any '
            f'bays.')

    return matched_names


def main(
        bay_patterns: List[str], print_device_nodes: bool, table: bool,
        name_only: bool, prefix: str, part_num: 'int | None',
        config_path: Path) \
        -> None:
    config = load_config(config_path)

    matched_bay_names = [
        j for i in bay_patterns
        for j in get_matched_bay_names(config, i)]

    def render_stable_name(name: Path):
        if name_only:
            string = name.name
        else:
            string = str(name)

        return prefix + string

    for b in matched_bay_names:
        path = bay_paths_root_dir / config.bays[b]

        if part_num is not None:
            path = path.parent / f'{path.name}-part{part_num}'

        device_node = get_device_node(path)

        if table:
            if device_node is None:
                stable_names_str = '(no device present)'
            elif print_device_nodes:
                stable_names_str = render_stable_name(device_node)
            else:
                patterns = get_stable_patterns(config, b)
                stable_names = iter_stable_names(device_node, patterns)

                if stable_names:
                    stable_names_str = \
                        ' '.join(render_stable_name(i) for i in stable_names)
                else:
                    stable_names_str = '(no matching stable name)'

            print(f'{b}: {stable_names_str}')
        else:
            if device_node is not None:
                if print_device_nodes:
                    print(render_stable_name(device_node))
                else:
                    patterns = get_stable_patterns(config, b)
                    stable_name = get_first_stable_name(device_node, patterns)

                    if stable_name:
                        print(render_stable_name(stable_name))
                    else:
                        logging.warning(
                            f'warning: Could not find a stable name for device '
                            f'node `{device_node}\' in  bay `{b}\'.')
