from obtener_variables_v2 import Obtener_variables_class
from procesa_excel_v2 import Procesa_excel_clase
from crear_phenopackets_v2 import creacion_de_phenopackets
RUTA_CARPETA = "pheno_archivos_separados_final"

""" 
Este es el script maestro que se encarga de orquestar la ejecución del resto de scripts 
encargados de procesar el archivo inicial, extraer las variables y generar los
phenopackets finales

"""


#-------------------------------------------------------
# Función: subarchivos
# Llama a la clase en la que estan englobadas las funciones encargadas de procesar 
# el archivo tipo excel inicial para generar los subarchivos
#------------------------------------------------------

def subarchivos():
    """
    Llama a Procesa_excel_clase para generar los subarchivos
    """
    procesador_excel = Procesa_excel_clase()


#-------------------------------------------------------
# Función: variables
# Llama a la clase encargada de extraer las variables de los diferentes subarchivos 
# y generar el archivo en el que se almacenan estas variables
#-------------------------------------------------------

def variables(ruta):
    """
    Ejecuta la extracción de variables sobre los archivos generados
    """
    procesador = Obtener_variables_class(ruta)
    resultados = procesador.Busqueda_de_archivos()
    return resultados


#-------------------------------------------------------
# Función: phenopackets
# Engloba todos los procesos necesarios para que los phenopackets se generen correctamente
# a partir del archivo en el que se almacenan las variables 
#-------------------------------------------------------
def phenopackets():
    """
    Crea los phenopackets a partir de las variables almacenadas
    """
    creacion_de_phenopackets()


if __name__ == "__main__":
    subarchivos()
    resultados = variables(RUTA_CARPETA)
    #print(resultados)  # para depuración en caso de querer observar el correcto funcionamiento de esta funcion 
    phenopackets()
