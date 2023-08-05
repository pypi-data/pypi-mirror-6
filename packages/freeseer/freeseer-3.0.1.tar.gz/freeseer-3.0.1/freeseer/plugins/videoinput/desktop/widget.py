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

from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QWidget

class ConfigWidget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QFormLayout()
        self.setLayout(layout)
        
        self.desktopLabel = QLabel("Record Desktop")
        self.desktopButton = QRadioButton()
        layout.addRow(self.desktopLabel, self.desktopButton)
        
        # Record Area of Desktop
        areaGroup = QHBoxLayout()
        self.areaLabel = QLabel("Record Region")
        self.areaButton = QRadioButton()
        self.setAreaButton = QPushButton("Set")
        areaGroup.addWidget(self.areaButton)
        areaGroup.addWidget(self.setAreaButton)
        layout.addRow(self.areaLabel, areaGroup)
        
        # Select screen to record
        self.screenLabel = QLabel("Screen")
        self.screenSpinBox = QSpinBox()
        layout.addRow(self.screenLabel, self.screenSpinBox)
