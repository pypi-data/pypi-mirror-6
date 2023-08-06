import os
from voluptuous import Schema, Extra, MultipleInvalid
import yaml


class ThemeLoadException(Exception):
    pass


class ThemeNotFoundException(ThemeLoadException):
    pass


class ThemeBadConfigException(ThemeLoadException):
    pass


def validate_config(theme_config):
    Schema({
        'parents': [str],
        'cms_templates': {
            Extra: str
        },
        'template_dirs': [str],
        'asset_dirs': [str]
    })(theme_config)


def load_theme(theme_paths, name, allow_abstract=False):

    if name in theme_paths['themes']:
        theme_path = theme_paths['themes'][name]
    else:
        theme_path = theme_paths['dir'] + os.sep + name

    theme_config_file = theme_path + os.sep + 'theme.yml'

    if not os.path.exists(theme_path):
        raise ThemeNotFoundException("Theme %s do not exist." % theme_path)

    if os.path.exists(theme_config_file):
        theme_config = yaml.load(open(theme_config_file, 'r'))
    else:
        raise ThemeBadConfigException("Theme %s must contain theme.yml." % theme_path)

    try:
        validate_config(theme_config)
    except MultipleInvalid as e:
        raise ThemeBadConfigException("Theme config %s validation error: %s" % (theme_config_file, str(e)))

    """
    Each theme should contain at least one cms template.
    """
    if not theme_config.has_key('abstract') and (not theme_config.has_key('cms_templates') or len(theme_config['cms_templates']) == 0):
        raise ThemeBadConfigException("Theme %s should contain at least one cms template." % theme_path)

    if not allow_abstract and theme_config.has_key('abstract') and theme_config['abstract']:
        raise ThemeBadConfigException("Theme %s is marked as abstract and can not be loaded as main theme." % theme_path)

    theme_config['loaded_themes'] = [name]

    if not 'template_dirs' in theme_config:
        theme_config['template_dirs'] = []
    theme_config['template_dirs'] = [theme_path + os.sep + dir_ for dir_ in theme_config['template_dirs']]

    if not 'asset_dirs' in theme_config:
        theme_config['asset_dirs'] = []
    theme_config['asset_dirs'] = [theme_path + os.sep + dir_ for dir_ in theme_config['asset_dirs']]

    if theme_config.has_key('parents'):
        for parent_ in theme_config['parents']:
            try:
                parent_config = load_theme(theme_paths, parent_, allow_abstract=True)
            except (ThemeNotFoundException, ThemeBadConfigException) as e:
                raise ThemeBadConfigException("Error loading theme \"%s\" parent: %s" % (name, e.message,))


            # update only not existing keys
            parent_config['cms_templates'].update(theme_config['cms_templates'])
            theme_config['cms_templates'] = parent_config['cms_templates']

            theme_config['template_dirs'].extend(parent_config['template_dirs'])
            theme_config['asset_dirs'].extend(parent_config['asset_dirs'])

            theme_config['loaded_themes'] += parent_config['loaded_themes']

    return theme_config

