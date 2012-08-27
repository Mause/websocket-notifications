#!/usr/bin/env python
import os
import subprocess


def get_version():
    if 'git' in os.environ['PATH'] and os.path.isdir('.git'):
        version_string = str(
            subprocess.Popen(['git', 'rev-parse', 'HEAD'],
                stdout=subprocess.PIPE,
                shell=True).communicate()[0])[:7]
    else:
        version_string = '1.0.0'
    return version_string
