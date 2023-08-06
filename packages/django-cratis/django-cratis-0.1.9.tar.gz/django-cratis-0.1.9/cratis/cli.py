import os
import sys
from cratis.env import load_env


def cratis_cmd():
    """
    Command that executes django ./manage.py task + adds cratis wrapping things
    """

    os.environ.setdefault("CRATIS_APP_PATH", os.getcwd())
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

    load_env()

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
