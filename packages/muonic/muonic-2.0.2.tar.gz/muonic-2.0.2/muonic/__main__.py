#! /usr/bin/env python

# This file is part of muonic, a program to work with the QuarkDAQ cards
# Copyright (C) 2009  Robert Franke (robert.franke@desy.de)
#
# muonic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# muonic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with muonic. If not, see <http://www.gnu.org/licenses/>.


# The way of the communication between the serial port and the GUI is based on
# the receipt presented at http://code.activestate.com/recipes/82965/
# Created by Jacob Hallen, AB Strakt, Sweden. 2001-10-17
# Adapted by Boudewijn Rempt, Netherlands. 2002-04-15
# It is licenced under the Python licence, http://www.python.org/psf/license/

# python std lib imports
import sys
#import os
import logging
from optparse import OptionParser
#import Queue
#import multiprocessing as mult

# PyQt4 imports
#from PyQt4 import QtCore
from PyQt4 import QtGui

# muonic imports
#from muonic.daq.DaqConnection import DaqConnection
#from muonic.daq.SimDaqConnection import SimDaqConnection
from daq.DAQProvider import DAQProvider
from gui.MainWindow import MainWindow

def main(opts,logger):

    root = QtGui.QApplication(sys.argv)
    client = DAQProvider(opts,logger,root)
    # Set up the GUI part
    gui=MainWindow(client.outqueue, client.inqueue, logger, opts,root)
    gui.show()
    root.exec_()


if __name__ == '__main__':


    usage = """%prog [options] YOURINITIALS
               WARNING: You are going to use muonic directly from this package!
               We recommend to use your system installation!
               This should be only used for testing
               Setting debuglevel to DEBUG!
               -d option will have no effect!
               """

    parser = OptionParser(usage=usage)

    parser.add_option("-s", "--sim", action="store_true", dest="sim", help="use simulation mode for testing without hardware", default=False)
    parser.add_option("-d", "--debug", dest="loglevel", action="store_const", const=10 , help="switch to loglevel debug", default=10)

    opts, args = parser.parse_args()
    if (len(args) != 1) or (len(args[0]) != 2):
            parser.error("Incorrect number of arguments, you have to specify just the initials of your name for the filenames \n initials must be two letters!")

    # small ugly hack, mixing args and options...
    opts.user = args[0]

    # set up logging
    logger = logging.getLogger()
    logger.setLevel(int(opts.loglevel))
    ch = logging.StreamHandler()
    ch.setLevel(int(opts.loglevel))
    formatter = logging.Formatter('%(levelname)s:%(process)d:%(module)s:%(funcName)s:%(lineno)d:%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # make it so!
    main(opts,logger)
