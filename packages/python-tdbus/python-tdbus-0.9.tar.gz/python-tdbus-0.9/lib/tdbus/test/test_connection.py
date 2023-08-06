"""
This file is part of python-tdbus. Python-tdbus is free software
available under the terms of the MIT license. See the file "LICENSE" that
was provided together with this source file for the licensing terms.

Copyright (c) 2012 the python-tdbus authors. See the file "AUTHORS" for a
complete list.
"""
import unittest

from tdbus import SimpleDBusConnection, GEventDBusConnection, DBUS_BUS_SESSION
from tdbus.test.base import BaseTest


class TestSimpleDBusConnection(unittest.TestCase, BaseTest):
    """Test suite for D-BUS connection."""

    def test_connection_open(self):
        conn = SimpleDBusConnection(DBUS_BUS_SESSION)
        conn.open(DBUS_BUS_SESSION)
        conn.close()

    def test_connection_init(self):
        conn = SimpleDBusConnection(DBUS_BUS_SESSION)
        conn.close()

    def test_connection_multiple_open(self):
        conn = SimpleDBusConnection(DBUS_BUS_SESSION)
        conn.close()
        conn.open(DBUS_BUS_SESSION)
        conn.close()

    def test_get_unique_name(self):
        conn = SimpleDBusConnection(DBUS_BUS_SESSION)
        name = conn.get_unique_name()
        assert name.startswith(':')
        conn.close()

class TestGeventDBusConnection(unittest.TestCase, BaseTest):
    """Test suite for D-BUS connection."""

    def test_connection_open(self):
        conn = GEventDBusConnection(DBUS_BUS_SESSION)
        conn.open(DBUS_BUS_SESSION)
        conn.close()

    def test_connection_init(self):
        conn = GEventDBusConnection(DBUS_BUS_SESSION)
        conn.close()

    def test_connection_multiple_open(self):
        conn = GEventDBusConnection(DBUS_BUS_SESSION)
        conn.close()
        conn.open(DBUS_BUS_SESSION)
        conn.close()

    def test_get_unique_name(self):
        conn = GEventDBusConnection(DBUS_BUS_SESSION)
        name = conn.get_unique_name()
        assert name.startswith(':')
        conn.close()
