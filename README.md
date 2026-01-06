# Generación de Phenopackets a partir de datos clínicos y genéticos

Este repositorio contiene una herramienta desarrollada en Python para
procesar datos clínicos y genéticos procedentes de un Sistema de
Información de Laboratorio (SIL) hospitalario, concretamente el SIL 
del servicio de genética del Hospital Universitario La Paz y 
transformarlos al formato estándar **Phenopackets** (GA4GH).

La herramienta permite automatizar la depuración, extracción,
normalización y estructuración de la información, generando como
resultado archivos Phenopacket en formato JSON interoperables con otras
herramientas bioinformáticas.

------------------------------------------------------------------------

## Estructura del repositorio

El repositorio contiene los siguientes archivos y carpetas:

-   **procesar_excel_v2.py**\
    Procesa el archivo Excel maestro, elimina duplicados y genera
    subarchivos organizados por número de historia clínica (NHC).

-   **obtener_variables_v2.py**\
    Extrae, transforma y normaliza las variables necesarias para la
    creación de Phenopackets.

-   **crear_phenopackets_v2.py**\
    Mapea las variables al esquema estándar Phenopackets y genera los
    archivos JSON finales.

-   **Herramienta_Phenopackets.py**\
    Script maestro que coordina la ejecución secuencial de los tres
    scripts anteriores.

-   **ejemplo_final.xlsx**\
    Archivo Excel maestro de entrada con datos clínicos y genéticos.

-   **resultados.txt**\
    Archivo intermedio con las variables extraídas y procesadas.

-   **pheno_Archivos_separados_final/**\
    Carpeta que contiene los archivos Excel separados por NHC.

-   **phenopackets_v2/**\
    Carpeta que contiene los Phenopackets generados en formato JSON.

------------------------------------------------------------------------

## Flujo de trabajo

1.  **Procesamiento del Excel maestro**\
    `procesar_excel_v2.py` lee el archivo `ejemplo_final.ods`, elimina
    registros duplicados y genera subarchivos por NHC. En caso de querer
    procesar otro archivo, es necesario modificar el parametro
    'archivo_entrada' y especificar en él el nombre del nuevo
    archivo que se desee procesar. 
    

3.  **Extracción y normalización de variables**\
    `obtener_variables_v2.py` procesa los subarchivos y genera el archivo
    intermedio `resultados.txt`.

4.  **Creación de Phenopackets**\
    `crear_phenopackets_v2.py` genera los Phenopackets individuales en
    formato JSON.

5.  **Ejecución conjunta**\
    `Herramienta_Phenopackets.py` permite ejecutar todo el flujo de
    forma automática.

------------------------------------------------------------------------

## Requisitos

-   Python 3.12 (probado con Python 3.12.3)
-   Paquetes de Python:
    -   pandas
    -   openpyxl
    -   odfpy
    -   requests
    -   phenopackets (versión 2.0.2.post5)
    -   protobuf

Instalación de dependencias:

``` bash
pip install pandas openpyxl odfpy requests phenopackets protobuf
```

------------------------------------------------------------------------

## Consideraciones sobre los datos

Por motivos de privacidad, los siguientes campos del archivo ejemplo_final.ods
han sido **falseados o anonimizados**:

-   Número de historia clínica (NHC)
-   CIPA
-   Fecha de nacimiento
-   Rutas internas de archivos
-   Número de ADN
-   Año
-   Petición clínica
-   Campo de resultado largo (contenido reducido o eliminado en su mayor
    parte)

Estos datos se incluyen únicamente con fines de demostración y
desarrollo.

------------------------------------------------------------------------

## Resultados

El resultado final del proceso son archivos Phenopacket en formato JSON,
estos Phenopackets finales se pueden encontrar en la carpeta 
**phenopackets_v2/** .

------------------------------------------------------------------------
