#!/usr/bin/python3


import math
import sqlite3

from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
		QSizeF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
		QPainterPath, QPen, QPixmap, QPolygonF)
from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QComboBox,
		QFontComboBox, QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem,
		QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
		QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QSizePolicy,
		QToolBox, QToolButton, QWidget, QTreeView, QSplitter)

from logging import warning, error, info

from ProductionLineScene import ProcessGraphic, ConstructProcessGraphicTree, FillScene
from ProductionScheme import ProductionScheme
from ProductionLine import ProductionLine
from Processes import LoadBlueprint, LoadRefine
from ToolkitTypes import ToolkitTypes
from EveTypesModel import EveTypesModel
from MarketGroup import MarketGroup, LazyMarketGroup
from ProcessesFilterModel import ProcessesFilterModel


class MainWindow(QMainWindow):
 
	def __init__(self):
		super(MainWindow, self).__init__()

		self.toolkitTypes = ToolkitTypes()

		dbFileName = "Eve toolkit/DATADUMP201403101147.db"
		connection = sqlite3.connect(dbFileName)
		self.productionLine = None

		
		#Tree view setup
		treeRoot = MarketGroup("Type")

		treeRoot.AppendChild(LazyMarketGroup(2, "Blueprints", treeRoot, connection))
		treeRoot.AppendChild(LazyMarketGroup(54, "Ore", treeRoot, connection))
		treeRoot.AppendChild(LazyMarketGroup(493, "Ice Ore", treeRoot, connection))

		model = EveTypesModel(treeRoot)
		self.filterModel = ProcessesFilterModel()
		self.filterModel.setSourceModel(model)
		
		self.treeView = QTreeView()
		self.treeView.doubleClicked.connect(self.OnTreeDoubleClick)
		self.treeView.setModel(self.filterModel)


		self.scene = QGraphicsScene()
		self.view = QGraphicsView(self.scene)
		self.view.setMinimumWidth(500)

		splitter = QSplitter()
		splitter.addWidget(self.treeView)
		splitter.addWidget(self.view)

		self.setCentralWidget(splitter)
		self.setWindowTitle("EveGant")

		self.createMenus()
		self.createToolbars()

	def TempFillIn(self):
		self.productionLine = ProductionLine(LoadBlueprint(connection.cursor(), 20188, None))
		self.productionLine.AddProcess(LoadBlueprint(connection.cursor(), 21010, None))
		self.productionLine.AddProcess(LoadBlueprint(connection.cursor(), 21018, None))
		self.productionLine.AddProcess(LoadBlueprint(connection.cursor(), 21028, None))
		self.productionLine.AddProcess(LoadBlueprint(connection.cursor(), 21038, None))

		self.productionLine.AddProcess(LoadRefine(connection.cursor(), 1228, None))
		self.productionLine.AddProcess(LoadRefine(connection.cursor(), 18, None))
		self.productionLine.AddProcess(LoadRefine(connection.cursor(), 1227, None))
		self.productionLine.AddProcess(LoadRefine(connection.cursor(), 1224, None))


	def	SetupGraphView(self):
		graphics = [ProcessGraphic(process, self.toolkitTypes) for process in self.productionLine.processes]
		ConstructProcessGraphicTree(graphics)

		FillScene(self.scene, graphics)			
		

	def OnTreeDoubleClick(self, aIndex):
		data = self.treeView.model().data(aIndex, Qt.UserRole)

		if data.GetChildCount() == 0:
			if self.productionLine:
				self.productionLine.AddProcess(data)
			else:
				self.productionLine = ProductionLine(data)
			self.filterModel.outputs = self.productionLine.inputs
			self.filterModel.invalidateFilter()
			self.SetupGraphView()

	def sceneScaleChanged(self, scale):
		newScale = float(scale[:-1]) / 100.0
		oldMatrix = self.view.transform()
		self.view.resetTransform()
		self.view.translate(oldMatrix.dx(), oldMatrix.dy())
		self.view.scale(newScale, newScale)

	def about(self):
		QMessageBox.about(self, "EveGant", "Eve online industrial planning and traking tool")

	def createMenus(self):
		exitAction = QAction("E&xit", self, shortcut="Ctrl+X",
				statusTip="Quit Scenediagram example", triggered=self.close)

		aboutAction = QAction("A&bout", self, shortcut="Ctrl+B",
				triggered=self.about)

		fileMenu = self.menuBar().addMenu("&File")
		fileMenu.addAction(exitAction)

		aboutMenu = self.menuBar().addMenu("&Help")
		aboutMenu.addAction(aboutAction)

	def createToolbars(self):

		sceneScaleCombo = QComboBox()
		sceneScaleCombo.addItems(["50%", "75%", "100%", "125%", "150%"])
		sceneScaleCombo.setCurrentIndex(2)
		sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)

		pointerToolbar = self.addToolBar("Pointer type")
		pointerToolbar.addWidget(sceneScaleCombo)


if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	mainWindow = MainWindow()
	mainWindow.setGeometry(100, 100, 800, 500)
	mainWindow.show()

	sys.exit(app.exec_())
