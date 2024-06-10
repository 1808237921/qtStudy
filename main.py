import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Ui_MainWindow import Ui_MainWindow

 
class MyWindow(QMainWindow, Ui_MainWindow): 
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.action.triggered.connect(QApplication.exit)
        self.action_2.triggered.connect(self.onAction2)
        self.action_3.triggered.connect(self.onAction3)

    def onAction2(self):
        QMessageBox.information(self, "关于", "这是一个用Qt开发的demo", QMessageBox.Ok)

    def onAction3(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "打开", "c:", "All Files (*)")
        image = QPixmap(filepath)
        image = image.scaled(300,300)
        self.label.setPixmap(image)
            
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./main_icon.jpg"))
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())    
