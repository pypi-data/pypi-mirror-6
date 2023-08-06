from __future__ import print_function
import subprocess
import sys
import re
import os

def check_syntax(filename):
    args = ["ecpg", "-o", "-", filename]

    with open(os.devnull, "w") as devnull:
        try:
            proc = subprocess.Popen(args, shell=False,
                                    stdout=devnull,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
        except OSError as e:
            msg = "Unable to execute 'ecpg', you likely need to install it.'"
            raise OSError(msg)

        proc.wait()
        if proc.returncode == 0:
            proc.stderr.close()
            return (True, "")
        else:
            err = proc.stderr.readline()
            proc.stderr.close()
            return (False, parse_error(err))

def parse_error(error):
    error = re.sub(r'^[^:]+:', 'line ', error, count=1)
    error = re.sub(r'\/\/', '--', error)
    return error.strip()
