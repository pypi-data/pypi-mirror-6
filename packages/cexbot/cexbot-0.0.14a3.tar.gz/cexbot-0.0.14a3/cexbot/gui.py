#!/usr/bin/env python

"""cexbot.gui
"""

import sys

from PyQt4 import QtCore, QtGui

from qtui.main import *

def main():
	app = QtGui.QApplication(sys.argv)
	window = QtGui.QDialog()
	f = Ui_formMain()
	f.setupUi(window)
	window.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()