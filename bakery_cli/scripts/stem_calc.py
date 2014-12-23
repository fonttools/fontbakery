#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Source: https://github.com/mekkablue/Glyphs-Scripts/blob/master/Masters/Insert%20instances.py

from __future__ import division


def distribute_lucas(min_val, max_val, n):
    q = max_val / min_val
    return [min_val * q**(i/(n-1)) for i in range(n)]


def distribute_equal(min_val, max_val, n):
    d = (max_val - min_val) / (n-1)
    return [min_val + i*d for i in range(n)]


def distribute_pablo(min_val, max_val, n):
    es = distribute_equal(min_val, max_val, n)
    ls = distribute_lucas(min_val, max_val, n)
    return [l*(1-i/(n-1)) + e*(i/(n-1)) for (i, e, l) in zip(range(n), es, ls)]
