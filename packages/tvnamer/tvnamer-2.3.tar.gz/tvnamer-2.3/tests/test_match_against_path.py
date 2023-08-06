#!/usr/bin/env python

"""Tests matching against full file paths, instead of filenames
"""

from functional_runner import run_tvnamer, verify_out_data
from nose.plugins.attrib import attr
from helpers import expected_failure


@attr("functional")
def test_batchconfig():
    """Test simple path-matching
    """

    conf = """
    {"always_rename": true,
    "select_first": true}
    """

    out_data = run_tvnamer(
        with_files = ['Scrubs/s01e01.avi'],
        with_config = conf,
        with_input = "")

    expected_files = ['Scrubs - [01x01] - My First Day.avi']

    verify_out_data(out_data, expected_files)
