import serial
from struct import pack, unpack
import matplotlib.pyplot as plt

# Se configura el puerto y el BAUD_Rate
PORT = 'COM4'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32

window_size = 10

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
    print("respuesta encriptada: ")
    print(respuesta_encriptada)
    #dato = unpack('>f', respuesta_encriptada) #Aqui desencripto la informacion
    dato_str = respuesta_encriptada.decode('utf-8') #Aqui desencripto la informacion
    dato = float(dato_str)
    print("Dato:")
    print(dato)
    return dato

def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

def cambiar_ventana(new_size):
    largo_mensaje = 7 + len(str(new_size))
    change_message = pack(f'{largo_mensaje}s', f'{new_size}\0'.encode()) #pack('9s', '6\0')
    ser.write(change_message)

def terminar_conexion():
    # Se envia el mensaje de termino de comunicacion
    send_end_message()
    ser.close()

# Funciones auxiliares
def comenzar_lectura():

    print("Sending begin message")
    # Se envia el mensaje de inicio de comunicacion
    message = pack('6s','BEGIN\0'.encode()) #Minuto 30 del aux 2
    send_message(message)

    print("Llegue a comenzar lectura")
    while True:
        if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
            try:
                message = receive_response()
                if b"OK" in message:
                    print("Mensaje de inicio recibido")
                    break
            except:
                continue
    
    

def leyendo(n):
    #Creamos un arreglo para guardar los datos
    print("LLEGUE A LEYENDO")
    datos_recibidos = []
    # Se lee data por la conexion serial
    #listen_forever()
    print("python está esperando que le manden datitos")
    while True:
        if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
            try:
                dato_nuevo = receive_data()
                datos_recibidos += [dato_nuevo]
                print("El tamaño de la lista es: "+str(len(datos_recibidos)))
                print("")
                if len(datos_recibidos)==  2*n+2:
                    print("LLEGUE AL IF")
                    data = {
                        "ventana_presion": list(datos_recibidos[:n]), #Aqui voy a colocar la ventana de presion
                        "pRMS": datos_recibidos[n], #Aqui voy a colocar el RMS de la ventana de presion
                        "ventana_temperatura": list(datos_recibidos[n:2*n+1]),  #Aqui voy a colocar la ventana de temperatura
                        "tRMS": datos_recibidos[2*n+1]  #Aqui voy a colocar el RMS de la ventana de temperatura
                    }
                    return data
            except:
                continue

def graficar(lista,variable):
    x = list(range(len(lista)))
    plt.plot(x, lista, marker='o', linestyle='-', color='b', label='Datos')
    plt.xlabel('Mediciones')
    plt.ylabel(variable)
    plt.title('Gráfico de Dispersión con Línea')
    plt.legend()
    plt.show()

def mostrar_datos(datos):
    presiones = datos["ventana_presion"]
    temperaturas = datos["ventana_temperatura"]
    pRMS = datos["pRMS"]
    tRMS = datos["tRMS"]
    graficar(presiones, "Presión")
    print(presiones)
    print(f"El RMS fue de {pRMS}")
    print(temperaturas)
    graficar(temperaturas, "Temperatura")
    print(f"El RMS fue de {tRMS}")


def solicitar_ventana(n):
    comenzar_lectura()
    datos = leyendo(n)
    return datos



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

