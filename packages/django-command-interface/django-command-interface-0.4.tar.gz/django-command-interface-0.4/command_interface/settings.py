"""Setting defaults for the ``command_interface`` app."""
from django.conf import settings

# list of commands to explicitly display. Adds up with DISPLAYED_APPS
DISPLAYED_COMMANDS = getattr(
    settings, 'COMMAND_INTERFACE_DISPLAYED_COMMANDS', [])

# which apps should be displayed on the main view. Same syntax is as in
# INSTALLED_APPS
DISPLAYED_APPS = getattr(settings, 'COMMAND_INTERFACE_DISPLAYED_APPS', [])

# absolute path, where the log files should be stored. All files will be
# prefixed with "command_interface_log-"
LOGFILE_PATH = getattr(settings, 'COMMAND_INTERFACE_LOGFILE_PATH', None)

# even though command interface can try to find the active virtual environment
# on its own, you can specify the exact path to your venv, that holds the
# correct python version to use. e.g. '/home/myname/Envs/myvenv/'
# this will then automatically attach 'bin/python' to execute the subprocesses
# with the correct python executable
VENV_PATH = getattr(settings, 'COMMAND_INTERFACE_VENV_PATH', None)
