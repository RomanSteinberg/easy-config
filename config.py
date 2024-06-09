"""
Title: Easy config
Description: Easy to use config processing based on yaml-files configuration. Allows hierarchical storage
    of configuration parameters, local storage for secrets and local parameters, validation of local and
    default configuration files validation.
Author: Roman Steinberg
Date: 2024-05-01

Copyright (c) 2024 Roman Steinberg

Licensed under the MIT License. See LICENSE file in the project root for full license information.
"""

from copy import deepcopy
from pathlib import Path

import yaml
from easydict import EasyDict

SubConfigType = dict | list | str | float | int


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self, user_source='configs/config.yaml', default_source='configs/config-default.yaml'):
        self._keys = list()
        self._user_source = user_source
        self._default_source = default_source
        self.reset()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)

    def __getitem__(self, name):
        return getattr(self, name)

    def get_part(self, subconfig: str) -> EasyDict:
        partial_config = {} if self[subconfig] is None else deepcopy(self[subconfig])
        partial_config.update(self['general'])
        return partial_config

    def reset(self):
        for key in self._keys:
            delattr(self, key)
        self._keys = list()

        d = EasyDict(self._load_config())
        for k, v in d.items():
            setattr(self, k, v)
            self._keys.append(k)

    def _load_config(self):
        config = self._read_config(self._default_source)
        local_config = dict()
        if Path(self._user_source).exists():
            local_config = self._read_config(self._user_source)

        config_issues = list()
        is_valid = self._update_config(
            config, local_config, config_name=self._default_source, issues_to_print=config_issues
        )
        if len(config_issues) > 1:
            print(f'Problem(s) with configs:\n{"".join(config_issues)}\n'
                  f'Check and correct your {_make_bold(self._default_source)} '
                  f'and {_make_bold(self._user_source)}!')
        if not is_valid:
            exit(0)

        self._working_dir = Path(config['general']['working_dir']).absolute()
        self._resources_dir = Path(config['general']['resources_dir']).absolute()
        config['general']['working_dir'] = str(self._working_dir)
        self._set_absolute_paths(config)

        return config

    @staticmethod
    def _read_config(source: str) -> dict[SubConfigType]:
        if isinstance(source, str):
            with open(source, 'r') as stream:
                config = yaml.safe_load(stream)
            if config is None:
                print(f'{source} is empty. Fill it, please.')
                exit()
        else:
            raise TypeError('Unexpected source to load config')
        return config

    @staticmethod
    def _update_config(
            default_cfg: SubConfigType,
            local_cfg: SubConfigType,
            config_name: str,
            issues_to_print: list[str]
    ) -> bool:
        result = True
        if type(default_cfg) != type(local_cfg):
            issues_to_print.append(f'{config_name} has different types: {type(default_cfg)} and {type(local_cfg)}\n')
            result = False
        elif isinstance(local_cfg, dict):
            for key, value in local_cfg.items():
                if key not in default_cfg:
                    issues_to_print.append(
                        f'No key in {config_name} {_get_delimiter()} {_make_bold(key)}\n'
                    )
                    result = False
                elif isinstance(value, dict):
                    new_str = f'{config_name} {_get_delimiter()} {key}'
                    cfg1, cfg2 = default_cfg[key], value
                    result = Config._update_config(cfg1, cfg2, new_str, issues_to_print) and result
                else:
                    default_cfg[key] = value

        return result

    def _set_absolute_paths(self, d: dict[SubConfigType]):
        for key, value in d.items():
            if isinstance(d[key], dict):
                if key.strip() == 'resources':
                    for sub_key, sub_value in value.items():
                        value[sub_key] = str(self._resources_dir.joinpath(sub_value))
                else:
                    self._set_absolute_paths(d[key])
            else:
                if value is not None:
                    if 'path' in key:
                        d[key] = str(self._working_dir.joinpath(value))
                    elif 'location' in key:
                        d[key] = str(self._resources_dir.joinpath(value))


def _make_bold(s):
    bold = '\033[1m'
    end_bold = '\033[0m'
    return bold + s + end_bold


def _get_delimiter():
    return '->'
