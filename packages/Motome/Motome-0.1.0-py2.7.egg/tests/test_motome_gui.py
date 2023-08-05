#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_motome_notemodel
----------------------------------

Tests the Motome Pyside GUI

see: https://voom.kilnhg.com/Code/Make-Stuff-Happen/Group/PyQtTestExample/Files/src/MargaritaMixerTest.py?nr=
"""

import glob
import os
import shutil
import sys
import unittest

from PySide import QtCore, QtGui, QtTest

from Motome.Modules.MainWindow import MainWindow

TESTS_DIR = os.path.join(os.getcwd(), 'tests')
TESTER_NOTES_PATH = os.path.join(os.getcwd(), 'tests', 'notes_for_testing')
EMPTY_TESTER_NOTES_PATH = os.path.join(os.getcwd(), 'tests', 'empty_notes_for_testing')

ZEN_TEXT_FILE = os.path.join(os.getcwd(), 'tests', 'zen.txt')


class TestGUI(unittest.TestCase):
    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.mw = MainWindow()
        self.orig_conf = self.mw.conf

    def test_load_empty_directory(self):
        load_setting_btn = self.mw.ui.btnSettings
        # QtTest.QTest.mouseClick(load_setting_btn, QtCore.Qt.LeftButton)
        QtCore.QMetaObject.invokeMethod(self.mw.ui.btnSettings, 'click', QtCore.Qt.QueuedConnection)
        print self.app.allWidgets()

    def tearDown(self):
        self.mw.conf = self.orig_conf
        self.mw.save_conf()


if __name__ == '__main__':
    unittest.main()