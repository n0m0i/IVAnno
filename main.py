# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import os.path

    import cv2
    import tkinter as tk
    from tkinter import filedialog
    from PIL import Image, ImageTk
    import json
    import jsonlines

    global OUTPUT_PATH
    global IMG_PATH
    global IMG_NAME

    global img

    # Tkinter 창 생성
    root = tk.Tk()
    root.title("Image Viewer")

    # 윈도우 크기 설정
    root.geometry("1000x500")

    # 이미지 리스트와 선택한 이미지 인덱스 초기화
    image_list = []
    selected_image_index = 0

    # 이미지 리스트와 선택한 이미지를 표시할 Label 위젯 생성
    image_listbox = tk.Listbox(root)
    image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    selected_image_label = tk.Label(root)
    selected_image_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    # 이미지 로드 함수 정의
    def load_images():
        global image_list
        global file_paths
        file_paths = filedialog.askopenfilenames()
        image_list = [cv2.imread(file_path) for file_path in file_paths]
        for fp in file_paths:
            image_listbox.insert(tk.END, os.path.basename(fp))


    # 이미지 선택 함수 정의
    def select_image(event):
        global selected_image_index
        selected_image_index = image_listbox.curselection()[0]
        show_selected_image()


    # 이미지 표시 함수 정의
    def show_selected_image():
        global selected_image_index
        img = image_list[selected_image_index]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(img))
        selected_image_label.configure(image=photo)
        selected_image_label.image = photo


    def save_image():
        pass


    def load_list_from_file(filename):
        with jsonlines.open(filename) as reader:
            fboxes = []
            for i in reader:
                if i["ID"] == IMG_NAME:
                    for gtbox in i['gtboxes']:
                        fbox = gtbox['fbox']
                        fboxes.append(fbox)
                else:
                    print(filename + "is different to " + IMG_NAME)
            return fboxes


    # 버튼 생성
    button = tk.Button(root, text="Open Images", command=load_images)
    button = tk.Button(root, text="Save", command=save_image)

    button.pack()

    # 이미지 리스트에서 이미지 선택 시 이벤트 바인딩
    image_listbox.bind("<<ListboxSelect>>", select_image)

    # 변수 초기화
    drawing = False
    mag = 1
    ix, iy = -1, -1
    odgt = dict()
    odgt["ID"] = IMG_NAME
    rectangles = []
    height, width = 0, 0

    # load json
    rectangles = load_list_from_file('rectangles.json')
    print(rectangles)
    print('len : ', len(rectangles))

    while True:
        # 이미지 출력
        height, width = select_image.shape[:2]
        img = cv2.resize(select_image, (mag * width, mag * height))

        for rectangle in rectangles:
            cv2.rectangle(img, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 255, 0), 1)
        cv2.imshow("image", img)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        # 'r' 키를 누르면 모든 사각형 지우기
        elif cv2.waitKey(1) & 0xFF == ord("r"):
            rectangles = []
            print("remove all")

    # Tkinter 창 실행
    root.mainloop()

