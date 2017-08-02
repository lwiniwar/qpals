"""
/***************************************************************************
Name			 	 : qpals lidar tools
Description          : integrates the opals software as a qgis plugin
Date                 : 04/Oct/15 
copyright            : (C) 2015 by Lukas Winiwarter/TU Wien
email                : lukas.winiwarter@tuwien.ac.at 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import tempfile

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import QpalsLog
import QpalsProject
import QpalsShowFile
import moduleSelector
from modules import QpalsSection, QpalsLM, QpalsAttributeMan


class qpals:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.active = True
        self.layerlist = dict()
        QgsProject.instance().readProject.connect(self.projectloaded)
        s = QSettings()
        proj = QgsProject.instance()
        opalspath = s.value("qpals/opalspath", "")
        tempdir = proj.readEntry("qpals","tempdir", tempfile.gettempdir())[0]
        workdir = proj.readEntry("qpals","workdir", tempfile.gettempdir())[0]
        firstrun = False
        while opalspath == "":
            msg = QMessageBox()
            msg.setText("The path to the opals binaries has not been set.")
            msg.setInformativeText("Please set it now, or press cancel to unload the qpals plugin.")
            msg.setWindowTitle("Qpals opals path")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec_()
            if ret == QMessageBox.Ok:
                opalspath = QFileDialog.getExistingDirectory(None, caption='Select path containing opals*.exe binaries')
                if opalspath:
                    if os.path.exists(os.path.join(opalspath, "opalsCell.exe")):
                        s.setValue("qpals/opalspath", opalspath)
                        firstrun = True
                    else:
                        opalspath = ""
                        msg = QMessageBox()
                        msg.setText("Ooops..")
                        msg.setInformativeText("Could not validate opals path. Please make sure to select the folder "
                                               "containing the opals binaries, i.e. opalsCell.exe, opalsInfo.exe, etc.")
                        msg.setWindowTitle("Qpals opals path")
                        msg.setStandardButtons(QMessageBox.Ok)
                        ret = msg.exec_()

            else:
                self.active = False

        if self.active:
            self.prjSet = QpalsProject.QpalsProject(name="", opalspath=opalspath,
                                                    tempdir=tempdir, workdir=workdir, iface=self.iface)

        if firstrun:
            self.showproject()

    def __del__(self):
        pass

    def projectloaded(self):
        proj = QgsProject.instance()
        tempdir = proj.readEntry("qpals","tempdir", "")[0]
        workdir = proj.readEntry("qpals","workdir", "")[0]
        vismethod = proj.readNumEntry("qpals", "vismethod", -1)[0]
        if tempdir:
            self.prjSet.tempdir = tempdir
        if workdir:
            self.prjSet.workdir = workdir
        if vismethod:
            self.prjSet.vismethod = vismethod
            self.dropobject.visMethod.setCurrentIndex(vismethod)


    def showModuleSelector(self):
        self.modSel = moduleSelector.moduleSelector(self.iface, self.layerlist, self.prjSet)
        self.modSelWindow = QDockWidget("Qpals Module Selector", self.iface.mainWindow(), Qt.WindowMinimizeButtonHint)
        self.modSelWindow.setWidget(self.modSel)
        self.modSelWindow.setAllowedAreas(Qt.NoDockWidgetArea)  # don't let it dock
        self.modSelWindow.setMinimumSize(800, 400)
        self.modSelWindow.setFloating(True)
        self.modSelWindow.show()

    def showproject(self):
        self.prjUI = self.prjSet.getUI()
        self.prjUI.show()

    def showdd(self):
        import qpals.qt_extensions.QpalsDropTextbox
        self.drop = qpals.QpalsDropTextbox.droptester()
        self.drop.show()

    def showlog(self):
        import webbrowser
        webbrowser.open('file:///' + os.path.join(self.prjSet.tempdir, "opalsLog.xml"))
        #self.log = QpalsLog.QpalsLog(iface=self.iface)
        #self.log.ui.show()

    def clearlog(self):
        try:
            os.remove(os.path.join(self.prjSet.tempdir, "opalsLog.xml"))
        except Exception as e:
            self.iface.messageBar().pushMessage('Something went wrong! See the message log for more information.',
                                                duration=3)
            print e

    def showAttrMan(self):
        self.attrman = QpalsAttributeMan.QpalsAttributeMan(project=self.prjSet,
                                                           layerlist=self.layerlist,
                                                           iface=self.iface)
        self.attrman.ui.show()

    def showSecGUI(self):
        self.sec = QpalsSection.QpalsSection(project=self.prjSet, layerlist=self.layerlist, iface=self.iface)
        self.secUI = self.sec.createWidget()
        self.secUIDock = QDockWidget("Qpals Section GUI", self.iface.mainWindow())
        self.secUIDock.setWidget(self.secUI)
        self.secUIDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.secUIDock.setFloating(True)
        self.secUIDock.show()

    def showLMGUI(self):
        self.linemodeler = QpalsLM.QpalsLM(project=self.prjSet, layerlist=self.layerlist, iface=self.iface)
        self.linemodelerUI = self.linemodeler.createWidget()
        self.linemodelerUIDock = QDockWidget("Qpals LineModeler GUI", self.iface.mainWindow())
        self.linemodelerUIDock.setWidget(self.linemodelerUI)
        self.linemodelerUIDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.linemodelerUIDock.setFloating(True)
        self.linemodelerUIDock.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.linemodelerUIDock.show()


    def initGui(self):
        if self.active:
            self.menu = QMenu(self.iface.mainWindow())
            self.menu.setObjectName("qpalsMenu")
            self.menu.setTitle("qpals")

            IconPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "media")
            opalsIcon = QIcon(os.path.join(IconPath, "opalsIcon.png"))

            self.menuItemModuleSelector = QAction(opalsIcon, "Module Selector", self.iface.mainWindow())
            self.menuItemModuleSelector.setWhatsThis("Select a module from a list")
            self.menuItemModuleSelector.setStatusTip("Select module from list")
            QObject.connect(self.menuItemModuleSelector, SIGNAL("triggered()"), self.showModuleSelector)
            self.menu.addAction(self.menuItemModuleSelector)

            self.logmnu = QMenu(self.menu)
            self.logmnu.setIcon(opalsIcon)
            self.logmnu.setObjectName("qpalsLogMenu")
            self.logmnu.setTitle("opalsLog")

            self.mnulog = QAction(opalsIcon, "show opalsLog.xml", self.iface.mainWindow())
            self.mnulog.setStatusTip("Show log information")
            QObject.connect(self.mnulog, SIGNAL("triggered()"), self.showlog)
            self.logmnu.addAction(self.mnulog)

            self.mnuclearlog = QAction(opalsIcon, "clear opalsLog.xml", self.iface.mainWindow())
            self.mnuclearlog.setStatusTip("Delete log file")
            self.mnuclearlog.triggered.connect(self.clearlog)
            self.logmnu.addAction(self.mnuclearlog)

            self.menu.addMenu(self.logmnu)


            self.mnuproject = QAction(opalsIcon, "Project settings", self.iface.mainWindow())
            self.mnuproject.setStatusTip("Project settings")
            QObject.connect(self.mnuproject, SIGNAL("triggered()"), self.showproject)
            self.menu.addAction(self.mnuproject)

            self.mnusec = QAction(opalsIcon, "Section GUI", self.iface.mainWindow())
            self.mnusec.setStatusTip("Project settings")
            QObject.connect(self.mnusec, SIGNAL("triggered()"), self.showSecGUI)
            self.menu.addAction(self.mnusec)

            self.mnulm = QAction(opalsIcon, "LineModeller GUI", self.iface.mainWindow())
            self.mnulm.setStatusTip("Start the LineModeller GUI")
            QObject.connect(self.mnulm, SIGNAL("triggered()"), self.showLMGUI)
            self.menu.addAction(self.mnulm)

            self.mnuatt = QAction(opalsIcon, "Attribute Manager", self.iface.mainWindow())
            self.mnuatt.setStatusTip("Start the attribute manager")
            QObject.connect(self.mnuatt, SIGNAL("triggered()"), self.showAttrMan)
            self.menu.addAction(self.mnuatt)

            menuBar = self.iface.mainWindow().menuBar()
            menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu)

            self.dropspace = QDockWidget("Qpals Visualizer", self.iface.mainWindow())
            self.dropspace.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            self.dropobject = QpalsShowFile.QpalsShowFile(self.iface, self.layerlist, self.prjSet)
            self.dropobject.initUI()
            self.dropspace.setWidget(self.dropobject.ui)
            self.iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dropspace)
            self.dropspace.setContentsMargins(9, 9, 9, 9)
            #self.dropspace.removeEventFilter(self.iface.mainWindow())


    def unload(self):
        if self.active:
            # Remove the plugin menu item and icon
            self.menu.deleteLater()
            self.dropspace.deleteLater()
