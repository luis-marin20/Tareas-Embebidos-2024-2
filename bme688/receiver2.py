import serial
from struct import pack, unpack
import matplotlib.pyplot as plt

# Se configura el puerto y el BAUD_Rate
PORT = 'COM4'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32
TIME = 1 # Tiempo de espera entre una medicion y otra

window_size = 20

# Se abre la conexion serial
ser = serial.Serial(PORT, BAUD_RATE, timeout = 1)

# Funciones
def send_message(message):
    """ Funcion para enviar un mensaje a la ESP32 """
    ser.write(message)

def receive_response():
    """ Funcion para recibir un mensaje de la ESP32 """
    response = ser.readline() #Esta funcion lee hasta que se topa con un salto de linea o el tiempo de espera se agota
    return response

def receive_data():
    """ Funcion que recibe n floats de la ESP32 
    y los imprime en consola """
    respuesta_encriptada = receive_response()
    # Separamos la respuesta en dos partes
    # print(respuesta_encriptada)
    dato_str1 = respuesta_encriptada[:9].decode('utf-8')
    dato_str2 = respuesta_encriptada[9:].decode('utf-8')
    temp = float(dato_str1)
    press = float(dato_str2)
    return temp, press

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
    
    

def leyendo(n):
    #Creamos un arreglo para guardar los datos
    temperatura = []
    presion = []
    # Se lee data por la conexion serial
    #listen_forever()
    while True:
        if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
            try:
                temp, press = receive_data()
                temperatura += [temp]
                presion += [press]
                if len(temperatura)+len(presion)==  2*n+2:
                    data = {
                        "ventana_temperatura": temperatura[:-1],
                        "ventana_presion": presion[:-1],
                        "tRMS": temperatura[-1],
                        "pRMS": presion[-1]
                    }
                    return data
            except:
                continue

def graficar(lista,variable, title, filename):
    plt.clf()
    x = [i*TIME for i in range(len(lista))]
    plt.plot(x, lista, marker='o', linestyle='-', color='b', label='Datos')
    plt.xlabel('Tiempo (s)')
    plt.ylabel(variable)
    plt.title(title)
    plt.legend()
    plt.savefig(filename)

def mostrar_datos(datos):
    presiones = datos["ventana_presion"]
    temperaturas = datos["ventana_temperatura"]
    pRMS = datos["pRMS"]
    tRMS = datos["tRMS"]
    graficar(temperaturas, "Temperatura (°C)", "Temperatura", "temperatura.png")
    print("Datos temperatura: ",temperaturas)
    print(f"El RMS fue de {tRMS}")
    graficar(presiones, "Presión (Pa)", "Presion", "presion.png")
    print("Datos presion: ",presiones)
    print(f"El RMS fue de {pRMS}")


def solicitar_ventana(n):
    print("Indicandole al ESP32 que comience a leer")
    comenzar_lectura()
    print("Recibiendo datos...")
    return leyendo(n)



def marcador():
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

def desplegar_menu_principal():
    marcador()
    print("Presion y Temperatura vía BME688")
    print("Selecciona una opcion:")
    print("\n")
    print("1: Solicitar una ventana de datos")
    print("2: Cambiar el tamaño de la ventana de datos")
    print("3: Cerrar la conexión")

def listen_forever():
    while True:
        print(receive_response())

while True:
    if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
        try:
            message = receive_response()
            if b"READY" in message:
                print("Mensaje READY recibido")
                send_message("START\0".encode())
                break
        except:
            continue
while True:
    desplegar_menu_principal()

    respuesta =  input("Ingresa el número de la opción elegida ")
    print("\n")

    if respuesta == "1":
        """
        Solicitamos una ventana y graficamos los datos
        """
        datos = solicitar_ventana(window_size)
        mostrar_datos(datos)

    elif respuesta == "2":
        respuesta2 =  input("Ingresa el nuevo tamaño de la ventana ")
        respuesta2 = int(respuesta2)
        if respuesta2 >= 5:
            """
            Cambiar el numero de ventana y enviar mensaje para que ellos lo cambien
            """
            cambiar_ventana(respuesta2) #Solicitamos al ESP32 que cambie el tamaño de la ventana
            window_size = respuesta2 #Cambiamos el tamaño de la ventana para nosotros


    elif respuesta == "3":
        """
        Enviar END\0 y cerrar conexion
        """
        terminar_conexion()
        print("FIN DEL PROGRAMA")
        marcador()
        break

    else:
        print("ERROR: No es un input valido.")
        print("Inputs validos: 1,2,3")

