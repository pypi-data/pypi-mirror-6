#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Tests for 'diff' module.
"""

from diff import diff


def test_diff_with_wrong_types():
    res = diff(3, "4")
    assert res == [{'prev': 3, 'details': 'type', 'value': '4', 'replace': '/'}]

    res = diff([], 3)
    assert res == [{'prev': [], 'details': 'type', 'value': 3, 'replace': '/'}]    

    res = diff(3, [])
    assert res == [{'prev': 3, 'details': 'type', 'value': [], 'replace': '/'}]  
