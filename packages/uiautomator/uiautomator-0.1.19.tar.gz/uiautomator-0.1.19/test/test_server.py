#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock, patch, call, mock_open
from uiautomator import AutomatorServer


class TestAutomatorServer(unittest.TestCase):

    def setUp(self):
        self.Adb_patch = patch('uiautomator.Adb')
        self.Adb = self.Adb_patch.start()

    def tearDown(self):
        self.Adb.stop()

    def test_local_port(self):
        self.assertEqual(AutomatorServer("1234", 9010).local_port, 9010)
        self.Adb.assert_called_once_with(serial="1234")

    def test_local_port_forwarded(self):
        self.Adb.return_value.forward_list.return_value = [
            ("1234", "tcp:1001", "tcp:9009"),
            ("1234", "tcp:1000", "tcp:9008")
        ]
        self.Adb.return_value.device_serial.return_value = "1234"
        self.assertEqual(AutomatorServer("1234").local_port, 1000)

    def test_local_port_scanning(self):
        with patch('uiautomator.next_local_port') as next_local_port:
            self.Adb.return_value.forward_list.return_value = []
            next_local_port.return_value = 1234
            self.assertEqual(AutomatorServer("abcd", None).local_port,
                             next_local_port.return_value)

            next_local_port.return_value = 14321
            self.Adb.return_value.forward_list.return_value = Exception("error")
            self.assertEqual(AutomatorServer("abcd", None).local_port,
                             next_local_port.return_value)

    def test_device_port(self):
        self.assertEqual(AutomatorServer().device_port, 9008)

    def test_start_success(self):
        server = AutomatorServer()
        server.download_and_push = MagicMock()
        server.download_and_push.return_value = ["bundle.jar", "uiautomator-stub.jar"]
        server.ping = MagicMock()
        server.ping.return_value = "pong"
        server.adb = MagicMock()
        server.start()
        server.adb.cmd.assert_valled_onec_with('shell', 'uiautomator', 'runtest', 'bundle.jar', 'uiautomator-stub.jar', '-c', 'com.github.uiautomatorstub.Stub')

    def test_start_error(self):
        server = AutomatorServer()
        server.download_and_push = MagicMock()
        server.download_and_push.return_value = ["bundle.jar", "uiautomator-stub.jar"]
        server.ping = MagicMock()
        server.ping.return_value = None
        server.adb = MagicMock()
        with patch("time.sleep"):
            with self.assertRaises(IOError):
                server.start()

    def test_auto_start(self):
        with patch("uiautomator.JsonRPCClient") as JsonRPCClient:
            JsonRPCClient.ping.return_value = None
            server = AutomatorServer()
            server.start = MagicMock()
            server.stop = MagicMock()
            server.jsonrpc
            server.start.assert_called_once_with()

    def test_start_ping(self):
        with patch("uiautomator.JsonRPCClient") as JsonRPCClient:
            JsonRPCClient.return_value.ping.return_value = "pong"
            server = AutomatorServer()
            server.adb = MagicMock()
            server.adb.forward.return_value = 0
            self.assertEqual(server.ping(), "pong")

    def test_start_ping_none(self):
        with patch("uiautomator.JsonRPCClient") as JsonRPCClient:
            JsonRPCClient.return_value.ping.side_effect = Exception("error")
            server = AutomatorServer()
            self.assertEqual(server.ping(), None)


class TestAutomatorServer_Stop(unittest.TestCase):

    def setUp(self):
        try:
            import urllib2
            self.urlopen_patch = patch('urllib2.urlopen')
        except:
            self.urlopen_patch = patch('urllib.request.urlopen')
        finally:
            self.urlopen = self.urlopen_patch.start()

    def tearDown(self):
        self.urlopen_patch.stop()

    def test_download_and_push(self):
        jars = ["bundle.jar", "uiautomator-stub.jar"]
        with patch("os.path.exists") as exists:
            with patch("os.stat") as stat:
                server = AutomatorServer()
                server.adb = MagicMock()
                exists.return_value = True
                stat.st_size = 1024
                self.assertEqual(set(server.download_and_push()), set(jars))
                for args in server.adb.cmd.call_args_list:
                    self.assertEqual(args[0][0], "push")
                    self.assertEqual(args[0][2], "/data/local/tmp/")

    def test_download_and_push_download(self):
        jars = ["bundle.jar", "uiautomator-stub.jar"]
        with patch("os.path.exists") as exists:
            with patch("os.mkdir") as mkdir:
                with patch("%s.open" % open.__class__.__module__, mock_open(), create=True) as m_open:
                    server = AutomatorServer()
                    server.adb = MagicMock()
                    exists.return_value = False
                    self.assertEqual(set(server.download_and_push()), set(jars))
                    self.assertEqual(len(m_open.call_args_list), len(jars))

    def test_stop_started_server(self):
        server = AutomatorServer()
        server.adb = MagicMock()
        server.uiautomator_process = process = MagicMock()
        process.poll.return_value = None
        server.stop()
        process.wait.assert_called_once_with()

        server.uiautomator_process = process = MagicMock()
        process.poll.return_value = None
        self.urlopen.side_effect = IOError("error")
        server.stop()
        process.kill.assert_called_once_with()

    def test_stop(self):
        results = [
            b"USER     PID   PPID  VSIZE  RSS     WCHAN    PC         NAME\n\rsystem    372   126   635596 104808 ffffffff 00000000 S uiautomator",
            b"USER     PID   PPID  VSIZE  RSS     WCHAN    PC         NAME\r\nsystem    372   126   635596 104808 ffffffff 00000000 S uiautomator",
            b"USER     PID   PPID  VSIZE  RSS     WCHAN    PC         NAME\nsystem    372   126   635596 104808 ffffffff 00000000 S uiautomator",
            b"USER     PID   PPID  VSIZE  RSS     WCHAN    PC         NAME\rsystem    372   126   635596 104808 ffffffff 00000000 S uiautomator"
        ]
        for r in results:
            server = AutomatorServer()
            server.adb = MagicMock()
            server.adb.cmd.return_value.communicate.return_value = (r, "")
            server.stop()
            self.assertEqual(server.adb.cmd.call_args_list,
                             [call("shell", "ps", "-C", "uiautomator"), call("shell", "kill", "-9", "372")])
