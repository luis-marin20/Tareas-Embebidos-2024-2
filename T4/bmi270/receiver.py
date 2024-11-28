import serial
from struct import pack, unpack
import matplotlib.pyplot as plt
import bisect
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGridLayout, QTableView


# Se configura el puerto y el BAUD_Rate
PORT = 'COM3'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32
TIME = 1 # Tiempo de espera entre una medicion y otra


# Se abre la conexion serial
ser = serial.Serial(PORT, BAUD_RATE, timeout = 1)

# Funciones
def insertar_ordenado(lista, dato):
    """ Funcion para insertar un dato en una lista ordenada """
    bisect.insort(lista, -dato)
def send_message(message):
    """ Funcion para enviar un mensaje a la ESP32 """
    ser.write(message)

def receive_response():
    """ Funcion para recibir un mensaje de la ESP32 """
    response = ser.readline()
    return response

def receive_data():
    """ Funcion que recibe tres floats (fff) de la ESP32 
    y los imprime en consola """
    respuesta_encriptada = receive_response()
    # Para poder ver los datos que envía la ESP:
            #print(f"Data = {respuesta_encriptada}")
            #data = unpack("fff", respuesta_encriptada)
            #print(f'Received: {data}')

    if b'FINISH' in respuesta_encriptada:
        return None, None, None, None

    datos = respuesta_encriptada.decode('utf-8').split(" ")

    if len(datos) == 6: #Estamos viendo mediciones

        return float(datos[0]), float(datos[1]), float(datos[2]), float(datos[3])
    
    elif len(datos) == 12:

        return (float(datos[0]), float(datos[1])),\
                (float(datos[2]), float(datos[3])),\
                (float(datos[4]), float(datos[5])),\
                (float(datos[6]), float(datos[7]))

def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

def cambiar_ventana(new_size):
    largo_mensaje = len(str(new_size))
    change_message = pack(f'{largo_mensaje}s', f'{new_size}\0'.encode()) #pack('9s', '6\0')
    ser.write(change_message)

def terminar_conexion():
    # Se envia el mensaje de termino de comunicacion
    send_end_message()
    # Esperamos que la ESP32 responda
    while True:
        if ser.in_waiting > 0:
            try:
                message = receive_response()
                # print(message)
                if b"CLOSED" in message:
                    break
            except:
                continue
    ser.close()

# Funciones auxiliares

def comenzar_lectura():

    # Se envia el mensaje de inicio de comunicacion
    message = pack('6s','BEGIN\0'.encode()) #Minuto 30 del aux 2
    send_message(message)

    while True:
        if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
            try:
                message = receive_response()
                if b"OK" in message:
                    break
            except:
                continue

def leyendo():
    #Creamos un arreglo para guardar los datos
    acc_x = []
    acc_y = []
    acc_z = []
    gyr_x = []
    gyr_y = []
    gyr_z = []
    peaks_acc_x = []
    peaks_acc_y = []
    peaks_acc_z = []
    peaks_gyr_x = []
    peaks_gyr_y = []
    peaks_gyr_z = []
    # Se lee data por la conexion serial
    #listen_forever()
    while True:
        if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
            try:
                ax, ay, az, gx, gy, gz = receive_data()
                if ax is None:
                    window_size =int((len(acc_x) - 6) / 2)
                    data = {
                        "ventana_ax": acc_x[:window_size],
                        "ventana_ay": acc_y[:window_size],
                        "ventana_az": acc_z[:window_size],
                        "ventana_gx": gyr_x[:window_size],
                        "ventana_gy": gyr_y[:window_size],
                        "ventana_gz": gyr_z[:window_size],

                        "axRMS": acc_x[window_size],
                        "ayRMS": acc_y[window_size],
                        "azRMS": acc_z[window_size],
                        "gxRMS": gyr_x[window_size],
                        "gyRMS": gyr_y[window_size],
                        "gzRMS": gyr_z[window_size],

                        "peaks_ax": acc_x[2*window_size +1 :],
                        "peaks_ay": acc_y[2*window_size +1 :],
                        "peaks_az": acc_z[2*window_size +1 :],
                        "peaks_gx": gyr_x[2*window_size +1 :],
                        "peaks_gy": gyr_y[2*window_size +1 :],
                        "peaks_gz": gyr_z[2*window_size +1 :],

                        "FFT_ax": acc_x[window_size + 1: 2 * window_size + 1],
                        "FFT_ay": acc_y[window_size + 1: 2 * window_size + 1],
                        "FFT_az": acc_z[window_size + 1: 2 * window_size + 1],
                        "FFT_gx": gyr_x[window_size + 1: 2 * window_size + 1],
                        "FFT_gy": gyr_y[window_size + 1: 2 * window_size + 1],
                        "FFT_gz": gyr_z[window_size + 1: 2 * window_size + 1],
                    }
                    return data
                acc_x.append(ax)
                acc_y.append(ay)
                acc_z.append(az)
                gyr_x.append(gx)
                gyr_y.append(gy)
                gyr_z.append(gz)
            except:
                continue

def graficarXYZ(listax, listay, listaz, variable, title, filename):
    plt.clf()
    x = [i*TIME for i in range(len(listax))]
    plt.plot(x, listax, marker='o', linestyle='-', color='b', label='X')
    plt.plot(x, listay, marker='o', linestyle='-', color='r', label='Y')
    plt.plot(x, listaz, marker='o', linestyle='-', color='g', label='Z')
    plt.xlabel('Tiempo (s)')
    plt.ylabel(variable)
    plt.title(title)
    plt.legend()
    plt.savefig(filename)

def mostrar_datos(datos):
    acc_x = datos["ventana_ax"]
    acc_y = datos["ventana_ay"]
    acc_z = datos["ventana_az"]
    gyr_x = datos["ventana_gx"]
    gyr_y = datos["ventana_gy"]
    gyr_z = datos["ventana_gz"]

    axRMS = datos["axRMS"]
    ayRMS = datos["ayRMS"]
    azRMS = datos["azRMS"]
    gxRMS = datos["gxRMS"]
    gyRMS = datos["gyRMS"]
    gzRMS = datos["gzRMS"]

    peaks_ax = datos["peaks_ax"]
    peaks_ay = datos["peaks_ay"]
    peaks_az = datos["peaks_az"]
    peaks_gx = datos["peaks_gx"]
    peaks_gy = datos["peaks_gy"]
    peaks_gz = datos["peaks_gz"]

    FFT_ax = datos["FFT_ax"]
    FFT_ay = datos["FFT_ay"]
    FFT_az = datos["FFT_az"]
    FFT_gx = datos["FFT_gx"]
    FFT_gy = datos["FFT_gy"]
    FFT_gz = datos["FFT_gz"]

    graficarXYZ(acc_x, acc_y, acc_z, "Aceleración", "Aceleración en los ejes x, y, z", "acc.png")

    graficarXYZ(gyr_x, gyr_y, gyr_z, "Giroscopio", "Giroscopio en los ejes x, y, z", "gyr.png")

    print("Tamaño de la ventana: ", len(acc_x), "\n")
    print(f"La transformada de fourier para la aceleración en el eje x fue: \n{FFT_ax}\n")
    print(f"La transformada de fourier para la aceleración en el eje y fue: \n{FFT_ay}\n")
    print(f"La transformada de fourier para la aceleración en el eje z fue: \n{FFT_az}\n")
    print(f"La transformada de fourier para el giroscopio en el eje x fue: \n{FFT_gx}\n")
    print(f"La transformada de fourier para el giroscopio en el eje y fue: \n{FFT_gy}\n")
    print(f"La transformada de fourier para el giroscopio en el eje z fue: \n{FFT_gz}\n")

    table_data = [
            [     "", "RMS", "Peak 1", "Peak 2", "Peak 3", "Peak 4", "Peak 5"],
            ["acc_x", axRMS[0], peaks_ax[0], peaks_ax[1], peaks_ax[2], peaks_ax[3], peaks_ax[4]],
            ["acc_y", axRMS[0], peaks_ay[0], peaks_ay[1], peaks_ay[2], peaks_ay[3], peaks_ay[4]],
            ["acc_z", azRMS[0], peaks_az[0], peaks_az[1], peaks_az[2], peaks_az[3], peaks_az[4]],
            ["gyr_x", gxRMS[0], peaks_gx[0], peaks_gx[1], peaks_gx[2], peaks_gx[3], peaks_gx[4]],
            ["gyr_y", gyRMS[0], peaks_gy[0], peaks_gy[1], peaks_gy[2], peaks_gy[3], peaks_gy[4]],
            ["gyr_z", gzRMS[0], peaks_gz[0], peaks_gz[1], peaks_gz[2], peaks_gz[3], peaks_gz[4]],
            ]
    return table_data

def solicitar_ventana():
    print("Indicandole al ESP32 que comience a leer")
    comenzar_lectura()
    print("Recibiendo datos...")
    return leyendo()



# Interfaz
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Tarea 4 Sistemas Embedidos y Sensores"
        self.setWindowTitle(self.title)
        self.data = None
        self.input = None
        self.ventana = 0

        self.button_vent = QPushButton("Cambiar Ventana")
        self.button_vent.clicked.connect(self.request_cambio_ventana)

        self.button_request = QPushButton("Solicitar ventana de datos")
        self.button_request.clicked.connect(self.request_ventana)

        self.button_cierre = QPushButton("Cerrar la conexión")
        self.button_cierre.clicked.connect(self.request_cierre)
        self.button_cierre.setStyleSheet("background-color : #d4817b")

        self.base_layout = QHBoxLayout()
        self.base_layout.addWidget(self.button_request)
        self.base_layout.addWidget(self.button_vent)
        self.base_layout.addWidget(self.button_cierre)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.base_layout)
        self.container = QWidget()
        self.container.setLayout(self.main_layout)

        self.setCentralWidget(self.container)

    def inicio_app(self):
        self.main_layout.removeWidget(self.data)
        self.data.deleteLater()
        info_ventana = QLabel(f"La ventana de datos es de {self.ventana}")
        self.main_layout.addWidget(info_ventana)
        self.data = info_ventana
        
    def request_cambio_ventana(self):
        new_data = InputWindow(self)
        if self.main_layout.count() >= 2:
            self.main_layout.replaceWidget(self.data, new_data)
            self.data.deleteLater()
        else:
            self.main_layout.addWidget(new_data)
        self.data = new_data
        

    def cambio_ventana(self):
        if self.input.text().isnumeric():
            cambiar_ventana(self.input.text())
            self.ventana = int(self.input.text())
            self.inicio_app()
        else:
            print("no es un número")

    def request_ventana(self):
        new_data = DataWindow()
        if self.main_layout.count() >= 2:
            self.main_layout.replaceWidget(self.data, new_data)
            self.data.deleteLater()
            self.inicio_app
        else:
            self.main_layout.addWidget(new_data)
        self.data = new_data


    def request_cierre(self):
        terminar_conexion()
        sys.exit()
    
class DataWindow(QWidget):
    def __init__(self):
        super().__init__()
        data = solicitar_ventana()
        table_data = mostrar_datos(data)

        self.label_acc = QLabel()
        pixmap_acc = QPixmap('acc.png')
        self.label_acc.setPixmap(pixmap_acc)

        self.label_gyr = QLabel()
        pixmap_gyr = QPixmap('gyr.png')
        self.label_gyr.setPixmap(pixmap_gyr)

        tabla = TableModel(table_data)
        self.table = QTableView()
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setMinimumSize(730,250)

        self.table.setModel(tabla)

        fotos = QHBoxLayout()
        fotos.addWidget(self.table)
        fotos.addWidget(self.label_acc)
        fotos.addWidget(self.label_gyr)

        self.setLayout(fotos)

class InputWindow(QWidget):
    def __init__(self, window: MainWindow):
        super().__init__()
        new_layout = QHBoxLayout()
        label = QLabel("Ingrese la nueva ventana de datos:")
        window.input = QLineEdit()
        button_cambio_vent = QPushButton("Cambiar Ventana")
        button_cambio_vent.clicked.connect(window.cambio_ventana)
        button_cambio_vent.setStyleSheet("background-color : #84e091")

        new_layout.addWidget(label)
        new_layout.addWidget(window.input)
        new_layout.addWidget(button_cambio_vent)
        
        self.setLayout(new_layout)

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
    
app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
