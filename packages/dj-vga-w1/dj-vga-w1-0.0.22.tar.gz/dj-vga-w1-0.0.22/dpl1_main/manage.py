#!/usr/bin/env python
import os
import sys

current_dir = os.getcwd()
sys.path.remove(current_dir)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

print sys.path
#This module is the ONLY ONE that sees 'deployment_util' as a standalone module
#All the other modules will see it only as a module in package dpl1_main
try:
    from deployment_util import correct_sys_path
except ImportError:
    # raise Exception('This module can only be executed from the current dir')
    pass

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dpl1_main.DPL1.settings")

    #Vlad was here: manage.py should see the PYTHONPATH as django-admin.py
    #sees it, meaning it should see dpl1_main as the main package
    # correct_sys_path()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
