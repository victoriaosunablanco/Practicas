import os
import pandas as pd
import requests
# from procesa_excel_v2 import Procesa_excel_clase
import re
import json
import time


"""

Este script se encarga de extraer las variables de interés de cada uno de los archivos generados por el script que 
procesa el archivo Excel. 
Para ello, utiliza un bucle que recorre cada archivo y extrayendo y normalizando las variables correspondientes.
Además, este script también puede llamar al script encargado de procesar el Excel, de modo que ambos pasos se ejecutarian 
de manera secuencial y automatizada.

"""

class Obtener_variables_class:

    def __init__(self, carpeta):
        self.carpeta = carpeta
        
    #-------------------------------------------------------
    # Función: subarchivos
    # Llama a procesa_excel_clase para que separe el excel original en subarchivos que serán procesados secuencialmente.
    #-------------------------------------------------------
    # def subarchivos():
    #    Procesa_excel_clase 

    # La funcion superior se puede ejecutar simplemente con quitarle # en el caso de querer que al llamar este archivo 
    # se dé tambien el proceso de procesar el excel. 


    #-------------------------------------------------------
    # Función: Busqueda_de_archivos
    # Busca cada uno de los archivos generados por la función anterior y se encarga de llamar a cada una de las
    # funciones necesarias para obtener las variables de interés. 
    #-------------------------------------------------------
    def Busqueda_de_archivos(self):
        resultados =[]
        for filename in os.listdir(self.carpeta):
            if filename.endswith(".csv") or filename.endswith(".xls"):
                filepath = os.path.join(self.carpeta, filename)

                # Se lee el archivo dependiendo la extensión
                # Aunque en general vayan a ser .xls, se plantea la opción de que los archivos puedan tener otra extensión 
                if filename.endswith(".csv"):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)

                print(f"Archivo cargado: {filename}") 


                # Se procesa cada archivo (estan indicadas cada una de las variables que se extraen por cada una de
                # las funciones)
                subject_data = self.Subject_general(df)  # phenopacket_id, phenopacket_subject_id,
                # phenopacket_subject_date_of_birth
                sex_input = self.Subject_input_gender(df)  # phenopacket_subject_sex
                sex_detected = self.Subject_detected_gender(df)  # phenopacket_subject_karyotypic_sex
                biosample_data = self.Biosamples(df)  # phenopacket_biosample_id,
                # phenopacket_biosamples_sampled_tissue_id,
                # phenopacket_biosamples_sampled_tissue_label, phenopacket_biosamples_sampled_type_id,
                # phenopacket_biosamples_sampled_type_label
                interpretation_data = self.interpretations_general(df)  # phenopacket_interpretations_id,
                # phenopacket_interpretations_progress_status
                interpretations_diagnosis = self.interpretations_diagnosis(df)
                # phenopacket_interpretations_diagnosis_disease_id,
                # phenopacket_interpretations_diagnosis_disease_label
                interpretations_genomic_interpretations = self.interpretations_genomic_interpretations(df)
                # phenopacket_interpretations_diagnosis_genomic_interpretations_subject_or_biosample_id, genes, cdnas, 
                # ACMG,phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_id, 
                # phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation,
                # phenopacket_interpretations_diagnosis_genomic_interpretationscall_variant_interpretation_variation_descriptor_expressions,
                # cdnas_value_id,
                # phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds,              
                # phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_label,
                # phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_id
                Medical_actions = self.Medical_actions()  # phenopacket_medical_actions_action_Procedure_code_id,
                # phenopacket_medical_actions_action_Procedure_code_label
                File = self.File(df)  # genommeAssembly, phenopacket_files_atributos, phenopacket_files_uri
                vcf = self.vcf(df)  # genomeAssembly, chrom, pos, ref, alt

                resultados.append({
                    "archivo": filename,
                    "subject_data": subject_data,
                    "sex_input": sex_input,
                    "sex_detected": sex_detected,
                    "biosample_data": biosample_data,
                    "interpretation_data": interpretation_data,
                    "interpretations_diagnosis": interpretations_diagnosis,
                    "interpretations_genomic_interpretations": interpretations_genomic_interpretations,
                    "Medical_actions": Medical_actions,
                    "File": File,
                    "vcf": vcf
                })


        # Se guardan estos resultados en un archivo para que sea posteriormente leido por el programa crear
        # phenopackets y crearlos a partir de estos datos
        with open("resultados.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(resultados, indent=4))
            print("Todo correctamente guardado, el siguiente paso es la creación de los phenopackets")
        
        return resultados



                                                        #=======================Subject=======================#


    """
    En esta sección se extraen todas las variables relacionadas con el sujeto (subject)
    a partir de los datos contenidos en los archivos .xls generados previamente.

    La metodología de extracción es la siguiente:

        - phenopacket_id:
            Se genera a partir del valor de la columna 'NHC', precedido por 'pheno_'.

        - phenopacket_subject_id:
            Corresponde directamente al valor de la columna 'NHC'.

        - phenopacket_subject_date_of_birth:
            Extraído del valor de la columna 'F.Nacimiento'.

        - phenopacket_subject_sex:
            Determinado leyendo el valor del campo 'Resultado' en la fila donde
            'Nombre Tecnica' es igual a 'Input gender'. Se mapea a MALE/FEMALE/OTHER_SEX.

        - phenopacket_subject_karyotypic_sex:
            Determinado leyendo el valor del campo 'Resultado' en la fila donde
            'Nombre Tecnica' es igual a 'Detected gender'. Se transforma a formatos
            estandarizados de cariotipo (XX, XY, etc.).

    Además, cada grupo de variables se extrae mediante funciones separadas, con el fin de
    organizar el código, facilitar la reutilización y mejorar la legibilidad.
    """


    #-------------------------------------------------------
    # Función: Subject_general
    # Extrae variables básicas: phenopacket_id, subject_id y fecha de nacimiento.
    #-------------------------------------------------------

    def Subject_general(self, df):
        # phenopacket.id -> "pheno_" + primer valor de la columna NHC
        phenopacket_id = "pheno_" + str(df.loc[0, "NHC"])

        # phenopacket.subject.id -> primer valor columna NHC
        phenopacket_subject_id = str(df.loc[0, "NHC"])

        # phenopacket.subject.date_of_birth -> primer valor columna F.Nacimiento
        phenopacket_subject_date_of_birth = str(df.loc[0, "F.Nacimiento"])

        return phenopacket_id, phenopacket_subject_id, phenopacket_subject_date_of_birth
 

    #-------------------------------------------------------
    # Función: Subject_input_gender
    # Busca el género introducido por el técnico ("Input gender")
    # y lo convierte a un valor estandarizado.
    #-------------------------------------------------------

    def Subject_input_gender(self, df):
        # Se busca la fila donde 'Nombre Tecnica' == 'Input gender'
        input_gender_row = df[df["Nombre Tecnica"] == "Input gender"]

        if not input_gender_row.empty:
            # Se obtiene el índice para extraer el valor correspondiente en la columna 'Resultado'
            idx = input_gender_row.index[0]
            valor_input = df.loc[idx, "Resultado"]

            # Se mapean de los valores H/M a estandarización interna
            if valor_input == "H":
                phenopacket_subject_sex = "MALE"
            elif valor_input == "M":
                phenopacket_subject_sex = "FEMALE"
            else:
                phenopacket_subject_sex = "OTHER_SEX"
        else:
            # Si no existe esa fila, se desconoce el género
            phenopacket_subject_sex = "UNKNOWN_SEX"

        return phenopacket_subject_sex
    

    #-------------------------------------------------------
    # Función: Subject_detected_gender
    # Extrae el género detectado ("Detected gender"), que representa
    # información de cariotipo, y lo traduce a un formato estandarizado.
    #-------------------------------------------------------

    def Subject_detected_gender(self, df):
         # Se buscar la fila donde columna 'Nombre Tecnica' == 'Detected gender'
        detected_gender_row = df[df["Nombre Tecnica"] == "Detected gender"]
        if not detected_gender_row.empty:
            idx = detected_gender_row.index[0]
            valor_detected = df.loc[idx, "Resultado"]
            if valor_detected == "H":
                phenopacket_subject_karyotypic_sex = "XY"
            elif valor_detected == "M":
                phenopacket_subject_karyotypic_sex = "XX"
            elif valor_detected == "XX":
                phenopacket_subject_karyotypic_sex = "XX"
            elif valor_detected == "XY":
                phenopacket_subject_karyotypic_sex = "XY"
            elif valor_detected == "XO":
                phenopacket_subject_karyotypic_sex = "XO"
            elif valor_detected == "XXY":
                phenopacket_subject_karyotypic_sex = "XXY"
            elif valor_detected == "XXX":
                phenopacket_subject_karyotypic_sex = "XXX"
            elif valor_detected == "XXYY":
                phenopacket_subject_karyotypic_sex = "XXYY"
            elif valor_detected == "XXXY":
                phenopacket_subject_karyotypic_sex = "XXXY"
            elif valor_detected == "XXXX":
                phenopacket_subject_karyotypic_sex = "XXXX"
            elif valor_detected == "XYY":
                phenopacket_subject_karyotypic_sex = "XYY"   
            else:
                phenopacket_subject_karyotypic_sex = "OTHER_KARYOTYPE"
        else:
            phenopacket_subject_karyotypic_sex = "UNKNOWN_KARYOTYPE"

        return(phenopacket_subject_karyotypic_sex)


                                                        #====================Biosamples===================#

    """
    En esta sección se extraen las variables relacionadas con los biosamples.  
    Para ello se aplica la siguiente metodología:

        - phenopacket_biosample_id:
            Se genera a partir del valor de la columna 'Peticion', precedido por 
            'phenopacket_biosample_'.

        - phenopacket_biosamples_sampled_tissue_id:
            Corresponde al identificador del tejido del que proviene la muestra.
            Este ID se obtiene buscando la equivalencia en la ontología UBERON
            (o SO), cuyo repositorio puede consultarse en:
            https://www.ebi.ac.uk/ols4/search?q

            Aunque este proceso podría automatizarse mediante una API, la
            heterogeneidad en cómo están redactados los datos hace que no
            resulte fiable en la práctica.

        - phenopacket_biosamples_sampled_tissue_label:
            Se traduce el valor de 'TipoMuestra' a inglés y se asigna la etiqueta  
            estándar correspondiente al tejido.

        - phenopacket_biosamples_sampled_type_id:
            Por defecto se asigna "SO:0000352" (DNA), debido a la naturaleza de
            los datos procesados y a que el material de muestra suele ser ADN.

        - phenopacket_biosamples_sampled_type_label:
            Etiqueta asociada al ID anterior, que en este caso será "DNA".

    La extracción de cada uno de estos elementos se realiza en esta misma función
    mediante reglas condicionales basadas en el contenido de la columna 'TipoMuestra'.
    """

    #-------------------------------------------------------
    # Función: Biosamples
    # Extrae las variables correspondientes a este apartado,
    # que están principalmente contenidas en la columna 'TipoMuestra'
    #-------------------------------------------------------

    def Biosamples(self, df):

        # Se genera el ID del biosample, que será "phenopacket_biosample_" + primer valor de la columna Peticion

        phenopacket_biosample_id = "phenopacket_biosample_" + str(df.loc[0, "Peticion"])

        #  Se extrae el tipo de muestra (columna 'TipoMuestra')
        if "TipoMuestra" in df.columns:
            valor_biosample_tissue = str(df.loc[0, "TipoMuestra"]).strip()
        else:
            valor_biosample_tissue = "UNKNOWN"

        # Se mapea el tipo de muestra a IDs UBERON/SO y labels
        
        if valor_biosample_tissue.startswith("Sangre periférica en EDTA tubo "):
            phenopacket_biosamples_sampled_tissue_id = "UBERON:0013756"
            phenopacket_biosamples_sampled_tissue_label = "Venous blood"
        elif valor_biosample_tissue == "Tejido fresco Vascular":
            phenopacket_biosamples_sampled_tissue_id = "UBERON:0003614"
            phenopacket_biosamples_sampled_tissue_label = "Blood vessel elastic tissue"
        elif valor_biosample_tissue == "Tejido parafinado Vascular":
            phenopacket_biosamples_sampled_tissue_id = "UBERON:0003614"
            phenopacket_biosamples_sampled_tissue_label = "Blood vessel elastic tissue"
        elif valor_biosample_tissue == "Tejido fresco desconocido":
            phenopacket_biosamples_sampled_tissue_id = "UBERON:0000479"
            phenopacket_biosamples_sampled_tissue_label = "Tissue"
        elif valor_biosample_tissue == "ADN extraído .":
            phenopacket_biosamples_sampled_tissue_id = "SO:0000352"
            phenopacket_biosamples_sampled_tissue_label = "DNA"
        elif valor_biosample_tissue == "Tejido parafinado Linfático":
            phenopacket_biosamples_sampled_tissue_id = "UBERON:0001744"
            phenopacket_biosamples_sampled_tissue_label = "Lymphoid tissue"
        elif valor_biosample_tissue == "Tejido fresco Otros":
            phenopacket_biosamples_sampled_tissue_id = "UBERON:0000479"
            phenopacket_biosamples_sampled_tissue_label = "Tissue"
        elif valor_biosample_tissue == "ADN historico":
            phenopacket_biosamples_sampled_tissue_id = "SO:0000352"
            phenopacket_biosamples_sampled_tissue_label = "DNA"
        else:
            filename= "pheno_" + str(df.loc[0, "NHC"])
            print(f"Tipo de muestra no reconocido en {filename}: {valor_biosample_tissue}")
            phenopacket_biosamples_sampled_tissue_id = "UNKNOWN"
            phenopacket_biosamples_sampled_tissue_label = "UNKNOWN"

        # El material de muestra siempre DNA en este caso 
        phenopacket_biosamples_sampled_type_id = "SO:0000352"
        phenopacket_biosamples_sampled_type_label = "DNA"

        # Lo correspondiente a material_sample se especifica en "crear_phenopackets_v2.py"

        # Se devuelven los resultados agrupados
        return (phenopacket_biosample_id, phenopacket_biosamples_sampled_tissue_id,
                phenopacket_biosamples_sampled_tissue_label, phenopacket_biosamples_sampled_type_id,
                phenopacket_biosamples_sampled_type_label)


                                                        #====================Interpretations===================#


    """
        
        El siguiente paso será la extracción de los datos correspondientes a interpretations.
        Para llevar a cabo el siguiente proceso se va a llevar a cabo la siguiente metodologia para cada uno de los 
        campos correspondientes: 


        - phenopacket_interpretations_id = Valor de la columna "Peticion", precedido por pheno_inter_

        - phenopacket_interpretations_progress_status = Se determina que el valor por defecto sea SOLVED, ya que los 
        resultados son de una base de datos. 

        - phenopacket_interpretations_diagnosis_disease_id = Codificación de la patología asignada en la columna de 
        "Nombre Prueba", debe de ser una ontologia OMIM, sin embargo, debido a la disparidad de términos y 
        terminologias empleadas por los usuarios, no está disponible en OMIM para que refleje de forma correcta 
        la enfermedad a la que se está haciendo referencia. 
        Por ello, en la mayor parte de los casos aparece esta campo rellenado con el valor "UNKNOWN"

        - phenopacket_interpretations_diagnosis_disease_label = Valor de la columna de "Nombre Prueba"

        - phenopacket_interpretations_diagnosis_genomic_interpretations_subject_or_biosample_id = biosample_id

        - ACMG = Valor del campo 'Nombre Tecnica' en la coordenada de la fila donde se recoge 'Clasificación ACMG': 
        se emplea la coordenada de columna de Resultado y de Clasificación ACMG: para las filas  

        - phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_id = 
        Valor de la columna NHC, precedido por pheno_variation_

        - phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation = 
        "GENOMIC" 

        - phenopacket_interpretations_diagnosis_genomic_interpretationscall_variant_interpretation_variation_descriptor_expressions = 
        "hgvs"

        - genes = Se extraen de las filas donde 'Nombre Tecnica' es 'Gen (HGNC):', tomando el valor de la columna 
        "Resultado".
        
        - cdnas = Se obtienen de las filas con 'Nombre Tecnica' = 'Variante cDNA:', asociándose posicionalmente al gen 
        correspondiente; en ausencia de valor se asigna "UNKNOWN".
        
        - cdnas_value_id = Para cada cDNA se consulta, cuando es posible, la API de VariantValidator para obtener 
        información normalizada; en caso de error o ausencia de datos se asigna "UNKNOWN".
        
        - ACMG = Se obtiene de las filas donde 'Nombre Tecnica' es 'Clasificación ACMG:', mapeando el valor de 
        'Resultado' a las categorías estandarizadas del esquema Phenopackets.
        
        - phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds = 
        Identificadores alternativos de la variante, obtenidos principalmente a partir de la información de la variante
         a nivel de aminoácido.
        
        - phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_label = 
        Etiqueta estandarizada de la cigosidad de la variante (heterocigota, homocigota, etc.).
        
        - phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_id = 
        Identificador ontológico GENO asociado al estado alélico.
        
        - genomeAssembly, chrom, pos, ref, alt = Se extraen de las filas donde 'Nombre Tecnica' comienza por 
        "Variante gDNA", normalizando ensamblaje genómico, cromosoma, posición y alelos para su uso en formato VCF.
        
        La extracción de estos campos se encuentra distribuida en varias funciones con el objetivo de mejorar la 
        legibilidad, el mantenimiento del código y la reutilización de la lógica implementada.
    """

    #-------------------------------------------------------
    # Función: interpretations_general
    # Se extraen las variables más simples del apartado de interpretacions
    # El id de interpretations se corresponderá al valor de la columna 'Peticion'
    # y el progress status, tendrá por defecto siempre el mismo valor ("SOLVED")
    #-------------------------------------------------------
    def interpretations_general(self, df):
        # phenopacket_interpretations_id -> pheno_inter_+ primer valor columna Peticion
        phenopacket_interpretations_id = "pheno_inter_" + str(df.loc[0, "Peticion"])

            # phenopacket_interpretations_progress_status -> de momento, este valor va a ser SOLVED
        phenopacket_interpretations_progress_status = "SOLVED"

        return phenopacket_interpretations_id, phenopacket_interpretations_progress_status


    #-------------------------------------------------------
    # Función: interpretations_diagnosis
    # Extrae y codifica los valores correspondientes a los datos relacionados 
    # con la enfermedad 
    #-------------------------------------------------------
    def interpretations_diagnosis(self, df):
        if "Nombre Prueba" in df.columns:
            valor_phenopacket_interpretations_diagnosis_disease_label = str(df.loc[0, "Nombre Prueba"]).strip()
        else:
            valor_phenopacket_interpretations_diagnosis_disease_label = "UNKNOWN"

            # Se Asignan el id y label según el tipo de muestra
            # la mayor parte de ids presentan el valor "UNKNOWN", esto se debe a que debido a que con los datos
            # de los que se dispone, no es posible obtener una ontologia
        if valor_phenopacket_interpretations_diagnosis_disease_label == "Neurofibromatosis tipo 2":
            phenopacket_interpretations_diagnosis_disease_id = "OMIM:101000"
            phenopacket_interpretations_diagnosis_disease_label = "Neurofibromatosis tipo 2"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Displasias esqueléticas":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Displasias esqueléticas"
        elif valor_phenopacket_interpretations_diagnosis_disease_label.startswith ("Genética de malformaciones vasculares: "): 
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Malformaciones vasculares"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Estudio genético dirigido de poliglobulia/trombocitosis en sangre":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "poliglobulia/trombocitosis"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Aneurismas arteriales no sindrómicos":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Aneurismas arteriales no sindrómicos"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Estudio de variante familiar conocida en cardiopatías hereditarias":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Cardiopatías hereditarias"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Miocardiopatía dilatada":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Miocardiopatía dilatada"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Síndrome de Cáncer de Mama y Ovario Hereditario":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Cáncer de Mama y Ovario Hereditario"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Diagnóstico de policitemia vera: SANGRE. qPCR JAK2":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Policitemia"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Trastorno del neurodesarrollo sindrómico":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Trastorno del neurodesarrollo sindrómico"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Trastorno del neurodesarrollo no sindrómico":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "UNKNOWN"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Estudio molecular de colestasis familiar":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Trastorno del neurodesarrollo no sindrómico"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Diabetes MODY":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Diabetes MODY"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Otras nefropatías hereditarias":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "nefropatías hereditarias"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Enfermedades oftalmogenéticas":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Enfermedades oftalmogenéticas"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Hipercolesterolemia familiar (FH) caso índice":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Hipercolesterolemia familiar"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Diabetes mellitus tipo 2":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Diabetes mellitus tipo 2"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Miocardiopatía hipertrófica":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Miocardiopatía hipertrófica"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Otras alteraciones del cribado neonatal":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Alteraciones del cribado neonatal"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Otras hepatopatías genéticas":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Hepatopatías genéticas"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Seguimiento de leucemia en sangre CON biomarcador al Dx":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Leucemia"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Estudio genético de enfermedades dermatológicas":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Enfermedades dermatológicas"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Otras nefropatías hereditarias":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Nefropatías hereditarias"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Hipocrecimiento armónico no sindrómico":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Hipocrecimiento armónico no sindrómico"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Otras distrofias musculares/miopatías":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Distrofias musculares/miopatías"
        elif valor_phenopacket_interpretations_diagnosis_disease_label == "Diagnóstico de tumor sólido en tejido":
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "Tumor solido en tejido" 
        else:
            filename= "pheno_" + str(df.loc[0, "NHC"])
            print(f"Tipo de muestra no reconocido en {filename}: {valor_phenopacket_interpretations_diagnosis_disease_label}")
            phenopacket_interpretations_diagnosis_disease_id = "UNKNOWN"
            phenopacket_interpretations_diagnosis_disease_label = "UNKNOWN"

        return phenopacket_interpretations_diagnosis_disease_id, phenopacket_interpretations_diagnosis_disease_label

    #-------------------------------------------------------
    # Función: interpretations_genomic_interpretations
    # Extrae los diferentes valores de las interpretaciones genomicas, bien empleando un API, 
    # mapeandolo a datos normalizados o bien extrayendo simplemente los datos crudos. 
    #-------------------------------------------------------

    def interpretations_genomic_interpretations(self, df):
        phenopacket_biosample_id = "phenopacket_biosample_" + str(df.loc[0, "Peticion"])
        phenopacket_interpretations_diagnosis_genomic_interpretations_subject_or_biosample_id = phenopacket_biosample_id 

            # Se filtran filas por 'Nombre Tecnica'
        input_hgnc_row = df[df["Nombre Tecnica"] == "Gen (HGNC):"]
        input_cdna_row = df[df["Nombre Tecnica"] == "Variante cDNA:"]
        input_acmg_row = df[df["Nombre Tecnica"] == "Clasificación ACMG:"]
        #input_variante_gDNA_row = df[df["Nombre Tecnica"].str.startswith("Variante gDNA")]
        input_variante_aa_row = df[df["Nombre Tecnica"] == "Variante aminoácido:"]
        input_cigosidad_row = df[df["Nombre Tecnica"] == "Cigosidad:"]
        cdnas_value_id = []
        phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds = []
        phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_label = []
        phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_id = []



            # Si no hay genes, poner valores por defecto
        if not input_hgnc_row.empty:
            genes = [df.loc[idx, "Resultado"]
                     for idx in input_hgnc_row.index]
            cdnas = [df.loc[idx, "Resultado"] for idx in input_cdna_row.index] \
                if not input_cdna_row.empty \
                else (["UNKNOWN"] * len(genes))
            variante_aa = [df.loc[idx, "Resultado"]
                           for idx in input_variante_aa_row.index]
            #variante_gdna = [df.loc[idx, "Resultado"] for idx in input_variante_gDNA_row.index]
            cigosidad = [df.loc[idx, "Resultado"]
                         for idx in input_cigosidad_row.index]

            # Se ha hecho un API para poder buscar mediante el valor del cnda cual será su valor de hgnc de una
            # forma programatica, y que asi sea más sencillo del mismo modo esto se agrega
            if not input_cdna_row.empty: 
                for i, cdna in enumerate(cdnas):
                    if cdna != "UNKNOWN":
                        url = f"https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts/{cdna}"
                        params = {"content-type": "application/json"}
                        headers = {"accept": "application/json"}

                            #  Se configura el proxy con autenticación
                        proxies = {
                            "http": "http://USUARIO:CONTRASEÑA!@proxy.gslb.madrid.org:8080",
                            "https": "http://USUARIO:CONTRASEÑA!@proxy.gslb.madrid.org:8080",
                        }

                        try:
                            response = requests.get(url, headers=headers, params=params) #, proxies=proxies
                            # "activar" el parametro relativo al proxy en caso de estar trabajando en entornos con proxy
                            if response.status_code == 200:
                                data = response.json()
                                hgnc_value = data.get("hgnc")
                                cdnas_value_id.append(hgnc_value)


                            # El siguiente codigo de error (429) era habitual, y es por ello se ha generado
                            # la siguiente condicion.
                            # El error indicaba que se habia alcanzado el rate limit, por ello, haciendo
                            # una espera se ha comprobado que se obtienen estos datos de forma satisfactoria

                            elif response.status_code == 429:
                                intentos = 0
                                max_intentos = 5
                                while intentos < max_intentos:
                                    wait = 2 * intentos  # espera
                                    print(f"Rate limit alcanzado. Reintentando en {wait} segundos...")
                                    time.sleep(wait)
                                    intentos = intentos + 1
                                else:
                                    print(f"Máximo de reintentos alcanzado para {hgnc_value}")
                                    cdnas_value_id.append("UNKNOWN")

                                time.sleep(0.5)  # pequeña pausa para no saturar el API

                            else:
                                print(f"Error {response.status_code} para {cdna}: {response.text}")
                                time.sleep(0.5)  # pequeña pausa para no saturar el API
                        except Exception as e:
                            print(f"Error al consultar VariantValidator para {cdna}: {e}")
                            cdnas_value_id.append("UNKNOWN")
                    else:
                        cdnas_value_id.append("UNKNOWN") 


                # Se procesa cada ACMG correspondiente
            ACMG = []
                #phenopacket_classifications = []
            for i, idx in enumerate(input_acmg_row.index):
                valor_input = df.loc[idx, "Resultado"]

                if valor_input == "Significado incierto":
                    classification = "UNCERTAIN_SIGNIFICANCE"
                elif valor_input == "Patogénica":
                    classification = "PATHOGENIC"
                elif valor_input == "Probablemente patogénica":
                    classification = "LIKELY_PATHOGENIC"
                elif valor_input == "Probablemente benigna":
                    classification = "LIKELY_BENIGN"
                elif valor_input == "Benigna":
                    classification = "BENIGN"
                else:
                    classification = "NOT_PROVIDED"

                ACMG.append(classification)

                #phenopacket_classifications.append(classification)
                # Se inicializa la lista para alternateIds (variante aa)
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds = []

              
            if not input_variante_aa_row.empty:
                variante_aa = [df.loc[idx, "Resultado"]
                               for idx in input_variante_aa_row.index]
                for valor_input in variante_aa:
                    phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds.append(
                        f"Variante aa : {valor_input}"
                    )
            else:
                variante_aa = ["UNKNOWN"]
                phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds.append(
                    "Variante aa : UNKNOWN"
                )

            if not input_cigosidad_row.empty:
                #  Se toma el primer valor (podria ser necesario adaptarlo en caso de querer recoger varios)
                valor_input = cigosidad[0]

                if valor_input == "Heterocigosis":
                    label = "HETEROCIGOSIS"
                    id_ = "GENO:0000135"
                elif valor_input == "Homocigosis":
                    label = "HOMOCIGOSIS"
                    id_ = "GENO:0000136"
                elif valor_input == "Hemicigosis":
                    label = "HEMICIGOSIS"
                    id_ = "GENO:000013"
                elif valor_input == "Homoplasmico":
                    label = "HOMOPLASMICO"
                    id_ = "GENO:0000602"
                elif valor_input == "Heteroplasmico":
                    label = "HETEROPLASMICO"
                    id_ = "GENO:0000603"
                elif valor_input == "Somatico":
                    label = "SOMATICO"
                    id_ = "GENO:0000882"
                else:
                    label = "CIGOSIDAD NO ESPECIFICADA"
                    id_ = "GENO:0000137"
            else:
                cigosidad = ["UNKNOWN"]
                label = "CIGOSIDAD NO ESPECIFICADA"
                id_ = "GENO:0000137"

                # Se guardan los valores finales en variables con nombres largos
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_label = label
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_id = id_



        else:
            genes = ["UNKNOWN"]
            cdnas = ["UNKNOWN"]
            ACMG = ["NOT_PROVIDED"]
            #phenopacket_classifications = ["NOT_PROVIDED"]

        phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_id = "pheno_variation_" + str(df.loc[0, "NHC"])
        phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation = "GENOMIC" 
        phenopacket_interpretations_diagnosis_genomic_interpretationscall_variant_interpretation_variation_descriptor_expressions = "hgvs"


            
        return [
            phenopacket_interpretations_diagnosis_genomic_interpretations_subject_or_biosample_id, genes, cdnas, 
            ACMG,phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_id, 
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation,
            phenopacket_interpretations_diagnosis_genomic_interpretationscall_variant_interpretation_variation_descriptor_expressions,
            cdnas_value_id,
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_alternateIds,              
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_label,
            phenopacket_interpretations_diagnosis_genomic_interpretations_call_variant_interpretation_variation_descriptor_variation_molecule_context_allelic_state_id
            ]

    #-------------------------------------------------------
    # Función: vcf
    # Extrae los valores correspondientes al archivo vcf, que se encuentran en el campo 'Variante gDNA'
    #-------------------------------------------------------
    def vcf(self, df): 
        # Se inicializan  listas vacías para cada variable
        genomeAssembly = []
        chrom = []
        pos = []
        ref = []
        alt = []

        # Se filtran las filas de gDNA y cDNA
        input_atributos = df[df["Nombre Tecnica"].str.startswith("Variante gDNA")]

        # Si no hay variantes, devolvemos una lista con un registro UNKNOWN
        if input_atributos.empty:
            genomeAssembly.append("UNKNOWN")
            chrom.append("UNKNOWN")
            pos.append("UNKNOWN")
            ref.append("UNKNOWN")
            alt.append("UNKNOWN")
            return genomeAssembly, chrom, pos, ref, alt

        # Se recorren todas las filas de gDNA
        for i, fila in input_atributos.iterrows():
            # Se busca el cDNA correspondiente (si existe y está después)
            fila_cdna = None
            for j in range(i + 1, len(df)):
                if df.iloc[j]["Nombre Tecnica"] == "Variante cDNA:":
                    fila_cdna = df.iloc[j]
                    break

            # Valores por defecto
            ga, c, p, r, a = "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"

            # Se procesa la fila de 'nombre técnica', en la poscion de 'variante gDNA'
            valor_texto = str(fila.get("Nombre Tecnica", "")).strip()
            if valor_texto:
                ga_tmp = valor_texto.replace("Variante gDNA", "").strip()
                if ga_tmp == "(hg19):":
                    ga = "GRCh37"
                elif ga_tmp in ["(hg38):", "(GRCh38)"]:
                    ga = "GRCh38"
                elif ga_tmp == "":
                    ga = "UNKNOWN"

            # Se obtienen los valores
            valor = str(fila.get("Resultado", "")).strip()
            valor_cdna = str(fila_cdna.get("Resultado", "")).strip() if fila_cdna is not None else ""

            if valor:
                # Se extrae el valor del cromosoma
                partes = valor.split(":")
                if len(partes) >= 2:
                    c = partes[0].strip()
                elif valor.startswith("chr"):
                    c = valor.split(":")[0].strip()

                # Se extrae la posicion
                numeros = re.findall(r'\d{5,}', valor)
                if numeros:
                    p = numeros[0]

                # Se extraen el alelo de referencia y el alternativo
                if '>' in valor:
                    try:
                        ref_seq, alt_seq = valor.split('>')
                        r = ref_seq[-1] if ref_seq else "UNKNOWN"
                        a = alt_seq[0] if alt_seq else "UNKNOWN"
                    except Exception:
                        r, a = "UNKNOWN", "UNKNOWN"
                elif '>' in valor_cdna:
                    try:
                        ref_seq, alt_seq = valor_cdna.split('>')
                        r = ref_seq[-1] if ref_seq else "UNKNOWN"
                        a = alt_seq[0] if alt_seq else "UNKNOWN"
                    except Exception:
                        r, a = "UNKNOWN", "UNKNOWN"

                # Casos de deleciones y duplicaciones
                if valor.endswith("del"):
                    r, a = "N", "DEL"
                elif valor.endswith("dup"):
                    r, a = "N", "DUP"

            # Se agregan los valores a las listas
            genomeAssembly.append(ga)
            chrom.append(c)
            pos.append(p)
            ref.append(r)
            alt.append(a)

        return genomeAssembly, chrom, pos, ref, alt


 


                                                            #====================Medical_Actions===================#


    """
    En este paso se obtienen las variables correspondientes a las acciones médicas
    (Medical Actions) asociadas al caso.

    Dado que los archivos fuente no contienen información específica que permita
    identificar de forma precisa el tipo de intervención médica realizada, se ha
    optado por asignar por defecto la acción "Genetic Testing", ya que en todos los
    casos analizados se ha llevado a cabo algún tipo de prueba genética.

    Por tanto, se asignan los siguientes valores estandarizados:

        - phenopacket_medical_actions_action_Procedure_code_id:
            Código del procedimiento según la ontología NCIT.
            Valor asignado: "NCIT:C15709"

        - phenopacket_medical_actions_action_Procedure_code_label:
            Etiqueta asociada al procedimiento.
            Valor asignado: "Genetic Testing"

    """                                                                            

    #-------------------------------------------------------
    # Función: Medical_actions
    # Devuelve los identificadores estandarizados correspondientes a la acción
    # médica realizada. En ausencia de información más específica en los datos
    # originales, se asume que en todos los casos se ha efectuado una prueba
    # genética, por lo que se devuelve el procedimiento "Genetic Testing"
    # según la ontología NCIT.
    #-------------------------------------------------------

    def Medical_actions (self):
        phenopacket_medical_actions_action_Procedure_code_id = "NCIT:C15709"
        phenopacket_medical_actions_action_Procedure_code_label = "Genetic Testing"

        return phenopacket_medical_actions_action_Procedure_code_id, phenopacket_medical_actions_action_Procedure_code_label



                                                            #====================File===================#
                                                                              
    """
    Esta función extrae las variables relacionadas con los archivos principales
    (asociados al phenopacket) a partir de los datos procesados del Excel.

    Se obtienen las siguientes variables:

        - genommeAssembly:
            Se extrae de la fila donde "Nombre Tecnica" empieza con "Variante gDNA".
            Se transforma a nombres estandarizados de ensamblajes genómicos:
                "(hg19):"  -> "GRCh37"
                "(hg38):" o "(GRCh38)" -> "GRCh38"

        - phenopacket_files_atributos:
            Lista con atributos de los archivos, que incluye:
                * Sample ID NGS
                * Análisis-Pipeline
                * Ventana
                * NGS
            Se manejan casos en lo que el valor termina con "..." para tomar la siguiente columna si existe.

        - phenopacket_files_uri:
            Lista de rutas de los archivos principales, obtenidas de filas donde
            "Nombre Tecnica" empieza con "Ruta Fichero". Se procesan para extraer
            la parte descriptiva y el valor correspondiente.

    Cada sección del código filtra primero las filas relevantes usando '.str.startswith()'
    y luego itera sobre los índices encontrados para construir las listas de salida.
    Se manejan casos donde no hay datos mediante valores por defecto como "UNKNOWN".
    """


    #-------------------------------------------------------
    # Función: File
    # Extrae los valores correspondientes al genoma de referencia, una serie de atributos
    # en los que se incluyen diferentes datos, como el pipeline empleado, 
    # y la ruta a los archivos.  
    #-------------------------------------------------------

    def File(self, df):

        # Se extraen las rutas de archivos ("Ruta Fichero")
        input_uri = df[df["Nombre Tecnica"].str.startswith("Ruta Fichero")]

        phenopacket_files_uri = []

        if not input_uri.empty:
            # Se obtiene la posición (índice) de la columna "Resultado"
            col_pos = df.columns.get_loc("Resultado")

            # Se obtiene el nombre de la siguiente columna (si existe)
            siguiente_col = df.columns[col_pos + 1] if col_pos + 1 < len(df.columns) else None

            for idx in input_uri.index:
                valor_input = df.loc[idx, "Resultado"]
                nombre_tecnica = df.loc[idx, "Nombre Tecnica"]

                # Se obtiene lo que viene después de "Ruta Fichero"
                parte_despues = nombre_tecnica.replace("Ruta Fichero", "").strip()
                    
                if valor_input.endswith("..."):
                    if siguiente_col:
                        valor_siguiente = df.loc[idx, siguiente_col]
                        phenopacket_files_uri.append(f' Ruta fichero {parte_despues} : {valor_siguiente}')
                    else:
                        phenopacket_files_uri.append("UNKNOWN")
                else:
                    phenopacket_files_uri.append(f' Ruta fichero {parte_despues} : {valor_input}')
        else:
            phenopacket_files_uri.append("UNKNOWN")


        phenopacket_files_uri = str(phenopacket_files_uri)

        # Se extraen los atributos de archivos ("Sample ID NGS", "Análisis-Pipeline", "Ventana", "NGS")
        phenopacket_files_atributos = []

            # a) Sample ID NGS

        input_atributos= df[df["Nombre Tecnica"].str.startswith("Sample ID NGS")]

        if not input_atributos.empty:
                # Se obteniene la posición (índice) de la columna "Resultado"
            col_pos = df.columns.get_loc("Resultado")

                # Se obtiene el nombre de la siguiente columna (si existe)
            siguiente_col = df.columns[col_pos + 1] if col_pos + 1 < len(df.columns) else None

            for idx in input_atributos.index:
                valor_input = df.loc[idx, "Resultado"]
                    
                if valor_input.endswith("..."):
                    if siguiente_col:
                        valor_siguiente = df.loc[idx, siguiente_col]
                        phenopacket_files_atributos.append(valor_siguiente)
                    else:
                        phenopacket_files_atributos.append("UNKNOWN")
                else:
                    phenopacket_files_atributos.append(valor_input)
        else:
            phenopacket_files_atributos.append("UNKNOWN")

            # b) Análisis-Pipeline

        input_atributos_pipeline = df[df["Nombre Tecnica"].str.startswith("Análisis-PipeLine")]

        if not input_atributos_pipeline.empty:
                # Se obteniene la posición (índice) de la columna "Resultado"
            #col_pos = df.columns.get_loc("Resultado")

            for idx in input_atributos_pipeline.index:
                    valor_input = df.loc[idx, "Resultado"]
                    phenopacket_files_atributos.append(f' Analisis-Pipeline {valor_input}')
        else:
            phenopacket_files_atributos.append(f' Analisis-Pipeline UNKNOWN')


            # c) Ventana

        input_atributos_ventana = df[df["Nombre Tecnica"].str.startswith("Ventana")]

        if not input_atributos_ventana.empty:
            # Se obtiene la posición (índice) de la columna "Resultado"
            #col_pos = df.columns.get_loc("Resultado")

            for idx in input_atributos_ventana.index:
                    valor_input = df.loc[idx, "Resultado"]
                    nombre_tecnica = df.loc[idx, "Nombre Tecnica"]

                        # Se obtiene lo que viene después de "Ruta Fichero"
                    parte_despues_ventana = nombre_tecnica.replace("Ventana", "").strip()
                    phenopacket_files_atributos.append(f' Ventana {parte_despues_ventana} {valor_input}')
        else:
            phenopacket_files_atributos.append(f' No ventana')

            # d) NGS

        input_atributos_NGS= df[df["Nombre Tecnica"].str.startswith("NGS")]
        input_uri = df[df["Nombre Tecnica"].str.startswith("Ruta Fichero")]

        if not input_atributos_NGS.empty:
            for idx in input_atributos_NGS.index:
                parte_despues = nombre_tecnica.replace("NGS", "").strip()
                phenopacket_files_atributos.append(f' NGS {parte_despues}')
        else:
            PETICION = str(df.loc[0, "Peticion"])
            NHC = str(df.loc[0, "NHC"])
            #if not input_uri.empty:
                # print(f'El archivo con NHC {NHC} y numero de peticion {PETICION},no presenta panel, pero si Ruta fichero')
                # El mensaje superior ha sido necesario para identificar, durante el desarrollo de la herramienta, 
                # aquellos datos en los que faltaba información necesaria 

        phenopacket_files_atributos = str(phenopacket_files_atributos)

        #  Se extrae el valor que hace alusión al genoma de referencia empleado ("Variante gDNA")
        input_atributos_genommeAssembly = df[df["Nombre Tecnica"].str.startswith("Variante gDNA")]

        if not input_atributos_genommeAssembly.empty:
            nombre_tecnica_actual = input_atributos_genommeAssembly["Nombre Tecnica"].iloc[0]
            genommeAssembly = nombre_tecnica_actual.replace("Variante gDNA", "").strip()
            if genommeAssembly == "(hg19):":
                genommeAssembly = "GRCh37"
            elif genommeAssembly == "(hg38):" or genommeAssembly =="(GRCh38)":
                genommeAssembly = "GRCh38"
        else:
            genommeAssembly="UNKNOWN"

        return genommeAssembly, phenopacket_files_atributos, phenopacket_files_uri


if __name__ == "__main__":
    carpeta = "pheno_archivos_separados_final" # esta carpeta tiene que ser la misma a la que se dirija el output del
    # archivo de procesa_excel.py
    procesador = Obtener_variables_class(carpeta)
    resultados = procesador.Busqueda_de_archivos()
    # print (f'los resultados son {resultados} \n ') # Esto ha sido de utilidad durante la creacion del script para
    # comprobar que las variables de extraian correctamente
