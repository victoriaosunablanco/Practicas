import pandas as pd
import os

""" 

Este script busca dividir el archivo .xls/.ods/... original, es decir, obtener archivos separados, y que cada archivo
contenga los datos de cada paciente individual.
Por lo que el archivo de entrada será un archivo tipo excel todos los datos, en el proceso se obtendrán subarchivos 
individuales por paciente,y se procesarán para eliminar aquellas filas que estén repetidas y de esta forma evitar 
redundancias en los archivos. 

"""


class Procesa_excel_clase():
    @staticmethod  # Sirve para definir un método que pertenece a la clase pero no está vinculado ni a la instancia
    # ni a la clase en sí misma.
    # Esto significa que el método no recibe automáticamente self (la instancia) ni cls (la clase) como primer argumento,
    # lo que lo hace útil para funciones de utilidad que están lógicamente asociadas a la clase pero no es estrictamente
    # necesario acceder a su estado


    #-------------------------------------------------------
    # Función: procesar_archivo_excel
    # Realiza el preprocesamiento de un archivo Excel clínico,
    # generando archivos individuales por paciente sin duplicados.
    # 
    #-------------------------------------------------------
    def procesar_archivo_excel(archivo_entrada, columna_separacion, columnas_con_duplicados, carpeta_salida):
        # Se detecta la extensión del archivo de entrada 
        extension = os.path.splitext(archivo_entrada)[1].lower()

        # Selección automática del engine
        # Este paso se realiza con el objetivo de que el programa no genere un error en caso de tener una extensión
        # diferente a la esperada
        engines = {
            ".ods": "odf",
            ".odf": "odf",
            ".xlsx": "openpyxl",
            ".xls": "xlrd"
        }

        engine = engines.get(extension, None)

        # Se intenta leer el archivo habiendole asignado el engine correcto
        try:
            if engine:
                df = pd.read_excel(archivo_entrada, engine=engine)
            else:
                # Intenta leer sin engine (pandas intentará adivinarlo sino)
                df = pd.read_excel(archivo_entrada)
        # Si se da el caso de que ninguno de los engine pensados concuerda con necesario para leer el archivo de entrada,
        # saltará una excepción mostrando los siguientes mensajes
        except Exception as e:
            print(f"\n Error al leer el archivo '{archivo_entrada}': {e}")
            print(" Intenta convertir tu archivo a .xlsx o .ods, o revisa que no esté dañado.\n")
            return

        # Se crea la carpeta de salida en el caso de que no exista
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)

        # Se obtienen los valores únicos para dividir los archivos
        # Los archivos se separarán en funcion de la columna NHC
        try:
            valores_unicos = df[columna_separacion].dropna().unique()
        except Exception as e:
            print(f"Error al acceder a la columna '{columna_separacion}': {e}")
            return

        for valor in valores_unicos:
            # Se realiza el proceso de filtrado
            df_filtrado = df[df[columna_separacion] == valor]

            # Se eliminan aquellas filas con duplicados
            df_sin_duplicados = df_filtrado.drop_duplicates(subset=columnas_con_duplicados)

            # Se crea el nombre de cada archivo
            nombre_archivo = f"pre_pheno_{valor}.xls"
            ruta_salida = os.path.join(carpeta_salida, nombre_archivo)

            # Se guardan los archivos resultantes en formato .xls
            try:
                with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
                    df_sin_duplicados.to_excel(writer, index=False)
            # En caso de haber algún error salga la siguiente excepcion con su mensaje correspondiente
            except Exception as e:
                print(f" Error al guardar el archivo '{ruta_salida}': {e}")
                continue

        print(f"Proceso de subdivisión del archivo inicial de entrada correctamente completado. "
              f"Archivos guardados en '{carpeta_salida}'.")



archivo_entrada = 'ejemplo_final.ods' #esto será necesario cambiarlo en caso de querer procesar otro archivo 
carpeta_salida = 'pheno_archivos_separados_final'
columna_separacion = 'NHC'
columnas_con_duplicados = ['Year', 'Mes', 'Peticion', 'F.Registro', 'CIPA', 'NHC', 'Sexo', 'F.Nacimiento',
                           'TipoMuestra', 'Cod.Prueba', 'Nombre Prueba', 'Cod.Tecnica', 'Nombre Tecnica','TipoPrueba',
                           'Proceso', 'SubProceso', 'Resultado',  'Resultado', 'Arbol']

Procesa_excel_clase.procesar_archivo_excel(archivo_entrada, columna_separacion, columnas_con_duplicados, carpeta_salida)
