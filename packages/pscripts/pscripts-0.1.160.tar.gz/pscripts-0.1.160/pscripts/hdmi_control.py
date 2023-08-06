#!/usr/bin/env python

from pdb import set_trace
from subprocess import check_output, call
from re import search 

line_pattern = r"(\d\.\d+)"

##########################
# API

def increase_brightness(step=0.1):
    # set_trace()
    line = get_brightness_line()
    val = extract_brightness(line)
    new_val = increment(val, step)
    set_brightness(new_val)

def decrease_brightness(step=0.1):
    # set_trace()
    line = get_brightness_line()
    val = extract_brightness(line)
    new_val = decrement(val, step)
    set_brightness(new_val)


##########################
# HELPERS

def increment(start, step):
    if start + step > 1.0:
        return 1.0
    return round(start + step, 1)

def decrement(start, step):
    if start - step <= 0:
        return 0.0
    return round(start - step, 1)

def set_brightness(val):
    # xrandr --output HDMI1  --brightness .5
    cmd = "xrandr --output HDMI1  --brightness " + str(val)
    call(cmd.split())

def get_brightness_line():
    cmd = "xrandr --current --verbose | grep -A5 'HDMI1' | tail -1"
    output = check_output(cmd, shell=True)
    return output.decode("utf-8")

def extract_brightness(line):
    # sample: b'\tBrightness: 0.50\n'
    match = search(line_pattern, line)
    return round(float(match.group(1)), 1)    

##########################
# TESTS

def _test():
    test_line_rewrite()
    test_numbers_only()

# UNIT-TESTS
def test_extract_brightness():
    sample_line = b'\tBrightness: 0.50\n'
    expected = 0.5
    result = extract_brightness(sample_line)
    assert expect == result

def test_numbers_only():
    b = 1.0
    a = 0.9
    res = decrement(b, adjust_brightness_step_val)
    assert a == res

if __name__ == '__main__':
    _test()
