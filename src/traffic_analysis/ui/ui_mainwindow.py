# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateEdit,
    QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpinBox, QSplitter, QStatusBar,
    QTabWidget, QTableView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1440, 900)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.sidebar = QWidget(self.splitter)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMinimumSize(QSize(330, 0))
        self.sideLayout = QVBoxLayout(self.sidebar)
        self.sideLayout.setObjectName(u"sideLayout")
        self.sideLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLabel = QLabel(self.sidebar)
        self.titleLabel.setObjectName(u"titleLabel")

        self.sideLayout.addWidget(self.titleLabel)

        self.sourceGroup = QGroupBox(self.sidebar)
        self.sourceGroup.setObjectName(u"sourceGroup")
        self.sourceLayout = QVBoxLayout(self.sourceGroup)
        self.sourceLayout.setObjectName(u"sourceLayout")
        self.dirLayout = QHBoxLayout()
        self.dirLayout.setObjectName(u"dirLayout")
        self.dirEdit = QLineEdit(self.sourceGroup)
        self.dirEdit.setObjectName(u"dirEdit")

        self.dirLayout.addWidget(self.dirEdit)

        self.browseButton = QPushButton(self.sourceGroup)
        self.browseButton.setObjectName(u"browseButton")

        self.dirLayout.addWidget(self.browseButton)


        self.sourceLayout.addLayout(self.dirLayout)

        self.refreshButton = QPushButton(self.sourceGroup)
        self.refreshButton.setObjectName(u"refreshButton")

        self.sourceLayout.addWidget(self.refreshButton)

        self.fileList = QListWidget(self.sourceGroup)
        self.fileList.setObjectName(u"fileList")
        self.fileList.setMinimumSize(QSize(0, 160))

        self.sourceLayout.addWidget(self.fileList)


        self.sideLayout.addWidget(self.sourceGroup)

        self.parameterGroup = QGroupBox(self.sidebar)
        self.parameterGroup.setObjectName(u"parameterGroup")
        self.parameterLayout = QFormLayout(self.parameterGroup)
        self.parameterLayout.setObjectName(u"parameterLayout")
        self.startLabel = QLabel(self.parameterGroup)
        self.startLabel.setObjectName(u"startLabel")

        self.parameterLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.startLabel)

        self.startDateEdit = QDateEdit(self.parameterGroup)
        self.startDateEdit.setObjectName(u"startDateEdit")
        self.startDateEdit.setDate(QDate(2016, 8, 1))
        self.startDateEdit.setCalendarPopup(True)

        self.parameterLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.startDateEdit)

        self.roadLabel = QLabel(self.parameterGroup)
        self.roadLabel.setObjectName(u"roadLabel")

        self.parameterLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.roadLabel)

        self.roadSpin = QSpinBox(self.parameterGroup)
        self.roadSpin.setObjectName(u"roadSpin")
        self.roadSpin.setMaximum(999999)

        self.parameterLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.roadSpin)

        self.typicalLabel = QLabel(self.parameterGroup)
        self.typicalLabel.setObjectName(u"typicalLabel")

        self.parameterLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.typicalLabel)

        self.typicalCombo = QComboBox(self.parameterGroup)
        self.typicalCombo.addItem("")
        self.typicalCombo.addItem("")
        self.typicalCombo.addItem("")
        self.typicalCombo.addItem("")
        self.typicalCombo.setObjectName(u"typicalCombo")

        self.parameterLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.typicalCombo)

        self.dateLabel = QLabel(self.parameterGroup)
        self.dateLabel.setObjectName(u"dateLabel")

        self.parameterLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.dateLabel)

        self.dateSpin = QSpinBox(self.parameterGroup)
        self.dateSpin.setObjectName(u"dateSpin")
        self.dateSpin.setMaximum(99999)

        self.parameterLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.dateSpin)

        self.clusterLabel = QLabel(self.parameterGroup)
        self.clusterLabel.setObjectName(u"clusterLabel")

        self.parameterLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.clusterLabel)

        self.clusterSpin = QSpinBox(self.parameterGroup)
        self.clusterSpin.setObjectName(u"clusterSpin")
        self.clusterSpin.setMinimum(2)
        self.clusterSpin.setMaximum(30)
        self.clusterSpin.setValue(4)

        self.parameterLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.clusterSpin)

        self.zLabel = QLabel(self.parameterGroup)
        self.zLabel.setObjectName(u"zLabel")

        self.parameterLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.zLabel)

        self.zSpin = QDoubleSpinBox(self.parameterGroup)
        self.zSpin.setObjectName(u"zSpin")
        self.zSpin.setMinimum(1.000000000000000)
        self.zSpin.setMaximum(10.000000000000000)
        self.zSpin.setSingleStep(0.500000000000000)
        self.zSpin.setValue(3.000000000000000)

        self.parameterLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.zSpin)

        self.zeroMissingCheck = QCheckBox(self.parameterGroup)
        self.zeroMissingCheck.setObjectName(u"zeroMissingCheck")

        self.parameterLayout.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.zeroMissingCheck)


        self.sideLayout.addWidget(self.parameterGroup)

        self.analyzeButton = QPushButton(self.sidebar)
        self.analyzeButton.setObjectName(u"analyzeButton")
        self.analyzeButton.setMinimumSize(QSize(0, 38))

        self.sideLayout.addWidget(self.analyzeButton)

        self.chartGroup = QGroupBox(self.sidebar)
        self.chartGroup.setObjectName(u"chartGroup")
        self.chartLayout = QVBoxLayout(self.chartGroup)
        self.chartLayout.setObjectName(u"chartLayout")
        self.chartList = QListWidget(self.chartGroup)
        self.chartList.setObjectName(u"chartList")
        self.chartList.setMinimumSize(QSize(0, 190))

        self.chartLayout.addWidget(self.chartList)


        self.sideLayout.addWidget(self.chartGroup)

        self.saveFigureButton = QPushButton(self.sidebar)
        self.saveFigureButton.setObjectName(u"saveFigureButton")

        self.sideLayout.addWidget(self.saveFigureButton)

        self.splitter.addWidget(self.sidebar)
        self.resultTabs = QTabWidget(self.splitter)
        self.resultTabs.setObjectName(u"resultTabs")
        self.chartTab = QWidget()
        self.chartTab.setObjectName(u"chartTab")
        self.plotLayout = QVBoxLayout(self.chartTab)
        self.plotLayout.setObjectName(u"plotLayout")
        self.resultTabs.addTab(self.chartTab, "")
        self.summaryTab = QWidget()
        self.summaryTab.setObjectName(u"summaryTab")
        self.summaryLayout = QVBoxLayout(self.summaryTab)
        self.summaryLayout.setObjectName(u"summaryLayout")
        self.summaryText = QPlainTextEdit(self.summaryTab)
        self.summaryText.setObjectName(u"summaryText")
        self.summaryText.setReadOnly(True)

        self.summaryLayout.addWidget(self.summaryText)

        self.resultTabs.addTab(self.summaryTab, "")
        self.tableTab = QWidget()
        self.tableTab.setObjectName(u"tableTab")
        self.tableLayout = QVBoxLayout(self.tableTab)
        self.tableLayout.setObjectName(u"tableLayout")
        self.tableHint = QLabel(self.tableTab)
        self.tableHint.setObjectName(u"tableHint")

        self.tableLayout.addWidget(self.tableHint)

        self.tableView = QTableView(self.tableTab)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setSortingEnabled(True)

        self.tableLayout.addWidget(self.tableView)

        self.resultTabs.addTab(self.tableTab, "")
        self.qualityTab = QWidget()
        self.qualityTab.setObjectName(u"qualityTab")
        self.qualityLayout = QVBoxLayout(self.qualityTab)
        self.qualityLayout.setObjectName(u"qualityLayout")
        self.qualityText = QPlainTextEdit(self.qualityTab)
        self.qualityText.setObjectName(u"qualityText")
        self.qualityText.setReadOnly(True)

        self.qualityLayout.addWidget(self.qualityText)

        self.resultTabs.addTab(self.qualityTab, "")
        self.splitter.addWidget(self.resultTabs)

        self.horizontalLayout.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Traffic Spatiotemporal Analysis Platform", None))
        self.titleLabel.setStyleSheet(QCoreApplication.translate("MainWindow", u"font-size: 18px; font-weight: 600;", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"Data and Analysis Controls", None))
        self.sourceGroup.setTitle(QCoreApplication.translate("MainWindow", u"1. Data Source", None))
        self.dirEdit.setText(QCoreApplication.translate("MainWindow", u"datasets", None))
        self.browseButton.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.refreshButton.setText(QCoreApplication.translate("MainWindow", u"Refresh Sources", None))
        self.parameterGroup.setTitle(QCoreApplication.translate("MainWindow", u"2. Analysis Parameters", None))
        self.startLabel.setText(QCoreApplication.translate("MainWindow", u"Start date", None))
        self.startDateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.roadLabel.setText(QCoreApplication.translate("MainWindow", u"Road ID", None))
        self.typicalLabel.setText(QCoreApplication.translate("MainWindow", u"Auto road", None))
        self.typicalCombo.setItemText(0, QCoreApplication.translate("MainWindow", u"Manual road ID", None))
        self.typicalCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"Lowest mean speed", None))
        self.typicalCombo.setItemText(2, QCoreApplication.translate("MainWindow", u"Highest mean speed", None))
        self.typicalCombo.setItemText(3, QCoreApplication.translate("MainWindow", u"Closest to overall mean", None))

        self.dateLabel.setText(QCoreApplication.translate("MainWindow", u"Day index", None))
        self.clusterLabel.setText(QCoreApplication.translate("MainWindow", u"Clusters", None))
        self.zLabel.setText(QCoreApplication.translate("MainWindow", u"Anomaly Z threshold", None))
        self.zeroMissingCheck.setText(QCoreApplication.translate("MainWindow", u"Treat zero as suspected missing", None))
        self.analyzeButton.setStyleSheet(QCoreApplication.translate("MainWindow", u"font-weight: 600;", None))
        self.analyzeButton.setText(QCoreApplication.translate("MainWindow", u"Load and Analyze Current Data", None))
        self.chartGroup.setTitle(QCoreApplication.translate("MainWindow", u"3. Analysis Charts", None))
        self.saveFigureButton.setText(QCoreApplication.translate("MainWindow", u"Save Current Chart as PNG...", None))
        self.resultTabs.setTabText(self.resultTabs.indexOf(self.chartTab), QCoreApplication.translate("MainWindow", u"Chart", None))
        self.resultTabs.setTabText(self.resultTabs.indexOf(self.summaryTab), QCoreApplication.translate("MainWindow", u"Analysis Summary", None))
        self.tableHint.setText(QCoreApplication.translate("MainWindow", u"The result table follows the selected analysis chart.", None))
        self.resultTabs.setTabText(self.resultTabs.indexOf(self.tableTab), QCoreApplication.translate("MainWindow", u"Result Table", None))
        self.resultTabs.setTabText(self.resultTabs.indexOf(self.qualityTab), QCoreApplication.translate("MainWindow", u"Data Inspection", None))
    # retranslateUi

