import sys
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import *
from synthesizer import *



class MainWindow(QMainWindow):

    synthesizer = Synthesizer()
    synthesizer.arm()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initMainWidget(self):
        layout = QGridLayout()
        mainWidget = QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)

        tabwidget = QTabWidget()
        layout.addWidget(tabwidget)

        # Play tab
        playTab = QWidget()
        playTabLayout = QVBoxLayout()
        playTab.setLayout(playTabLayout)

        label1 = QLabel("Widget in Tab 1.")
        playTabLayout.addWidget(label1)

        ''' <-------------------- SOUND DESIGN TAB --------------------> '''
        oscillatorsTab = QWidget()
        oscillatorsTabLayout = QVBoxLayout()
        oscillatorsTab.setLayout(oscillatorsTabLayout)

        '''UPPER OSCILLATOR LAYOUT'''
        upperOscillatorsTabLayout = QGridLayout()
        #upperOscillatorsTabLayout.setRowStretch(0, 1)
        #upperOscillatorsTabLayout.setRowStretch(1, 1)
        #upperOscillatorsTabLayout.setRowStretch(2, 1)
        #upperOscillatorsTabLayout.setRowStretch(3, 1)
        oscillatorsTabLayout.addLayout(upperOscillatorsTabLayout)

        # oscillator 1 waveform selector
        oscillator1DropDownLabel = QLabel("Waveform")
        oscillator1DropDownLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillator1DropDownLabel, 0, 0)

        oscillator1DropDown = QComboBox()
        oscillator1DropDown.addItems(Synthesizer.waveforms)
        oscillator1DropDown.setCurrentIndex(0)
        oscillator1DropDown.activated.connect(self.oscillator1ShapeChanged)
        upperOscillatorsTabLayout.addWidget(oscillator1DropDown, 1, 0)

        # oscillator 2 waveform selector
        oscillator2DropDownLabel = QLabel("Waveform")
        oscillator2DropDownLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillator2DropDownLabel, 2, 0)

        oscillator2DropDown = QComboBox()
        oscillator2DropDown.addItems(Synthesizer.waveforms)
        oscillator2DropDown.setCurrentIndex(0)
        oscillator2DropDown.activated.connect(self.oscillator2ShapeChanged)
        upperOscillatorsTabLayout.addWidget(oscillator2DropDown, 3, 0)

        # oscillator 1 pitch dial
        oscillator1PitchLabel = QLabel("Pitch")
        oscillator1PitchLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillator1PitchLabel, 0, 1)

        self.oscillator1PitchDial = QDial()
        self.oscillator1PitchDial.setMinimum(-12)
        self.oscillator1PitchDial.setMaximum(12)
        self.oscillator1PitchDial.setValue(0)
        self.oscillator1PitchDial.valueChanged.connect(self.oscillator1PitchChanged)
        upperOscillatorsTabLayout.addWidget(self.oscillator1PitchDial, 1, 1)

        # oscillator 2 pitch dial
        oscillator2PitchLabel = QLabel("Pitch")
        oscillator2PitchLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillator2PitchLabel, 2, 1)

        self.oscillator2PitchDial = QDial()
        self.oscillator2PitchDial.setMinimum(-12)
        self.oscillator2PitchDial.setMaximum(12)
        self.oscillator2PitchDial.setValue(0)
        self.oscillator2PitchDial.valueChanged.connect(self.oscillator2PitchChanged)
        upperOscillatorsTabLayout.addWidget(self.oscillator2PitchDial, 3, 1)

        # oscillator ratio slider
        oscillatorRatioLabel = QLabel("Ratio")
        oscillatorRatioLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillatorRatioLabel, 0, 2)
        self.oscillatorRatioSlider = QSlider(Qt.Orientation.Vertical)
        self.oscillatorRatioSlider.setMinimum(0)
        self.oscillatorRatioSlider.setMaximum(100)
        self.oscillatorRatioSlider.setValue(50)
        self.oscillatorRatioSlider.valueChanged.connect(self.ratioChanged)
        upperOscillatorsTabLayout.addWidget(self.oscillatorRatioSlider, 1, 2, 3, 1)

        # oscillator volume dial
        oscillatorVolumeLabel = QLabel("Volume")
        oscillatorVolumeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillatorVolumeLabel, 0, 3)

        self.volumeDial = QDial()
        self.volumeDial.setMinimum(0)
        self.volumeDial.setMaximum(100)
        self.volumeDial.setValue(100)
        self.volumeDial.valueChanged.connect(self.volumeChanged)
        upperOscillatorsTabLayout.addWidget(self.volumeDial, 1, 3)

        # oscillator cutoff dial
        oscillatorCutoffLabel = QLabel("Cutoff")
        oscillatorCutoffLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upperOscillatorsTabLayout.addWidget(oscillatorCutoffLabel, 2, 3)

        self.cutoffDial = QDial()
        self.cutoffDial.setMinimum(0)
        self.cutoffDial.setMaximum(100)
        self.cutoffDial.setValue(100)
        self.cutoffDial.valueChanged.connect(self.volumeChanged)
        upperOscillatorsTabLayout.addWidget(self.cutoffDial, 3, 3)

        tabwidget.addTab(playTab, "Play")
        tabwidget.addTab(oscillatorsTab, "Oscillators")

        #tabwidget.currentChanged.connect(self.onChange)

    def volumeChanged(self):
        self.synthesizer.setVolume(self.volumeDial.value() / 100)

    def oscillator1ShapeChanged(self, index):
        self.synthesizer.setOscillator1Waveform(index)
    
    def oscillator2ShapeChanged(self, index):
        self.synthesizer.setOscillator2Waveform(index)

    def oscillator1PitchChanged(self, index):
        self.synthesizer.setOscillator1Pitch(index)
    
    def oscillator2PitchChanged(self, index):
        self.synthesizer.setOscillator2Pitch(index)

    def ratioChanged(self):
        self.synthesizer.setOscillatorRatio(self.oscillatorRatioSlider.value() / 100)
    
    def setCutoff(self):
        self.synthesizer.setCutoff(self.oscillatorRatioSlider.value() / 100)

    def onChange(self, tabIndex):
        '''
        if tabIndex == 0:
            self.synthesizer.arm()
        else:
            self.synthesizer.dearm()
            '''

    ''' <-------------------- KEYBOARD INTERACTION --------------------> '''
    keys = [
    Qt.Key.Key_Z, Qt.Key.Key_S, Qt.Key.Key_X, Qt.Key.Key_D, Qt.Key.Key_C, Qt.Key.Key_V, Qt.Key.Key_G, Qt.Key.Key_B, Qt.Key.Key_H, Qt.Key.Key_N, Qt.Key.Key_J, Qt.Key.Key_M,
    Qt.Key.Key_Comma
    ]

    keymappings = {}
    for i in range(len(keys)):
        keymappings[keys[i]] = i + Synthesizer.C5

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        note = self.keymappings.get(event.key(), None)
        if note != None:
            self.synthesizer.playNote(note)

        event.accept()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        note = self.keymappings.get(event.key(), None)
        if note != None:
            self.synthesizer.stopNote(note)
        event.accept()

    def initUI(self):
        
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.instance().quit)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("bug.png"), "Arm Synthesizer", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.toggleArmSynthesizer)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)

        self.initMainWidget()

        self.resize(800, 800)
        self.center()

        self.setWindowTitle('Synthesizer')
        self.show()

    def toggleArmSynthesizer(self, s):
        if (s == True):
            self.synthesizer.arm()
        else:
            self.synthesizer.dearm()

    def center(self):

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

