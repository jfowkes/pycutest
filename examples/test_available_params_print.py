#!/usr/bin/env python3

"""
Test interface for parameter-dependent problems
"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

import pycutest

# name = 'ARGLALE'
# name = 'COOLHANS'
name = 'SEMICON2'

pycutest.print_available_sif_params(name)
