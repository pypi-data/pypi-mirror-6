#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import jira_analysis
    sys.path.insert(0, os.path.dirname(jira_analysis.__file__))
    sys.path.insert(0, os.getcwd()) # for reading local config.ini

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
