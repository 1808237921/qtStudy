import sys
import SimpleITK as sitk
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Ui_MainWindow import Ui_MainWindow
from PIL import Image, ImageFilter
import torch
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
from nnunetv2.imageio.simpleitk_reader_writer import SimpleITKIO

predictor = nnUNetPredictor(
    tile_step_size=0.5,
    use_gaussian=True,
    use_mirroring=True,
    perform_everything_on_device=False,
    device=torch.device('cuda'),
    verbose=False,
    verbose_preprocessing=False,
    allow_tqdm=True
)

predictor.initialize_from_trained_model_folder(
    "3d_lowres_model",
    use_folds=(0,),
    checkpoint_name='checkpoint_final.pth',
)
 
class Window(QMainWindow, Ui_MainWindow): 
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.resize(1024, 700)
        self.action.triggered.connect(QApplication.exit)
        self.action_2.triggered.connect(self.onAction2Triggered)
        self.action_3.triggered.connect(self.onAction3Triggered)
        self.action_4.triggered.connect(self.onAction4Triggered)
        self.action_5.triggered.connect(self.onAction5Triggered)
        self.action_6.triggered.connect(self.onAction6Triggered)
        self.horizontalSlider.sliderMoved.connect(self.onSliderMoved)
        self.hasImageOn = False
        self.hasInfered = False
        self.imagePath = None

    def onAction2Triggered(self):
        QMessageBox.information(self, "关于", "这是一个用Qt开发的demo", QMessageBox.Ok)

    def onAction3Triggered(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "打开", ".", "nii.gz文件(*.nii.gz);; nii文件 (*.nii)")
        if filepath == "": return
        self.hasImageOn = True
        self.imagePath = filepath
        self.data = sitk.ReadImage(filepath)
        self.data = np.uint8((1 - sitk.GetArrayFromImage(self.data)) * 255)
        self.horizontalSlider.setMaximum(self.data.shape[0] - 1)
        self.horizontalSlider.setValue(0)
        image = Image.fromarray(self.data[0]).filter(ImageFilter.MedianFilter)
        self.label.setPixmap(image.toqpixmap())
        self.label_2.setText("等待推理")
        self.hasInfered = False

    def onAction4Triggered(self):
        if not self.hasImageOn:
            QMessageBox.information(self, "提示", "请选择一个nii文件再进行推理！", QMessageBox.Ok)
            return
        image, props = SimpleITKIO().read_images([self.imagePath])
        self.data_infered = np.uint8(predictor.predict_single_npy_array(image, props, None, None, False) * 255)
        image = Image.fromarray(self.data_infered[self.horizontalSlider.value()])
        self.label_2.setPixmap(image.toqpixmap())
        self.hasInfered = True

    def onAction5Triggered(self):
        if not self.hasImageOn: 
            QMessageBox.information(self, "提示", "请打开一个nii文件再进行保存原图操作！", QMessageBox.Ok)
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "保存", ".", "jpg文件(*.jpg);; png文件 (*.png)")
        if filepath == "": return
        image = Image.fromarray(self.data[self.horizontalSlider.value()])
        image.save(filepath)
        
    def onAction6Triggered(self):
        if not self.hasInfered:
            QMessageBox.information(self, "提示", "请进行推理后再进行保存推理后的图片操作！", QMessageBox.Ok)
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "保存", ".", "jpg文件(*.jpg);; png文件 (*.png)")
        if filepath == "": return
        image = Image.fromarray(self.data_infered[self.horizontalSlider.value()])
        image.save(filepath)

    def onSliderMoved(self, val):
        if not self.hasImageOn: return
        image = Image.fromarray(np.uint8(self.data[val])).filter(ImageFilter.MedianFilter)
        self.label.setPixmap(image.toqpixmap())
        if self.hasInfered:
            image = Image.fromarray(np.uint8(self.data_infered[val]))
            self.label_2.setPixmap(image.toqpixmap())
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./main_icon.jpg"))
    window = Window()
    window.show()
    sys.exit(app.exec_())    