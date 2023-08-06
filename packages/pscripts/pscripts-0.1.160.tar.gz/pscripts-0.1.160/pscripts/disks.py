#!/usr/bin/env python3

from subprocess import check_output

cmd = "lsblk"
output = check_output(cmd, shell=True)
# return output.decode("utf-8")
