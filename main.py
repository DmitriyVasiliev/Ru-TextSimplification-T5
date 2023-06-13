import logging

logger = logging.getLogger('transformers')
logger.disabled = False
logger.setLevel(logging.CRITICAL)
import datetime
import time
import sys
import pyperclip
from nltk.tokenize import sent_tokenize

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import Main_Window
import lang_model


class Worker(QObject):
    def __init__(self, inputText):
        super().__init__()
        self.inputText = inputText

    finished = pyqtSignal()
    finalText = pyqtSignal(str)
    # PBs
    progress_seq = pyqtSignal(int)
    set_progress_max = pyqtSignal(int)
    # etc
    killme = pyqtSignal()

    def stop(self):
        self.wait()

    def run(self):
        self.progress_seq.emit(0)
        txt = sent_tokenize(self.inputText, language="russian")
        maxT = txt.__len__()
        self.set_progress_max.emit(maxT)
        nowT = datetime.datetime.now().strftime("%H:%M:%S")
        fText = ""
        for i in range(maxT):
            fText += lang_model.SimplifyText(txt[i])
            self.progress_seq.emit(i + 1)
        self.finalText.emit(fText)
        self.finished.emit()


class MainWindow(QMainWindow, Main_Window.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.dFormat = "[%H:%M:%S]"  # Datetime
        self.ASFormat = "-упр"  # AutoSave
        # adding action to a button
        self.buttonSimplify.clicked.connect(self.simplify)
        self.buttonFile.clicked.connect(self.openFile)
        # temps
        self.isFile = False
        self.curPath = ""

        self.appendStatus("Начало работы")

    # Workers functions

    def killThread(self):
        # self.worker.quit()
        # self.thread.quit()
        self.thread.quit()

    def setFinalText(self, txt):
        if self.isFile:
            self.saveFile(txt)
            self.outputText.setText(txt)
        else:
            if self.checkCopy.isChecked():
                self.outputText.setText(txt)
                self.inputText.clear()
                pyperclip.copy(txt)
            else:
                self.outputText.setText(txt)
        self.isFile = False
        self.curPath = ""

    def setProgressValue(self, value):
        self.barText.setValue(value)

    def setMaxProgressValue(self, value):
        self.barText.setMaximum(value)

    # Self function
    def saveFile(self, txt):
        if self.checkSave.isChecked():
            path = self.curPath
            delRange = 1
            for i in range(-1, -len(path), -1):
                x = path[i]
                if x == '.':
                    break
                else:
                    delRange += 1
            self.curPath = path[0:len(path) - delRange] + self.ASFormat + ".txt"
        else:
            path = self.curPath
            delRange = 0
            for i in range(-1, -len(path), -1):
                x = path[i]
                if x == '/':
                    break
                else:
                    delRange += 1
            self.curPath = path[0:len(path) - delRange]
            filePath = QFileDialog.getSaveFileName(self, caption="Укажите место сохранения файла", filter="*.txt",
                                                   directory=self.curPath)
            if filePath[0] == "":
                return 0
            self.curPath = filePath[0]

        with open(self.curPath, "w", encoding="utf8") as f:
            f.write(txt)
        self.appendStatus("Файл сохранён:" + self.curPath)

    def appendStatus(self, txt):
        if txt == "":
            return 0
        T = datetime.datetime.now().strftime(self.dFormat) + ": " + txt
        self.statusText.append(T)

    def simplify(self):
        iText = self.inputText.toPlainText()
        iText = iText.strip()
        if iText == "":
            return 0
        self.appendStatus("Упрощение текста")
        self.start(iText)

    def openFile(self):
        filePath = QFileDialog.getOpenFileName(self, caption="Укажите текстовый файл", filter="*.txt")
        if filePath[0] == "":
            return 0
        with open(filePath[0], encoding="utf8") as f:
            contents = f.read()
        contents = contents.strip()
        if contents == "":
            return 0
        self.isFile = True
        self.curPath = filePath[0]
        self.appendStatus("Упрощение файла")
        self.start(contents)

    def end(self):
        pass

    def start(self, txt):
        # Init thread
        self.thread = QThread()
        self.worker = Worker(txt)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Connect
        self.worker.finalText.connect(self.setFinalText)  # Output text
        self.worker.progress_seq.connect(self.setProgressValue)  # Progress value
        self.worker.set_progress_max.connect(self.setMaxProgressValue)  # Progress max
        self.worker.killme.connect(self.killThread)  # Kill Thread

        # Unstuck buttons
        self.thread.finished.connect(
            lambda: self.buttonSimplify.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.buttonFile.setEnabled(True)
        )
        self.thread.finished.connect(self.end)
        # Start thread
        self.thread.start()
        # Final resets
        self.buttonSimplify.setEnabled(False)
        self.buttonFile.setEnabled(False)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
