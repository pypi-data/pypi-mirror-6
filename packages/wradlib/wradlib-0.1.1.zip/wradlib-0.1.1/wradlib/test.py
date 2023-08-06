#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      heistermann
#
# Created:     18/02/2014
# Copyright:   (c) heistermann 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from util import deprecated

# --- new function
def sum_many(*args):
    return sum(args)

# --- old / deprecated function
@deprecated(sum_many)
def sum_couple(a, b):
    return a + b



