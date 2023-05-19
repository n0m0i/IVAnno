import os.path
import sys

from PyQt5.QtCore import Qt, QPointF, QStringListModel
from PyQt5.QtGui import QPixmap, QTransform, QPainter
from PyQt5.QtWidgets import *
from PyQt5 import uic

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("IVAnno.ui")[0]
dataList = []
#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.actionOpen_Images.triggered.connect(self.openImage)
        self.actionSave.triggered.connect(self.handleSaveClicked)

        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphicsView.viewport().setCursor(Qt.OpenHandCursor)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)

        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.clicked.connect(self.handleItemClick)

    def populateList(self, text):
        # 목록 데이터 생성
        dataList.append(text)
        # QStringListModel 생성 및 데이터 설정
        model = QStringListModel()
        name_list = [os.path.basename(x) for x in dataList]
        model.setStringList(name_list)

        # QListView에 model 설정
        self.listView.setModel(model)
    def handleItemClick(self, index):
        # 클릭된 아이템의 인덱스와 텍스트를 가져옵니다.
        item_index = index.row()

        # item_text = self.listView.model().data(index)
        # 처리할 로직을 작성합니다.
        self.loadImage(dataList[item_index])
        pass

    def openImage(self):
        # file_dialog = QFileDialog()
        # file_dialog.setFileMode(QFileDialog.ExistingFile)
        # file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.bmp)")
        file_paths, _ = QFileDialog.getOpenFileNames(self, 'Select Files', '', 'Images (*.png *.xpm *.jpg)')

        # if file_dialog.exec_():
        #     file_path = file_dialog.selectedFiles()[0]
        #     self.populateList(file_paths)
        #     self.loadImage(file_path)
        for file_path in file_paths:
            print(file_path)
            self.populateList(file_path)
        self.loadImage(file_paths[0])


    def loadImage(self, image_path):
        # 이미지 파일을 로드합니다.
        pixmap = QPixmap(image_path)

        # QGraphicsScene을 생성하고 이미지를 표시할 QGraphicsPixmapItem을 생성합니다.
        scene = QGraphicsScene()
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)

        # graphicsView에 QGraphicsScene을 설정합니다.
        self.graphicsView.setScene(scene)

        self.graphicsView.resetTransform()
        oW = self.getOriginSize().width()
        oH = self.getOriginSize().height()

        self.lbl_ImageSize.setText(
            "Origin Size : " + str(oW) + " x " + str(oH))
        self.lbl_CurrentSize.setText(
            "Current Size : " + str(oW) + " x " + str(oH))
        self.lbl_Scale.setText("Scale : 100%")

    def getOriginSize(self):
        # Graphics View에 표시된 이미지의 원래 크기 얻기
        scene = self.graphicsView.scene()
        items = scene.items()
        original_size = -1
        for item in items:
            if isinstance(item, QGraphicsPixmapItem):
                pixmap = item.pixmap()
                original_size = pixmap.size()
                break
        return original_size
    def wheelEvent(self, event):
        # Ctrl 키를 누르고 있을 때만 이미지 크기를 조정합니다.
        if event.modifiers() == Qt.ControlModifier:
            # 현재 이미지의 크기를 가져옵니다.
            current_size = self.graphicsView.transform().m11()
            angle = event.angleDelta().y() / 120  # 휠 동작의 각도를 가져옵니다.
            scale_factor = 1.1 ** angle  # 이미지 크기를 조정하는 비율 계산

            #원본 이미지의 가로세로 크기
            oW = self.getOriginSize().width()
            oH =  self.getOriginSize().height()
            # 이미지를 비율로 조정합니다.
            new_size = current_size * scale_factor
            new_transform = QTransform().scale(new_size, new_size)
            self.graphicsView.setTransform(new_transform)
            self.lbl_ImageSize.setText("Origin Size : " + str(oW) + " x " + str(oH))
            self.lbl_CurrentSize.setText("Current Size : " + str(round(oW * new_size)) + " x " + str(round(oH * new_size)))
            self.lbl_Scale.setText("Scale : " + str(round(new_size*100)) + "%")

            # 이미지의 중심을 기준으로 조정하기 위해 view의 중심을 계산합니다.
            scene_pos = self.graphicsView.mapToScene(self.graphicsView.viewport().rect().center())
            view_pos = self.graphicsView.mapFromScene(scene_pos)
            self.graphicsView.centerOn(view_pos)

        else:
            # Ctrl 키를 누르지 않은 경우에는 원래의 wheelEvent 동작을 수행합니다.
            super().wheelEvent(event)

    def handleSaveClicked(self):
        # 메뉴 항목을 클릭했을 때 실행되는 코드를 작성합니다.
        print("Save clicked!")

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()