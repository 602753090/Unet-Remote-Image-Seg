import sys
import subprocess
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QFileDialog, QMessageBox, QHBoxLayout)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal


class App(QWidget):
    imagesProcessed = pyqtSignal()
    statusUpdated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('遥感图像语义分割系统')
        self.setGeometry(200, 200, 830, 430)
        self.initUI()

        self.imagesProcessed.connect(self.showImages)
        self.statusUpdated.connect(self.updateStatusLabel)
        self.originalImagePath = ""
        self.output1ImagePath = 'output/output_dice.png'
        self.output2ImagePath = 'output/output_crosse.png'
        self.legendPath = 'imgs/legend.png'

    def initUI(self):
        # 背景图片
        self.background = QLabel(self)
        self.background.resize(self.size())
        self.setBackground()

        # 标题
        self.mainTitle = QLabel('遥感图像语义分割系统', self)
        self.mainTitle.setStyleSheet('font-size: 50px; font-weight: bold; background-color: rgba(255, 255, 255, 150);')

        # 登录界面组件
        self.usernameLabel = QLabel('请输入用户名:', self)
        self.usernameLabel.setStyleSheet(
            'font-size: 24px; font-weight: bold; color: white;')
        self.usernameInput = QLineEdit(self)
        self.passwordLabel = QLabel('请输入密码:', self)
        self.passwordLabel.setStyleSheet(
            'font-size: 24px; font-weight: bold; color: white;')
        self.passwordInput = QLineEdit(self)
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.loginButton = QPushButton('登录', self)
        self.loginButton.setStyleSheet(
            'font-size: 24px; font-weight: bold; background-color: rgba(255, 255, 255, 200);')
        self.loginButton.clicked.connect(self.onLoginClicked)

        # 主界面组件（先隐藏）
        self.uploadButton = QPushButton('上传图像', self)
        self.uploadButton.setStyleSheet(
            'font-size: 24px; font-weight: bold; background-color: rgba(255, 255, 255, 200);')
        self.uploadButton.clicked.connect(self.uploadImage)
        self.statusLabel = QLabel('已就绪', self)
        self.statusLabel.setStyleSheet(
            'font-size: 24px; font-weight: bold; color: white; background-color: rgba(0, 0, 0, 100);')

        # 设置组件的半透明背景
        self.setStyleForWidgets([self.usernameInput,self.passwordInput])

        self.centerWidgets()

    def setStyleForWidgets(self, widgets):
        for widget in widgets:
            widget.setStyleSheet("background-color: rgba(255, 255, 255, 150);")

    def centerWidgets(self):
        self.legendLabel = QLabel()
        # 中心布局
        centerLayout = QVBoxLayout()
        centerLayout.addWidget(self.mainTitle, 0, Qt.AlignHCenter)
        centerLayout.addWidget(self.legendLabel, 0, Qt.AlignHCenter)
        self.legendLabel.setMinimumSize(1000, 30)
        self.legendLabel.setMaximumSize(2000, 2000)
        self.legendLabel.setScaledContents(True)

        centerLayout.addWidget(self.usernameLabel, 0, Qt.AlignHCenter)
        centerLayout.addWidget(self.usernameInput, 0, Qt.AlignHCenter)
        centerLayout.addWidget(self.passwordLabel, 0, Qt.AlignHCenter)
        centerLayout.addWidget(self.passwordInput, 0, Qt.AlignHCenter)
        centerLayout.addWidget(self.loginButton, 0, Qt.AlignHCenter)

        imageLayout = QHBoxLayout()
        originalLayout = QVBoxLayout()
        output1Layout = QVBoxLayout()
        output2Layout = QVBoxLayout()

        # 为每张图像创建QLabel
        self.originalImageLabel = QLabel()
        self.originalTitle = QLabel('输入图像', self)
        self.originalTitle.setStyleSheet(
            'font-size: 24px; font-weight: bold; background-color: rgba(255, 255, 255, 100);')
        self.output1ImageLabel = QLabel()
        self.output1Title = QLabel('输出1：使用DICE损失', self)
        self.output1Title.setStyleSheet(
            'font-size: 24px; font-weight: bold; background-color: rgba(255, 255, 255, 100);')
        self.output2ImageLabel = QLabel()
        self.output2Title = QLabel('输出2：使用交叉熵损失', self)
        self.output2Title.setStyleSheet(
            'font-size: 24px; font-weight: bold; background-color: rgba(255, 255, 255, 100);')

        # 将QLabels添加到布局中
        originalLayout.addWidget(self.originalImageLabel)
        originalLayout.addWidget(self.originalTitle, Qt.AlignHCenter)
        self.originalImageLabel.setMinimumSize(500, 500)
        self.originalImageLabel.setMaximumSize(1000, 1000)

        output1Layout.addWidget(self.output1ImageLabel)
        output1Layout.addWidget(self.output1Title, Qt.AlignHCenter)
        self.output1ImageLabel.setMinimumSize(500, 500)
        self.output1ImageLabel.setMaximumSize(1000, 1000)

        output2Layout.addWidget(self.output2ImageLabel)
        output2Layout.addWidget(self.output2Title, Qt.AlignHCenter)
        self.output2ImageLabel.setMinimumSize(500, 500)
        self.output2ImageLabel.setMaximumSize(1000, 1000)

        imageLayout.addLayout(originalLayout)
        imageLayout.addLayout(output1Layout)
        imageLayout.addLayout(output2Layout)
        centerLayout.addLayout(imageLayout, Qt.AlignHCenter)

        # 主界面组件（先隐藏）
        self.uploadButton.hide()
        self.statusLabel.hide()
        self.originalTitle.hide()
        self.output1Title.hide()
        self.output2Title.hide()
        self.legendLabel.hide()
        centerLayout.addWidget(self.uploadButton, 0, Qt.AlignHCenter)
        centerLayout.addWidget(self.statusLabel, 0, Qt.AlignHCenter)

        # 应用中心布局
        self.setLayout(centerLayout)

    def setBackground(self):
        pixmap = QPixmap('imgs/background.jpg').scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        self.background.setPixmap(pixmap)

    def onLoginClicked(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        if username == 'admin' and password == 'admin':
            self.loginSuccess()
        else:
            QMessageBox.warning(self, '错误', '用户名或密码错误')

    def loginSuccess(self):
        # 隐藏登录组件，显示主界面组件
        self.usernameLabel.hide()
        self.usernameInput.hide()
        self.passwordLabel.hide()
        self.passwordInput.hide()
        self.loginButton.hide()

        self.uploadButton.show()
        self.statusLabel.show()

    def uploadImage(self):
        filename, _ = QFileDialog.getOpenFileName(self, "上传图像", "", "")
        if filename:
            self.originalImagePath = filename
            self.processImage(filename)

    def processImage(self, file_path):
        self.statusLabel.setText('处理中……（图像越大耗时越久，请耐心等待）……')

        def run_processing_commands():
            model1_path = 'models/model-m-dice.pth'         # 使用model_dice.pth为二分类
            model2_path = 'models/model-m-crosse.pth'       # 使用model_crosse.pth为二分类
            output1_path = 'output/output_dice.png'
            output2_path = 'output/output_crosse.png'

            command1 = ['python', 'predict.py', '--model', model1_path, '--input', file_path, '--output', output1_path]
            command2 = ['python', 'predict.py', '--model', model2_path, '--input', file_path, '--output', output2_path]

            result1 = subprocess.run(command1, capture_output=True, text=True)
            result2 = subprocess.run(command2, capture_output=True, text=True)

            if result1.returncode == 0 and result2.returncode == 0:
                self.statusUpdated.emit('处理完成')
                self.imagesProcessed.emit()
            else:
                self.statusUpdated.emit('处理失败')

        processing_thread = threading.Thread(target=run_processing_commands)
        processing_thread.start()

    def updateStatusLabel(self, text):
        self.statusLabel.setText(text)
    def showImages(self):
        # 加载并展示图像
        self.originalImageLabel.setPixmap(
            QPixmap(self.originalImagePath).scaled(self.originalImageLabel.size(), Qt.KeepAspectRatio))
        self.output1ImageLabel.setPixmap(
            QPixmap(self.output1ImagePath).scaled(self.output1ImageLabel.size(), Qt.KeepAspectRatio))
        self.output2ImageLabel.setPixmap(
            QPixmap(self.output2ImagePath).scaled(self.output2ImageLabel.size(), Qt.KeepAspectRatio))
        self.legendLabel.setPixmap(
            QPixmap(self.legendPath).scaled(self.legendLabel.size(), Qt.KeepAspectRatio))

        # 显示QLabels
        self.legendLabel.show()
        self.originalImageLabel.show()
        self.output1ImageLabel.show()
        self.output2ImageLabel.show()
        self.originalTitle.show()
        self.output1Title.show()
        self.output2Title.show()

    def setScaledPixmapToLabel(self, imagePath, label):
        if imagePath:
            pixmap = QPixmap(imagePath)
            scaledPixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaledPixmap)

    def resizeEvent(self, event):
        self.background.resize(self.size())
        self.setBackground()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
