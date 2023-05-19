import json
import os
import sys

from PyQt5.QtCore import Qt, QPointF, QStringListModel, QEvent, QRectF
from PyQt5.QtGui import QPixmap, QTransform, QPainter, QPen, QCursor
from PyQt5.QtWidgets import *
from PyQt5 import uic
from jsonlines import jsonlines

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("IVAnno.ui")[0]
dataList = []
rectangles = []
#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.loadImage('img.png')

        self.actionOpen_Images.triggered.connect(self.openImage)
        #self.actionOpen_Video.triggered.connect(self.openVideo)
        self.actionOpen_Label_File.triggered.connect(self.openLabelFile)
        self.actionSave.triggered.connect(self.handleSaveClicked)

        self.graphicsView.viewport().setCursor(QCursor(Qt.CrossCursor))

        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.clicked.connect(self.handleItemClick)

        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.textEdit.textChanged.connect(self.handleTextChanged)

        self.btn_txtSave.clicked.connect(self.saveJson)
        self.btn_txtSaveAs.clicked.connect(self.saveJsonAs)
        self.btn_format.clicked.connect(self.switchJsonFormat)


        self.json_file_path = None
        self.odgt = dict()


        self.start_pos = None
        self.end_pos = None
        self.rect_item = None

        self.width = 820
        self.height = 615


        self.graphicsView.viewport().installEventFilter(self)
        print(rectangles)

    def eventFilter(self, obj, event):
        if obj == self.graphicsView.viewport():
            if event.type() == QEvent.MouseMove: # 도대체 왜 클릭해서 움직여야만 동자갛는지 도저히 몰ㄹ르갯ㅈ어리ㅏㅇㄴ머링ㄴㅁㄹ
                # 마우스의 좌표 얻기
                pos = event.pos()
                scene_pos = self.graphicsView.mapToScene(pos)
                # 좌표 출력
                # print(f"마우스 좌표: x={scene_pos.x()}, y={scene_pos.y()}")
                self.lbl_cursorX.setText("X : " + str(round(scene_pos.x(), 4)))
                self.lbl_cursorY.setText("Y : " + str(round(scene_pos.y(), 4)))
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.start_pos = self.graphicsView.mapToScene(event.pos())
                    self.end_pos = self.graphicsView.mapToScene(event.pos())
                    self.rect_item = QGraphicsRectItem()
                    self.rect_item.setPen(QPen(Qt.red))
                    self.graphicsView.scene().addItem(self.rect_item)
                    return True
                elif event.button() == Qt.RightButton:
                    scene_point = self.graphicsView.mapToScene(event.pos())
                    items = self.graphicsView.scene().items(scene_point)
                    if items:
                        for item in items:
                            if isinstance(item, QGraphicsRectItem):
                                self.graphicsView.scene().removeItem(item)
                    return True
            elif event.type() == QEvent.MouseMove:
                if event.buttons() & Qt.LeftButton and self.start_pos is not None:
                    self.end_pos = self.graphicsView.mapToScene(event.pos())
                    self.updateRectangle()
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton and self.start_pos is not None:
                    self.end_pos = self.graphicsView.mapToScene(event.pos())
                    self.rect_item.setPen(QPen(Qt.green))

                    # self.start_pos = self.graphicsView.mapToScene(self.start_pos)
                    # self.end_pos = self.graphicsView.mapToScene(self.end_pos)
                    if True:
                        if self.start_pos.x() < 0:
                            self.start_pos.setX(0)
                        elif self.start_pos.x() > self.width:
                            self.start_pos.setX(self.width)
                        if self.start_pos.y() < 0:
                            self.start_pos.setY(0)
                        elif self.start_pos.y() > self.height:
                            self.start_pos.setY(self.height)

                        if self.end_pos.x() < 0:
                            self.end_pos.setX(0)
                        elif self.end_pos.x() > self.width:
                            self.end_pos.setX(self.width)
                        if self.end_pos.y() < 0:
                            self.end_pos.setY(0)
                        elif self.end_pos.y() > self.height:
                            self.end_pos.setY(self.height)

                        if self.start_pos.x() > self.end_pos.x():
                            tmp = self.start_pos.x()
                            self.start_pos.setX(self.end_pos.x())
                            self.end_pos.setX(tmp)
                        if self.start_pos.y() > self.end_pos.y():
                            tmp = self.start_pos.y()
                            self.start_pos.setY(self.end_pos.y())
                            self.end_pos.setY(tmp)

                    self.updateRectangle()
                    rectangles.append([int(self.start_pos.x()), int(self.start_pos.y()), int(self.end_pos.x()), int(self.end_pos.y())])
                    print(rectangles[-1])
                    self.start_pos = None
                    self.end_pos = None
                    self.rect_item = None
                    return True

        return super().eventFilter(obj, event)

    def updateRectangle(self):

        rect = QRectF(self.start_pos, self.end_pos).normalized()
        self.rect_item.setRect(rect)
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
        file_paths, _ = QFileDialog.getOpenFileNames(self, 'Select Files', '', 'Images (*.png *.xpm *.jpg)')
        if file_paths:
            for file_path in file_paths:
                print(file_path)
                self.populateList(file_path)
                rectangles.append(list())
            self.loadImage(file_paths[0])
    def openLabelFile(self):
        self.json_file_path, _ = QFileDialog.getOpenFileName(self, 'Select Files', '', 'Text files(*.json *.odgt *.txt)')
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)

        # JSON 내용을 문자열로 변환
        json_string = json.dumps(data, indent=4)

        # QTextEdit에 JSON 내용 표시 및 편집 가능 모드로 설정
        self.textEdit.setPlainText(json_string)
        self.textEdit.setReadOnly(False)
    def saveJson(self):
        text = self.textEdit.toPlainText()

        if self.json_file_path:
            try:
                with open(self.json_file_path, 'w') as file:
                    json.dump(text, file)
                # QMessageBox.information(self, "Save Successful", "Text saved.")
                self.lbl_saved.setText("Saved")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"An error occurred while saving the file:\n{str(e)}")
        else:
            self.save_text_as()

    def saveJsonAs(self):
        text = self.textEdit.toPlainText()

        # JSON 파일 저장 대화 상자 열기
        new_file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "JSON Files (*.json)")

        if self.json_file_path:
            try:
                with open(new_file_path, 'w') as file:
                    json.dump(text, file)
                self.json_file_path = new_file_path
                self.lbl_saved.setText("Saved")
                # QMessageBox.information(self, "Save Successful", "Text saved.")

            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"An error occurred while saving the file:\n{str(e)}")

    def handleTextChanged(self):
        self.lbl_saved.setText("Typing...")
    def switchJsonFormat(self):
        try:
            text = self.textEdit.toPlainText()
            json_list = text.split('}\n{')  # 빈 줄을 기준으로 여러 개의 JSON 분리

            formatted_json_list = []
            for i, j in enumerate(json_list):
                if len(json_list) > 1:
                    if i == 0:
                        parsed_json = json.loads(j + '}')
                    elif len(json_list)-1 == i:
                        parsed_json = json.loads('{' + j)
                    else:
                        parsed_json = json.loads('{' + j + '}')
                else:
                    parsed_json = json.loads(j)
                if "\n" in j:
                    formatted_json = json.dumps(parsed_json, separators=(",", ":"), indent=None)
                else:
                    formatted_json = json.dumps(parsed_json, separators=(",", ":"), indent=4)
                formatted_json_list.append(formatted_json)

            formatted_text = '\n'.join(formatted_json_list)  # 다시 합치기
            self.textEdit.setPlainText(formatted_text)
        except:
            QMessageBox.information(self, "Bad Format", "It must Fix the Sequence")

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
        self.getOriginSize()

        self.lbl_ImageSize.setText(
            "Origin Size : " + str(self.width) + " x " + str(self.height))
        self.lbl_CurrentSize.setText(
            "Current Size : " + str(self.width) + " x " + str(self.height))
        self.lbl_Scale.setText("Scale : 100%")

        # self.odgt["ID"] = os.path.basename(image_path)
        # self.odgt["ID"] = os.path.splitext(self.odgt["ID"])[0]
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
        self.width = original_size.width()
        self.height = original_size.height()
    def wheelEvent(self, event):
        # Ctrl 키를 누르고 있을 때만 이미지 크기를 조정합니다.
        if event.modifiers() == Qt.ControlModifier:
            # 현재 이미지의 크기를 가져옵니다.
            current_size = self.graphicsView.transform().m11()
            angle = event.angleDelta().y() / 120  # 휠 동작의 각도를 가져옵니다.
            scale_factor = 1.1 ** angle  # 이미지 크기를 조정하는 비율 계산

            #원본 이미지의 가로세로 크기

            # 이미지를 비율로 조정합니다.
            new_size = current_size * scale_factor
            new_transform = QTransform().scale(new_size, new_size)
            self.graphicsView.setTransform(new_transform)
            self.getOriginSize()
            self.lbl_ImageSize.setText("Origin Size : " + str(self.width) + " x " + str(self.height))
            self.lbl_CurrentSize.setText("Current Size : " + str(round(self.width * new_size)) + " x " + str(round(self.height * new_size)))
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