import serial
from struct import pack, unpack
import matplotlib.pyplot as plt
import bisect

# Se configura el puerto y el BAUD_Rate
PORT = 'COM4'  # Esto depende del sistema operativo
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
    response = ser.readline() #Esta funcion lee hasta que se topa con un salto de linea o el tiempo de espera se agota
    return response

def receive_data():
    """ Funcion que recibe n floats de la ESP32 
    y los imprime en consola """
    respuesta_encriptada = receive_response()
    print(respuesta_encriptada)
    if b'FINISH' in respuesta_encriptada:
        print("llegue al finish")
        return None, None, None, None
    
    datos = respuesta_encriptada.decode('utf-8').split(" ")

    if len(datos) == 4: #Estamos viendo mediciones

        return float(datos[0]), float(datos[1]), float(datos[2]), float(datos[3])
    
    elif len(datos) == 8:

        return (float(datos[0]), float(datos[1])),\
                (float(datos[2]), float(datos[3])),\
                (float(datos[4]), float(datos[5])),\
                (float(datos[6]), float(datos[7]))
    
        
    # Separamos la respuesta en dos partes


    # if len(respuesta_encriptada) == 72:
    #     dato_str1 = respuesta_encriptada[:9].decode('utf-8')
    #     dato_fft1 = respuesta_encriptada[9:18].decode('utf-8')
    #     dato_str2 = respuesta_encriptada[18:27].decode('utf-8')
    #     dato_fft2 = respuesta_encriptada[27:36].decode('utf-8')
    #     dato_str3 = respuesta_encriptada[36:45].decode('utf-8')
    #     dato_fft3 = respuesta_encriptada[45:54].decode('utf-8')
    #     dato_str4 = respuesta_encriptada[54:63].decode('utf-8')
    #     dato_fft4 = respuesta_encriptada[63::].decode('utf-8')

    #     temp = [float(dato_str1), float(dato_fft1)]
    #     press = [float(dato_str2), float(dato_fft2)]
    #     hum = [float(dato_str3), float(dato_fft3)]
    #     co = [float(dato_str4), float(dato_fft4)]
    #     return temp, press, hum, co
    # else:
    #     dato_str1 = respuesta_encriptada[:9].decode('utf-8')
    #     dato_str2 = respuesta_encriptada[9:18].decode('utf-8')
    #     dato_str3 = respuesta_encriptada[18:27].decode('utf-8')
    #     dato_str4 = respuesta_encriptada[27::].decode('utf-8')

    #     temp = [float(dato_str1), None]
    #     press = [float(dato_str2), None]
    #     hum = [float(dato_str3), None]
    #     co = [float(dato_str4), None]
    #     return temp, press, hum, co

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
    temperatura = []
    presion = []
    humedad = []
    concentracion_co = []
    peaks_tmp = []
    peaks_pres = []
    peaks_hum = []
    peaks_co = []
    # Se lee data por la conexion serial
    #listen_forever()
    while True:
        if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
            try:
                temp, press, hum, co = receive_data()
                if temp is None:
                    print("Entre al procesamiento de los datos")
                    window_size =int((len(temperatura) - 6) / 2)
                    print(window_size)
                    print(temperatura)
                    data = {
                        "ventana_temperatura": temperatura[:window_size],
                        "ventana_presion": presion[:window_size],
                        "ventana_humedad": humedad[:window_size],
                        "ventana_concentracion": concentracion_co[:window_size],

                        "tRMS": temperatura[window_size],
                        "pRMS": presion[window_size],
                        "hRMS": humedad[window_size],
                        "cRMS": concentracion_co[window_size],

                        "peaks_temperatura" : temperatura[2*window_size +1 :],
                        "peaks_presion" : presion[2*window_size +1 :],
                        "peaks_humedad" : humedad[2*window_size +1 :],
                        "peaks_concentracion" : concentracion_co[2*window_size +1 :],

                        "FFT_temperatura" : temperatura[window_size + 1: 2 * window_size + 1],
                        "FFT_presion" : presion[window_size + 1: 2 * window_size + 1],
                        "FFT_humedad" : humedad[window_size + 1: 2 * window_size + 1],
                        "FFT_concentracion" : concentracion_co[window_size + 1: 2 * window_size + 1]
                    }
                    print("Termine de procesar los datos")
                    return data
                temperatura.append(temp)
                presion.append(press)
                humedad.append(hum)
                concentracion_co.append(co)
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
    print("Entre a mostrar datos")
    presiones = datos["ventana_presion"]
    temperaturas = datos["ventana_temperatura"]
    humedades = datos["ventana_humedad"]
    concentraciones = datos["ventana_concentracion"]

    pRMS = datos["pRMS"]
    tRMS = datos["tRMS"]
    hRMS = datos["hRMS"]
    cRMS = datos["cRMS"]

    peaks_temperatura = datos["peaks_temperatura"]
    peaks_presion = datos["peaks_presion"]
    peaks_humedad = datos["peaks_humedad"]
    peaks_concentracion = datos["peaks_concentracion"]

    FFT_temperatura = datos["FFT_temperatura"]
    FFT_presion = datos["FFT_presion"]
    FFT_humedad = datos["FFT_humedad"]
    FFT_concentracion = datos["FFT_concentracion"]

    print("Voy a graficar el primer grafico")
    graficar(temperaturas, "Temperatura (°C)", "Temperatura", "temperatura.png")
    print("Tamaño de la ventana: ", len(temperaturas), "\n")
    print("Datos temperatura: ",temperaturas)
    print(f"El RMS fue de {tRMS}")
    print(f"Los 5 datos mas altos fueron: {peaks_temperatura}")
    print(f"La transformada de fourier fue: {FFT_temperatura}\n")

    graficar(presiones, "Presión (Pa)", "Presion", "presion.png")
    print("Datos presion: ",presiones)
    print(f"El RMS fue de {pRMS}")
    print(f"Los 5 datos mas altos fueron: {peaks_presion}")
    print(f"La transformada de fourier fue: {FFT_presion}\n")

    graficar(humedades, "Humedad (%%r.h.)", "Humedad", "humedad.png") ##### Rellenar unidad de medida
    print("Datos humedad: ",humedades)
    print(f"El RMS fue de {hRMS}")
    print(f"Los 5 datos mas altos fueron: {peaks_humedad}")
    print(f"La transformada de fourier fue: {FFT_humedad}\n")

    graficar(concentraciones, "Concentración de CO (kΩ)", "Concentracion de CO", "concentracion.png") ##### Rellenar unidad de medida
    print("Datos concentración: ",concentraciones)
    print(f"El RMS fue de {cRMS}")
    print(f"Los 5 datos mas altos fueron: {peaks_concentracion}")
    print(f"La transformada de fourier fue: {FFT_concentracion}")


def solicitar_ventana():
    print("Indicandole al ESP32 que comience a leer")
    comenzar_lectura()
    print("Recibiendo datos...")
    return leyendo()



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

# while True:
#     if ser.in_waiting > 0: #verifica si hay datos en el puerto serial
#         try:
#             message = receive_response()
#             if b"READY" in message:
#                 print("Mensaje READY recibido")
#                 send_message("START\0".encode())
#                 break
#         except:
#             continue
while True:
    desplegar_menu_principal()

    respuesta =  input("Ingresa el número de la opción elegida ")
    print("\n")

    if respuesta == "1":
        """
        Solicitamos una ventana y graficamos los datos
        """
        datos = solicitar_ventana()
        mostrar_datos(datos)

    elif respuesta == "2":
        respuesta2 =  input("Ingresa el nuevo tamaño de la ventana ")
        respuesta2 = int(respuesta2)
        if respuesta2 >= 5:
            """
            Cambiar el numero de ventana y enviar mensaje para que ellos lo cambien
            """
            cambiar_ventana(respuesta2) #Solicitamos al ESP32 que cambie el tamaño de la ventana


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

