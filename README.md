Para implementar la funcion de lectura se extrajeron 6 numeros random, uno para cada eje de las aceleraciones y los medidores de orientacion. Estos se introdujeron paulatinamente en arreglos que contendrían toda la data de cada eje.
Para el calculo de los rms se introdujeron acumuladores que iban aumentando al sumar los cuadrados de los valores calculados. Al finalizar la extracción de los datos se calcula la raiz del acumulador para obtener los rms de cada eje.
Para calcular los fft se crean previamente dos arreglos para contener la parte real y la parte imaginaria de los valores de cada eje, luego se entregan estos arreglos a la funcion calcularFFT obteniendo 12 arreglos.
Para calcular los 5 peaks se ordenan los arreglos de data con quicksort y se toman los cinco primeros.
Finalmente, se envían los arreglos de data de forma alternada coordenada por coordenada
