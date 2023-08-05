#!/usr/bin/python
# -*- coding: utf-8 -*-

# freeseer - vga/presentation capture software
#
#  Copyright (C) 2011  Free and Open Source Software Learning Centre
#  http://fosslc.org
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# For support, questions, suggestions or any other inquiries, visit:
# http://wiki.github.com/Freeseer/freeseer/

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from freeseer import __version__, NAME, URL
from freeseer.frontend.qtcommon.Resource import resource_rc

RECORD_BUTTON_ARTIST=u'Sekkyumu'
RECORD_BUTTON_LINK=u'http://sekkyumu.deviantart.com/'
HEADPHONES_ARTIST=u'Ben Fleming'
HEADPHONES_LINK=u'http://mediadesign.deviantart.com/'

class AboutDialog(QtGui.QDialog):
    """
    Common About Dialog for the Freeseer Project. This should be used for the
    about dialog when including one in GUIs.
    
    
    Grid Layout:
    
    Logo  |  About Infos
    ------|-------------
          |  Close Button
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.current_language = "en_US"
        self.uiTranslator = QtCore.QTranslator()
        self.uiTranslator.load(":/languages/tr_en_US.qm")
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/freeseer/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        
        # Left Top corner of grid, Logo
        self.logo = QtGui.QLabel("Logo")
        self.logo.setPixmap(QtGui.QPixmap(_fromUtf8(":/freeseer/logo.png")))
        self.layout.addWidget(self.logo, 0, 0)
        
        # Right Top corner of grid, Infos
        self.aboutInfo = QtGui.QLabel("About Info", openExternalLinks=True)
        self.aboutInfo.setWordWrap(True)
        self.layout.addWidget(self.aboutInfo, 0, 1)
        
        # Right Bottom corner of grid, Close Button
        self.buttonBox = QtGui.QDialogButtonBox()
        self.closeButton = self.buttonBox.addButton("Close", QtGui.QDialogButtonBox.AcceptRole)
        self.layout.addWidget(self.buttonBox, 1, 1)
        self.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self.close)
        
        self.retranslate()
        
    def retranslate(self, language=None):
        if language is not None:
            self.current_language = language
        
        self.uiTranslator.load(":/languages/tr_%s.qm" % self.current_language)
        
        self.setWindowTitle(self.uiTranslator.translate("AboutDialog", "Freeseer About"))
        self.closeButton.setText(self.uiTranslator.translate("AboutDialog", "Close"))
        
        #
        # Main Text
        #
        self.descriptionString = self.uiTranslator.translate("AboutDialog",
                    "Freeseer is a video capture utility capable of capturing presentations. It captures video "
                    "sources such as usb, firewire, or local desktop along with audio and mixes them together to "
                    "produce a video.")
        self.copyrightString = self.uiTranslator.translate("AboutDialog", 'Copyright (C) 2011-2013 The Free and Open Source Software Learning Centre')
        self.licenseTextString = self.uiTranslator.translate("AboutDialog", "Freeseer is licensed under the GPL version 3. This software is provided 'as-is',"
                    "without any express or implied warranty. In no event will the authors be held liable for any "
                    "damages arising from the use of this software.")
        
        self.aboutInfoString = u'<h1>'+NAME+u'</h1>' + \
        u'<br><b>'+ self.uiTranslator.translate("AboutDialog", "Version")+":" + __version__ + u'</b>' + \
        u'<p>' + self.descriptionString + u'</p>' + \
        u'<p>' + self.copyrightString + u'</p>' + \
        u'<p><a href="'+URL+u'">' + URL + u'</a></p>' \
        u'<p>' + self.licenseTextString + u'</p>' \
        u'<p>' + self.uiTranslator.translate("AboutDialog", "Record button graphics by") + ': <a href="' + RECORD_BUTTON_LINK+ u'">' + RECORD_BUTTON_ARTIST + u'</a></p>' \
        u'<p>'+ self.uiTranslator.translate("AboutDialog", "Headphones graphics by") + ': <a href="' + HEADPHONES_LINK+ u'">' + HEADPHONES_ARTIST + u'</a></p>'
        
        self.aboutInfo.setText(self.aboutInfoString)
        # --- End Main Text
