import os
import sys
import yaml


def _find_project_env(path):
    env_file_name = '%s/%s_env.yml' % (os.path.dirname(path), os.path.basename(path))
    env_file_name_dot = '%s/.%s_env.yml' % (os.path.dirname(path), os.path.basename(path))

    if os.path.exists(env_file_name):
        return path, env_file_name
    elif os.path.exists(env_file_name_dot):
        return path, env_file_name_dot
    elif path != '/':
        return _find_project_env(os.path.dirname(path))
    else:
        return None, None


def _format_val(val):
    return str(val)


def load_env():
    """
    Loads environment variables from project folder ../folder_name_env.yml file
    """
    app_dir, _file = _find_project_env(os.getcwd())
    if _file:
        os.environ["CRATIS_APP_PATH"] = app_dir

        with open(_file) as f:
            for key, val in yaml.load(f).iteritems():
                val = _format_val(val)
                os.environ[key] = val

    sys.path += (os.environ['CRATIS_APP_PATH'], )

    if os.path.exists(os.environ['CRATIS_APP_PATH'] + os.sep + 'settings.py'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cratis.settings")