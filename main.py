import sys
import SimpleITK as sitk
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Ui_MainWindow import Ui_MainWindow
from PIL import Image

 
class MyWindow(QMainWindow, Ui_MainWindow): 
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.resize(1024, 700)
        self.action.triggered.connect(QApplication.exit)
        self.action_2.triggered.connect(self.onAction2)
        self.action_3.triggered.connect(self.onAction3)
        self.horizontalSlider.sliderMoved.connect(self.onSliderMoved)

    def onAction2(self):
        QMessageBox.information(self, "关于", "这是一个用Qt开发的demo", QMessageBox.Ok)

    def onAction3(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "打开", "c:", "nii.gz文件(*.nii.gz);; nii文件 (*.nii)")
        if filepath == "": return
        self.hasImageOn = True
        self.data = sitk.ReadImage(filepath)
        self.data = sitk.GetArrayFromImage(self.data)
        self.horizontalSlider.setMaximum(self.data.shape[0] - 1)
        self.horizontalSlider.setValue(0)
        image = Image.fromarray(np.uint8(self.data[0])).toqpixmap()
        self.label.setPixmap(image)
        

    def onSliderMoved(self, val):
        if not self.hasImageOn: return
        image = Image.fromarray(np.uint8(self.data[val])).toqpixmap()
        self.label.setPixmap(image)
        
        
            
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./main_icon.jpg"))
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())    
