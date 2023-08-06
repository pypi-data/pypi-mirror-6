#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import migratore

if __name__ == "__main__":
    # validates that the provided number of arguments
    # is the expected one, in case it's not raises a
    # runtime error indicating the problem
    if len(sys.argv) < 3: raise RuntimeError("Invalid number of arguments")

    # unpacks the second and third command line arguments
    # as the scope of the execution and the name of the
    # script to be executed
    scope = sys.argv[1]
    script_name = sys.argv[2]

    # retrieves the set of extra arguments to be sent to the
    # command to be executed, (this may be dangerous)
    args =  sys.argv[3:]

    # retrieves both the loader command for the current
    # scope and the script to be executed and then used
    # them to run the requested command
    is_command = hasattr(migratore, "run_" + scope)
    if is_command: command = getattr(migratore, "run_" + scope)
    else: command = getattr(migratore, scope)
    is_script = hasattr(migratore, script_name)
    if is_script: script = getattr(migratore, script_name)
    else: script = script_name
    command(script, *args)
