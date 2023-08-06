#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    sys.path.insert(0, os.getcwd()) # for reading local config.ini
    import jira_analysis
    sys.path.insert(0, os.path.dirname(jira_analysis.__file__)) # for settings.py

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
