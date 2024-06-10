import sys
import SimpleITK as sitk
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Ui_MainWindow import Ui_MainWindow
from PIL import Image
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
        self.action_2.triggered.connect(self.onAction2)
        self.action_3.triggered.connect(self.onAction3)
        self.action_4.triggered.connect(self.onAction4)
        self.horizontalSlider.sliderMoved.connect(self.onSliderMoved)
        self.hasImageOn = False
        self.hasInfered = False
        self.imagePath = None

    def onAction2(self):
        QMessageBox.information(self, "关于", "这是一个用Qt开发的demo", QMessageBox.Ok)

    def onAction3(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "打开", "c:", "nii.gz文件(*.nii.gz);; nii文件 (*.nii)")
        if filepath == "": return
        self.hasImageOn = True
        self.imagePath = filepath
        self.data = sitk.ReadImage(filepath)
        self.data = sitk.GetArrayFromImage(self.data)
        self.horizontalSlider.setMaximum(self.data.shape[0] - 1)
        self.horizontalSlider.setValue(0)
        image = Image.fromarray(np.uint8(self.data[0])).toqpixmap()
        self.label.setPixmap(image)
        self.label_2.setText("等待推理")
        self.hasInfered = False

    def onAction4(self):
        if not self.hasImageOn:
            QMessageBox.information(self, "提示", "请选择一个nii文件再进行推理!", QMessageBox.Ok)
            return
        image, props = SimpleITKIO().read_images([self.imagePath])
        self.data_infered = predictor.predict_single_npy_array(image, props, None, None, False)
        self.data_infered[self.data_infered == 1] = 255
        image = Image.fromarray(np.uint8(self.data_infered[self.horizontalSlider.value()])).toqpixmap()
        self.label_2.setPixmap(image)
        self.hasInfered = True

    def onSliderMoved(self, val):
        if not self.hasImageOn: return
        image = Image.fromarray(np.uint8(self.data[val])).toqpixmap()
        self.label.setPixmap(image)
        if self.hasInfered:
            image = Image.fromarray(np.uint8(self.data_infered[val])).toqpixmap()
            self.label_2.setPixmap(image)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./main_icon.jpg"))
    window = Window()
    window.show()
    sys.exit(app.exec_())    
