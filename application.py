import sys
import numpy as np
import PyQt6
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from synthesizer import *
import pyqtgraph as pg

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.WindowDoesNotAcceptFocus)

    def eventFilter(self, source, event):
        print(event)
        if event.type() == QEvent.KeyPress:
            return False
            

class MainWindow(QMainWindow):
    synthesizer = Synthesizer()
    synthesizer.arm()

    plotLineColor = (150, 150, 150)
    plotLineWidth = 1

    spectrogramImage = np.zeros((100, len(synthesizer.generateSpectrogramData())))
    spectrogramImage[0:] = synthesizer.generateSpectrogramData()

    spectrogramScrollSpeed = int(1)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.setInterval(50) # spectrogram update interval (in ms)
        self.timer.timeout.connect(self.updateSpectrogramWidget)
        self.timer.start()

    def initMainWidget(self):
        layout = QGridLayout()
        mainWidget = QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)

        tabwidget = QTabWidget()
        layout.addWidget(tabwidget)


        ''' <-------------------- SOUND DESIGN TAB --------------------> '''
        oscillatorsTab = QWidget()
        oscillatorsTabLayout = QVBoxLayout()
        oscillatorsTab.setLayout(oscillatorsTabLayout)

        '''UPPER OSCILLATOR LAYOUT'''
        soundDesignLayout = QGridLayout()
        oscillatorsTabLayout.addLayout(soundDesignLayout)

        # oscillator 1 waveform selector
        oscillator1DropDownLabel = QLabel("Waveform")
        oscillator1DropDownLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillator1DropDownLabel, 0, 0)

        oscillator1DropDown = CustomComboBox()
        oscillator1DropDown.addItems(Synthesizer.waveforms)
        oscillator1DropDown.setCurrentIndex(0)
        oscillator1DropDown.activated.connect(self.oscillator1ShapeChanged)
        soundDesignLayout.addWidget(oscillator1DropDown, 1, 0)

        # oscillator 2 waveform selector
        oscillator2DropDownLabel = QLabel("Waveform")
        oscillator2DropDownLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillator2DropDownLabel, 2, 0)

        oscillator2DropDown = CustomComboBox()
        oscillator2DropDown.addItems(Synthesizer.waveforms)
        oscillator2DropDown.setCurrentIndex(0)
        oscillator2DropDown.activated.connect(self.oscillator2ShapeChanged)
        soundDesignLayout.addWidget(oscillator2DropDown, 3, 0)

        # oscillator 1 pitch dial
        oscillator1PitchLabel = QLabel("Pitch")
        oscillator1PitchLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillator1PitchLabel, 0, 1)

        self.oscillator1PitchDial = QDial()
        self.oscillator1PitchDial.setMinimum(-12)
        self.oscillator1PitchDial.setMaximum(12)
        self.oscillator1PitchDial.setValue(0)
        self.oscillator1PitchDial.valueChanged.connect(self.oscillator1PitchChanged)
        soundDesignLayout.addWidget(self.oscillator1PitchDial, 1, 1)

        # oscillator 2 pitch dial
        oscillator2PitchLabel = QLabel("Pitch")
        oscillator2PitchLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillator2PitchLabel, 2, 1)

        self.oscillator2PitchDial = QDial()
        self.oscillator2PitchDial.setMinimum(-12)
        self.oscillator2PitchDial.setMaximum(12)
        self.oscillator2PitchDial.setValue(0)
        self.oscillator2PitchDial.valueChanged.connect(self.oscillator2PitchChanged)
        soundDesignLayout.addWidget(self.oscillator2PitchDial, 3, 1)

        # oscillator ratio slider
        oscillatorRatioLabel = QLabel("Ratio")
        oscillatorRatioLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillatorRatioLabel, 0, 2)
        self.oscillatorRatioSlider = QSlider(Qt.Orientation.Vertical)
        self.oscillatorRatioSlider.setMinimum(0)
        self.oscillatorRatioSlider.setMaximum(100)
        self.oscillatorRatioSlider.setValue(50)
        self.oscillatorRatioSlider.valueChanged.connect(self.ratioChanged)
        soundDesignLayout.addWidget(self.oscillatorRatioSlider, 1, 2, 3, 1)

        # oscillator volume dial
        oscillatorVolumeLabel = QLabel("Volume")
        oscillatorVolumeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillatorVolumeLabel, 0, 3)

        self.volumeDial = QDial()
        self.volumeDial.setMinimum(0)
        self.volumeDial.setMaximum(100)
        self.volumeDial.setValue(100)
        self.volumeDial.valueChanged.connect(self.volumeChanged)
        soundDesignLayout.addWidget(self.volumeDial, 1, 3)

        # oscillator cutoff dial
        oscillatorCutoffLabel = QLabel("Cutoff")
        oscillatorCutoffLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        soundDesignLayout.addWidget(oscillatorCutoffLabel, 2, 3)

        self.cutoffDial = QDial()
        self.cutoffDial.setMinimum(0)
        self.cutoffDial.setMaximum(100)
        self.cutoffDial.setValue(100)
        self.cutoffDial.valueChanged.connect(self.cutoffChanged)
        soundDesignLayout.addWidget(self.cutoffDial, 3, 3)

        '''LOWER GRAPHICS LAYOUT'''
        graphsLayout = QVBoxLayout()
        oscillatorsTabLayout.addLayout(graphsLayout)
        self.plotWidget = pg.PlotWidget()
        graphsLayout.addWidget(self.plotWidget)
        self.plotWidgetMode = 0
        self.plotWidget.scene().sigMouseClicked.connect(self.togglePlotWidgetMode)
        self.updatePlotWidget()

        '''SPECTROGRAM WIDGET'''
        self.spectrogramWidget = pg.ImageView()
        graphsLayout.addWidget(self.spectrogramWidget)
        self.spectrogramWidget.ui.roiBtn.hide()
        self.spectrogramWidget.ui.menuBtn.hide()
        self.spectrogramWidget.ui.histogram.hide()
        self.spectrogramWidget.setImage(self.spectrogramImage)

        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.15, 0.75])
        colors = [(0,255,255), (255,255,0), (0, 0, 0), (0, 0, 255), (255, 0, 0)]
        cmap = pg.ColorMap(pos=pos, color=colors)
        self.spectrogramWidget.imageItem.setColorMap(cmap)
        self.spectrogramWidget.imageItem.setLevels([-50,40])

        graphsLayout.setStretch(0, 1)
        graphsLayout.setStretch(1, 1)

        tabwidget.addTab(oscillatorsTab, "Oscillators")


    def volumeChanged(self):
        self.synthesizer.setVolume(self.volumeDial.value() / 100)
        self.updatePlotWidget()


    def oscillator1ShapeChanged(self, index):
        self.synthesizer.setOscillator1Waveform(index)
        self.updatePlotWidget()
        self.setFocus()
    

    def oscillator2ShapeChanged(self, index):
        self.synthesizer.setOscillator2Waveform(index)
        self.updatePlotWidget()
        self.setFocus()


    def oscillator1PitchChanged(self, index):
        self.synthesizer.setOscillator1Pitch(index)
        self.updatePlotWidget()
    

    def oscillator2PitchChanged(self, index):
        self.synthesizer.setOscillator2Pitch(index)
        self.updatePlotWidget()


    def ratioChanged(self):
        self.synthesizer.setOscillatorRatio(self.oscillatorRatioSlider.value() / 100)
        self.updatePlotWidget()
    

    def cutoffChanged(self):
        self.synthesizer.setCutoff(self.cutoffDial.value() / 100)
        self.updatePlotWidget()


    def updatePlotWidget(self):
        if self.plotWidgetMode == 0:
            self.updateWavePlot()
        else:
            self.updateFrequencyPlot()


    def updateWavePlot(self):
        data = self.synthesizer.generateWavePlotData() * self.synthesizer.volume
        self.plotWidget.setXRange(0, len(data))
        self.plotWidget.setYRange(-1, 1)
        self.plotWidget.setTitle('Waveform - Time Domain')
        self.plotWidget.plotItem.hideAxis('bottom')
        self.plotWidget.plotItem.clear()
        self.plotWidget.plotItem.plot(data, pen=pg.mkPen(self.plotLineColor, width=self.plotLineWidth))


    def updateFrequencyPlot(self):
        data = self.synthesizer.generateFrequencyPlotData()
        self.plotWidget.setXRange(0, len(data))
        self.plotWidget.setYRange(0, data.max())
        self.plotWidget.plotItem.showAxis('bottom')
        self.plotWidget.setTitle('Waveform - Frequency Domain')
        self.plotWidget.plotItem.clear()
        self.plotWidget.plotItem.plot(data, pen=pg.mkPen(self.plotLineColor, width=self.plotLineWidth))


    def togglePlotWidgetMode(self):
        if self.plotWidgetMode == 0:
            self.plotWidgetMode = 1
        else:
            self.plotWidgetMode = 0

        self.updatePlotWidget()


    def updateSpectrogramWidget(self):
        newData = self.synthesizer.generateSpectrogramData()

        self.spectrogramImage = np.roll(self.spectrogramImage, -self.spectrogramScrollSpeed, 0)
        height = self.spectrogramImage.shape[0]
        self.spectrogramImage[height - self.spectrogramScrollSpeed:height] = newData
        self.spectrogramWidget.setImage(self.spectrogramImage.T, autoLevels=False)
        self.spectrogramWidget.imageItem.setRect(self.spectrogramWidget.view.viewRect())


    ''' <-------------------- KEYBOARD INTERACTION --------------------> '''
    keys = [
    Qt.Key.Key_Z, Qt.Key.Key_S, Qt.Key.Key_X, Qt.Key.Key_D, Qt.Key.Key_C, Qt.Key.Key_V, Qt.Key.Key_G, Qt.Key.Key_B, Qt.Key.Key_H, Qt.Key.Key_N, Qt.Key.Key_J, Qt.Key.Key_M,
    Qt.Key.Key_Q, Qt.Key.Key_2, Qt.Key.Key_W, Qt.Key.Key_3, Qt.Key.Key_E, Qt.Key.Key_R, Qt.Key.Key_5, Qt.Key.Key_T, Qt.Key.Key_6, Qt.Key.Key_Y, Qt.Key.Key_7, Qt.Key.Key_U,
    Qt.Key.Key_I, Qt.Key.Key_9, Qt.Key.Key_O, Qt.Key.Key_0, Qt.Key.Key_P, Qt.Key.Key_BracketLeft, Qt.Key.Key_Equal, Qt.Key.Key_BracketRight
    ]

    keymappings = {}
    for i in range(len(keys)):
        keymappings[keys[i]] = i + Synthesizer.C4

    keymappings.update({
        Qt.Key.Key_Comma: Synthesizer.C5,
        Qt.Key.Key_L: Synthesizer.Db5,
        Qt.Key.Key_Period: Synthesizer.D5,
        Qt.Key.Key_Semicolon: Synthesizer.Eb5,
        Qt.Key.Key_Slash: Synthesizer.E5
    })


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

