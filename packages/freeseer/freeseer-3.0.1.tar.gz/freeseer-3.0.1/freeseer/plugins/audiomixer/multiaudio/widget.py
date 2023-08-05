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

@author: Aaron Brubacher
'''

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QWidget

class ConfigWidget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QGridLayout()
        self.setLayout(layout)
        
        self.source1_label = QLabel('Source 1')
        self.source1_combobox = QComboBox()
        self.source1_combobox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.source1_button = QToolButton() 
        self.source1_button.setText("Settings")
        configIcon = QIcon.fromTheme("preferences-other")
        self.source1_button.setIcon(configIcon)
        self.source1_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.source1_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.source1_stack = QStackedWidget()
        blankWidget = QWidget()
        self.source1_stack.addWidget(blankWidget)
        self.source1_stack.addWidget(self.source1_button)
        layout.addWidget(self.source1_label, 0, 0)
        layout.addWidget(self.source1_combobox, 0, 1)
        layout.addWidget(self.source1_stack, 0, 2)
        
        self.source2_label = QLabel('Source 2')
        self.source2_combobox = QComboBox()
        self.source2_combobox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.source2_button = QToolButton() 
        self.source2_button.setText("Settings")
        self.source2_button.setIcon(configIcon)  # reuse icon from source1
        self.source2_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.source2_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.source2_stack = QStackedWidget()
        blankWidget = QWidget()
        self.source2_stack.addWidget(blankWidget)
        self.source2_stack.addWidget(self.source2_button)
        layout.addWidget(self.source2_label, 1, 0)
        layout.addWidget(self.source2_combobox, 1, 1)
        layout.addWidget(self.source2_stack, 1, 2)

