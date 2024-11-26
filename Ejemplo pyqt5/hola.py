import sys
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGridLayout

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "My app"
        self.setWindowTitle(self.title)

        self.label_acc = QLabel(self)
        pixmap_acc = QPixmap('cat.jpg')
        self.label_acc.setPixmap(pixmap_acc)

        self.label_gyr = QLabel(self)
        pixmap_gyr = QPixmap('cat.jpg')
        self.label_gyr.setPixmap(pixmap_gyr)
        #self.resize(pixmap_acc.width(), pixmap_acc.height())

        self.label = QLabel("Ingrese la nueva ventana de datos:")
        self.input = QLineEdit()
        #self.input.textChanged.connect(self.imprimir)
        self.button_vent = QPushButton("Cambiar Ventana")
        self.button_vent.clicked.connect(self.request_cambio_ventana)

        self.button_request = QPushButton("Solicitar ventana de datos")
        self.button_request.clicked.connect(self.request_ventana)

        self.button_cierre = QPushButton("Cerrar la conexión")
        self.button_cierre.clicked.connect(self.request_cierre)
        self.button_cierre.setStyleSheet("background-color : #d4817b")

        fotos = QVBoxLayout()
        fotos.addWidget(self.label_acc)
        fotos.addWidget(self.label_gyr)

        ventana = QVBoxLayout()
        ventana.addWidget(self.button_request)
        ventana.addWidget(self.label)
        ventana.addWidget(self.input)
        ventana.addWidget(self.button_vent)
        ventana.addWidget(self.button_cierre)

        layout = QGridLayout()
        layout.addLayout(fotos, 0, 0)
        layout.addLayout(ventana, 1, 1)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)
    
    def request_cambio_ventana(self):
        if self.input.text().isnumeric():
            print(f"Quiero cambiar la ventana a {self.input.text()}")
            self.label_acc.setPixmap(QPixmap("dog.jpg"))
            self.label_gyr.setPixmap(QPixmap("dog.jpg"))
        else:
            print("no es un número")

    def request_ventana(self):
        print("quiero la ventana")

    def request_cierre(self):
        print("me quiero cerrar")
        sys.exit()

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())