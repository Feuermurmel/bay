from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import dacite
import platformdirs
import toml
from bay.util import UserError


@dataclass
class Config:
    bays: Dict[str, str]
    bay: 'Dict[str, BayConfig]'


@dataclass
class BayConfig:
    stable_patterns: List[str]


def get_config_file_path() -> Path:
    return Path(platformdirs.user_config_dir('bay')) / 'bay.toml'


def load_config(path: Path) -> Config:
    try:
        return dacite.from_dict(Config, toml.load(path))
    except FileNotFoundError as e:
        raise UserError(f'Config file `{e.filename}\' not found.')
