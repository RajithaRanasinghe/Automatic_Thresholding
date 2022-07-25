import sys
import os
import numpy as np
try:
    import PySide2
    #print("PySide2 Detected")
except:
    pass
try:
    import PyQt5
    #print("PySide2 Detected")
except:
    pass

if 'PySide2' in sys.modules:
    from PySide2.QtGui import QPixmap,QPalette,QColor,QPainter, QPen, QBrush, QImage
    from PySide2.QtWidgets import QWidget,QComboBox,QDialog, QCheckBox, QMessageBox, QFileDialog, QPushButton, QLineEdit, QProgressBar, QGridLayout, QHBoxLayout, QVBoxLayout, QApplication, QSplashScreen,QTabWidget,QMainWindow,QLabel,QStyleFactory,QDialogButtonBox
    from PySide2.QtCore import QTimer,Qt,QSize
elif 'PyQt5' in sys.modules:
    from PyQt5.QtGui import QPixmap,QPalette,QPainter, QPen, QColor, QBrush, QImage
    from PyQt5.QtWidgets import QWidget,QComboBox,QDialog, QCheckBox, QMessageBox, QFileDialog, QPushButton, QLineEdit, QProgressBar, QGridLayout, QHBoxLayout, QVBoxLayout, QApplication, QSplashScreen,QTabWidget,QMainWindow,QLabel,QStyleFactory,QDialogButtonBox
    from PyQt5.QtCore import QTimer,Qt,QSize,QColor
else:
    sys.exit()
    #print("Missing PySide2 or PyQt5")


from skimage import io as sk_io, color as sk_col, morphology as sk_mm
from skimage.filters import threshold_yen, threshold_triangle, threshold_otsu, threshold_minimum, threshold_mean, threshold_isodata
from skimage.transform import rescale, resize, downscale_local_mean

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        #Setup basics
        self.title = "Automatic Thresholding"    
        self.setWindowTitle(self.title)
        self.setFixedSize(QSize(1024, 768))

        self.inputFolder_path = ''
        self.outputFolder_path = ''
        self.inputFile_path = ''
        self.output_width = 1024
        self.output_height = 1024
        self.currentInputImage = 0
        self.currentOutputImage = 0

        self.thresholdingMethodList = {'Yen’s method' : threshold_yen, 'triangle algorithm' : threshold_triangle , 'Otsu’s method' : threshold_otsu, 'minimum method' : threshold_minimum, 'mean of grayscale values' : threshold_mean,'ISODATA method' : threshold_isodata}



        

        self.initUI()
        self.setProgress(100)


    def applyForallFiles(self, INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH, size_as_tuple):
        self.makeFolders(OUTPUT_FOLDER_PATH, ['input_resized','output_resized', 'input_histograms', 'output_input_histograms'])
        content = os.listdir(INPUT_FOLDER_PATH)
        self.setProgress(0)
        y  = len(content)
        for i, item in enumerate(content):
            input_item_PATH = INPUT_FOLDER_PATH + '/' + item
            output_in_item_PATH = OUTPUT_FOLDER_PATH + '/' + 'input_resized' + '/' + item
            output_out_item_PATH = OUTPUT_FOLDER_PATH + '/' + 'output_resized' + '/' + item
            output_in_hist_PATH = OUTPUT_FOLDER_PATH + '/' + 'input_histograms' + '/' + item
            output_out_hist_PATH = OUTPUT_FOLDER_PATH + '/' + 'output_input_histograms' + '/' + item

            try:
                self.currentOutputImage = self.ImageThresholding(input_item_PATH, self.thresholdingMethodList[str(self.select_thd_cmbx.currentText())])
                #resize
                if (self.resize_onOff.isChecked() == True):
                    self.currentInputImage = resize(self.currentInputImage, size_as_tuple, anti_aliasing=True)
                    self.currentOutputImage = resize(self.currentOutputImage, size_as_tuple, anti_aliasing=False)

                if os.path.exists(output_in_item_PATH):
                    os.remove(output_in_item_PATH)
                if os.path.exists(output_out_item_PATH):
                    os.remove(output_out_item_PATH)
                if os.path.exists(output_in_hist_PATH):
                    os.remove(output_in_hist_PATH)
                if os.path.exists(output_out_hist_PATH):
                    os.remove(output_out_hist_PATH)

                # Save the image
                sk_io.imsave(fname=output_in_item_PATH, arr=self.currentInputImage)
                sk_io.imsave(fname=output_out_item_PATH, arr=self.currentOutputImage)

                fig, ax = plt.subplots()
                ax.hist(self.currentInputImage.ravel(), label='')
                ax.set_xlabel('Pixel Intensity Value')
                ax.set_ylabel('Numper of Pixels')
                plt.savefig(output_in_hist_PATH)
                plt.close()

                fig, ax = plt.subplots()
                ax.hist(np.uint8(self.currentOutputImage.ravel()), label=str(self.select_thd_cmbx.currentText()))
                ax.set_xlabel('Pixel Intensity Value')
                ax.set_ylabel('Numper of Pixels')
                plt.savefig(output_out_hist_PATH)
                plt.close()
                self.clearView()
                self.updateUI()
                self.setProgress(int(i * 100/y))
            

            except OSError as error:
                self.notice_msgbox('ERROR :'+ str(error))
        self.setProgress(100)

    def notice_msgbox(self, notice = ''):
        message = QMessageBox()
        message.setWindowTitle("Notice")
        message.setText(notice)
        message.show()
        message.exec_()


    def makeFolders(self, folder_name, sub_folder_list = []):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            if len(sub_folder_list) > 0:
                for folder in sub_folder_list:
                    os.makedirs(folder_name + '/'+folder)

        else:
            if len(sub_folder_list) > 0:
                for folder in sub_folder_list:
                    if not os.path.exists(folder_name + '/'+folder):
                        os.makedirs(folder_name + '/'+folder)



    def updateUI(self):
        if len(self.inputFile_path) > 0:
            self.currentOutputImage = self.ImageThresholding(self.inputFile_path,self.thresholdingMethodList[str(self.select_thd_cmbx.currentText())])
        self.showImages(self.currentInputImage, self.currentOutputImage, str(self.select_thd_cmbx.currentText()))


    def showImages(self, Input_image_numpy, Output_image_numpy, Method_title):

        fig = Figure(figsize=(12, 12), dpi=65, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        fig.suptitle(Method_title, fontsize=20)

        a=fig.add_subplot(2,2,1)
        a.imshow(Input_image_numpy)
        a.set_title('Input')


        a=fig.add_subplot(2,2,2)
        x = Input_image_numpy.ravel()
        a.hist(x)
        whitePxl = np.sum(x)
        a.set_title('Input Histogram / Total white pixels = {}'.format(whitePxl))
        a.set_xlabel('Pixel Intensity Value')
        a.set_ylabel('Numper of Pixels')


        a=fig.add_subplot(2,2,3)
        a.imshow(Output_image_numpy, cmap='gray')
        a.set_title('Output')

        
        a=fig.add_subplot(2,2,4)
        x = np.uint8(Output_image_numpy.ravel())
        a.hist(x)
        whitePxl = np.sum(x)
        a.set_title('Histogram Output / Total white pixels = {}'.format(whitePxl))
        a.set_xlabel('Pixel Intensity Value')
        a.set_ylabel(''Numper of Pixels')

        fig.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)
        

        canvas = FigureCanvas(fig)
        self.imgView_layout.addWidget(canvas)


    def ImageThresholding(self, FILE_PATH, Thresholding_method):

        # Load the image from FILE_PATH
        self.currentInputImage = sk_io.imread(FILE_PATH)

        # Convert to grayscale
        try:
            bw_image = sk_col.rgb2gray(self.currentInputImage)
        except:
            bw_image = self.currentInputImage


        # Find the threshold value
        th_val = Thresholding_method(bw_image)

        # Threshold the image
        binary_image = bw_image > th_val

        return binary_image

    def setOutputWidth(self):
        self.output_width = int(self.Text_Outputwidth.text())

    def setOutputHeight(self):
        self.output_height = int(self.Text_Outputheight.text())

    def updateInputPath(self):
        self.inputFolder_path = str(self.Text_InputFlder.text())
        self.inputFile_path = ''

    def updateOutputPath(self):
        self.outputFolder_path = str(self.Text_OutputFlder.text())
        self.inputFile_path = ''


    def setInputFolderPath(self):
        FOLDER_NAME, FOLDER_PATH = self.getFolder()
        self.Text_InputFlder.setText(FOLDER_PATH)
        self.updateInputPath()

    def setOutputFolderPath(self):
        FOLDER_NAME, FOLDER_PATH = self.getFolder()
        self.Text_OutputFlder.setText(FOLDER_PATH)
        self.updateOutputPath()
        self.Text_Outputwidth.setText(str(self.output_width))
        self.Text_Outputheight.setText(str(self.output_height))

    def setInputFilePath(self):
        FILE_NAME, FILE_PATH = self.getFile()
        self.Text_InputFlder.setText(FILE_PATH)
        self.updateInputPath()
        self.inputFile_path = FILE_PATH
        self.updateUI()



    def getFolder(self):
        dlgBox = QFileDialog()
        dlgBox.setFileMode(QFileDialog.Directory)
        FOLDER_PATH = dlgBox.getExistingDirectory(self,'Open Folder')
        FOLDER_NAME = FOLDER_PATH.split('/')[-1]
        return FOLDER_NAME, FOLDER_PATH

    def getFile(self):
        dlgBox = QFileDialog()
        dlgBox.setFileMode(QFileDialog.AnyFile)
        FILE_PATH,_ = dlgBox.getOpenFileName(self, 'Open File')
        FILE_NAME = FILE_PATH.split('/')[-1]
        return FILE_NAME, FILE_PATH


    def setProgress(self,value):
        self.pbar.setValue(value)

    def clearView(self):
        if self.imgView_layout is not None:
            while self.imgView_layout.count():
                item = self.imgView_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearView(item.layout())  #recursive

    def applyButtonpressed(self):
        self.applyForallFiles(self.inputFolder_path, self.outputFolder_path , (self.output_width, self.output_height))

    def aboutpressed(self):
        message = QMessageBox()
        message.setWindowTitle("ABOUT")
        link = "https://github.com/RajithaRanasinghe?tab=repositories"
        message.setText('<font color="blue">Written by</font><font color="red"> RGR </font><font color="green">!</font><br><a href="url">{}</a>'.format(link))

        message.show()
        message.exec_()



    def createUIcomponents(self):
        #progress bar
        self.pbar = QProgressBar()
        self.pbar.setMaximumWidth(100)
        self.pbar.setMaximum(100)
        self.statusBar().addPermanentWidget(self.pbar)

        # Input folder path
        self.InputFlder_label = QLabel("Input Folder")
        self.Text_InputFlder = QLineEdit()
        self.Text_InputFlder.setAlignment(Qt.AlignLeft)
        self.Text_InputFlder.setMinimumWidth(400)
        self.Text_InputFlder.textChanged.connect(self.updateInputPath)
        self.InputFlder_btn = QPushButton("Set Input Folder")
        self.InputFile_btn = QPushButton("Set Input File")
        self.InputFlder_btn.clicked.connect(self.setInputFolderPath)
        self.InputFile_btn.clicked.connect(self.setInputFilePath)

        # Input folder path
        self.OutputFlder_label = QLabel("Output Folder")
        self.Text_OutputFlder = QLineEdit()
        self.Text_OutputFlder.setAlignment(Qt.AlignLeft)
        self.Text_OutputFlder.setMinimumWidth(400)
        self.Text_OutputFlder.textChanged.connect(self.updateOutputPath)
        self.OutputFlder_btn = QPushButton("Set Output Folder")
        self.OutputFile_btn = QPushButton("Set Output File")
        self.OutputFlder_btn.clicked.connect(self.setOutputFolderPath)
        self.Outputwidth_label = QLabel("Output Width")
        self.Text_Outputwidth = QLineEdit()
        self.Text_Outputwidth.textChanged.connect(self.setOutputWidth)
        self.Outputheight_label = QLabel("Output Height")
        self.Text_Outputheight = QLineEdit()
        self.Text_Outputheight.textChanged.connect(self.setOutputHeight)

        # Select Thresholding Method
        self.select_thd_label = QLabel("Select Thresholding Method")
        self.select_thd_cmbx = QComboBox()
        self.select_thd_cmbx.activated.connect(self.updateUI)
        for key in self.thresholdingMethodList.keys():
            self.select_thd_cmbx.addItem(key)

        #buttons
        self.clear_btn = QPushButton("Clear View")
        self.clear_btn.setObjectName("Clear View")
        self.clear_btn.clicked.connect(self.clearView)

        self.apply_btn = QPushButton("Apply to all")
        self.apply_btn.setObjectName("Apply to all")
        self.apply_btn.clicked.connect(self.applyButtonpressed)

        self.about_btn = QPushButton("About")
        self.about_btn.setObjectName("About")
        self.about_btn.clicked.connect(self.aboutpressed)

        #Checkoxes
        self.resize_onOff = QCheckBox("Resize")
        self.resize_onOff.setChecked(True)








    def initUI(self):
        #Layouts        
        self.main_layout = QVBoxLayout()
        self.data_layout = QGridLayout()
        self.imgView_layout = QVBoxLayout()
        self.control_btn_layout = QHBoxLayout()


        #set margins (left,top,right,bottom)
        self.main_layout.setContentsMargins(1,1,1,1)
        self.data_layout.setContentsMargins(1,1,1,1)
        self.control_btn_layout.setContentsMargins(1,1,1,1)
        self.imgView_layout.setContentsMargins(1,1,1,1)

        #layout Widgets
        self.data_widget = QWidget()
        self.control_btn_widget = QWidget()
        self.main_widget = QWidget()
        self.imgView_widget = QWidget()

        #create components for layout
        self.createUIcomponents()

        #Add component widgets to button layout
        self.control_btn_layout.addWidget(self.clear_btn)
        self.control_btn_layout.addWidget(self.apply_btn)
        self.control_btn_layout.addWidget(self.about_btn)


        #Set widget
        self.control_btn_widget.setLayout(self.control_btn_layout)

        # Add data input items to layout
        self.data_layout.addWidget(self.InputFlder_label, 0, 0, Qt.AlignCenter)
        self.data_layout.addWidget(self.Text_InputFlder, 0, 1, Qt.AlignCenter)
        self.data_layout.addWidget(self.InputFlder_btn, 0, 2, Qt.AlignCenter)
        self.data_layout.addWidget(self.InputFile_btn, 0, 3, Qt.AlignCenter)
        self.data_layout.addWidget(self.OutputFlder_label, 1, 0, Qt.AlignCenter)
        self.data_layout.addWidget(self.Text_OutputFlder, 1, 1, Qt.AlignCenter)
        self.data_layout.addWidget(self.OutputFlder_btn, 1, 2, Qt.AlignCenter)
        self.data_layout.addWidget(self.Outputwidth_label, 3, 0, Qt.AlignCenter)
        self.data_layout.addWidget(self.Text_Outputwidth, 3, 1, Qt.AlignCenter)
        self.data_layout.addWidget(self.Outputheight_label, 3, 2, Qt.AlignCenter)
        self.data_layout.addWidget(self.Text_Outputheight, 3, 3, Qt.AlignCenter)
        self.data_layout.addWidget(self.resize_onOff, 3, 4, Qt.AlignCenter)    
        self.data_layout.addWidget(self.select_thd_label, 4, 0, Qt.AlignCenter)
        self.data_layout.addWidget(self.select_thd_cmbx, 4, 1, Qt.AlignCenter)


        #Set widget
        self.data_widget.setLayout(self.data_layout)

        # Add  items to image View
        #self.imgView_layout.addWidget(self.InputImg_label,0,0,Qt.AlignCenter)



        #Set widget
        self.imgView_widget.setLayout(self.imgView_layout)


        #Add widjets to main layout        
        self.main_layout.addWidget(self.data_widget)
        self.main_layout.addWidget(self.imgView_widget)
        self.main_layout.addWidget(self.control_btn_widget)

        #Set widget
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

 

if __name__ == '__main__':
    sys.argv.append('--no-sandbox')
    app = QApplication(sys.argv)
    QApplication.processEvents()
    main = Main()
    main.show()
    sys.exit(app.exec_())
