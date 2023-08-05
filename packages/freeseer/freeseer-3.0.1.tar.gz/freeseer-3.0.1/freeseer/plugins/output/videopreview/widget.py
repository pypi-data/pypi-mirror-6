#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
freeseer - vga/presentation capture software

Copyright (C) 2013  Free and Open Source Software Learning Centre
http://fosslc.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For support, questions, suggestions or any other inquiries, visit:
http://wiki.github.com/Freeseer/freeseer/

@author: Thanh Ha
'''

from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget

class ConfigWidget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QFormLayout()
        self.setLayout(layout)

        # Preview
        self.previewLabel = QLabel("Preview")
        self.previewComboBox = QComboBox()
        self.previewComboBox.addItem("autovideosink")
        self.previewComboBox.addItem("ximagesink")
        self.previewComboBox.addItem("xvimagesink")
        self.previewComboBox.addItem("gconfvideosink")
        
        layout.addRow(self.previewLabel, self.previewComboBox)

        # Leaky Queue
        # Allows user to set queue in video to be leaky - required to work with RTMP streaming plugin
        self.leakyQueueLabel = QLabel("Leaky Queue")
        self.leakyQueueComboBox = QComboBox()
        
        layout.addRow(self.leakyQueueLabel, self.leakyQueueComboBox)
