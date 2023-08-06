#!/usr/bin/env python

"""
Tests for curmit.
"""

import os
import unittest
from unittest.mock import patch, Mock

from curmit.curmit import main, urltext

ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)

# This published document cannot be parsed as a Google doc by 'html2text'
STRANGE_URL = "https://docs.google.com/document/d/1DXQk7Qnd0wCBZ4T8GcUHcMMc2oVPMjXOxMIeyfLQ4v4/pub?embedded=true"  # pylint: disable=C0301


class TestCLI(unittest.TestCase):  # pylint: disable=R0904
    """Integration tests for the 'curmit' command."""

    @unittest.skipUnless(os.getenv(ENV), REASON)
    def test_no_update(self):
        """Verify 'curmit --no-update' can be called."""
        self.assertIs(None, main(['--no-update']))

    @unittest.skipUnless(os.getenv(ENV), REASON)
    def test_no_commit(self):
        """Verify 'curmit --no-commit' can be called."""
        self.assertIs(None, main(['--no-commit']))

    @patch('curmit.curmit._run', Mock(return_value=False))
    def test_exit(self):
        """Verify 'curmit' treats False as an error ."""
        self.assertRaises(SystemExit, main, [])

    @patch('curmit.curmit._run', Mock(side_effect=KeyboardInterrupt))
    def test_interrupt(self):
        """Verify 'curmit' treats KeyboardInterrupt as an error."""
        self.assertRaises(SystemExit, main, [])


@patch('curmit.curmit._run', Mock(return_value=True))  # pylint: disable=R0904
class TestLogging(unittest.TestCase):  # pylint: disable=R0904
    """Integration tests for the 'curmit' logging."""

    def test_verbose_1(self):
        """Verify verbose level 1 can be set."""
        self.assertIs(None, main(['-v']))

    def test_verbose_2(self):
        """Verify verbose level 2 can be set."""
        self.assertIs(None, main(['-vv']))

    def test_verbose_3(self):
        """Verify verbose level 3 can be set."""
        self.assertIs(None, main(['-vvv']))


@unittest.skipUnless(os.getenv(ENV), REASON)  # pylint: disable=R0904
class TestUrlText(unittest.TestCase):  # pylint: disable=R0904
    """Integration tests for getting URL text."""

    def test_invalid_google_doc(self):
        """Verify that 'html2text' handles strange Google Documents."""
        self.assertIsInstance(urltext(STRANGE_URL), list)

    def test_invalid(self):
        """Verify an exception is raised on an invalid URL."""
        self.assertRaises(IOError, urltext, "")
