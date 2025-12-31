import json
from phenopackets import (
    Phenopacket, Biosample, OntologyClass, Individual, MetaData, Diagnosis,
    GenomicInterpretation, Interpretation, VariantInterpretation,
    VariationDescriptor, GeneDescriptor, Expression, Resource, File, VcfRecord
)
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToJson
from datetime import datetime, timezone
import os

""" 

Este script busca es leer el archivo .txt generado por el script de "obtener_variables_v2.py" y mapear
cada una de las variables recogidas al formato predefinido de Phenopackets, para asi, poder generar
los phenopackets individuales secuencialmente y de forma correcta. 

"""


#-------------------------------------------------------
# Función: creacion_de_phenopackets
# Engloba todos los procesos neecarios para que los phenopackets se generen correctamente
#-------------------------------------------------------
def creacion_de_phenopackets (): 

#===========================================
#   FUNCIONES AUXILIARES
#===========================================

    #-------------------------------------------------------
    # Función: asegurar_lista 
    # Se encarga de convertir a lista si no lo es, si es un string o int, lo convierte en lista con un solo elemento.
    #-------------------------------------------------------

    def asegurar_lista(x):
        # Si es valor (x), ya es una lista, no se hace nada
        if isinstance(x, list):
            return x
        # Se convierte cualquier string o número en lista de un solo elemento
        if isinstance(x, (str, int)):
            return [x]  # se mantiene el tipo original del valor
        # Para cualquier otro tipo de dato, también lo "envolvemos" en una lista para mantener consistencia
        return [x]


    #-------------------------------------------------------
    # Función: expandir_lista
    # Expande o rellena lista para que tenga la longitud necesaria.
    #-------------------------------------------------------

    def expandir_lista(lista, longitud, default):
        # Otro paso fundamental, ya que sin él, en el caso de tener un número diferente de variables,
        # tambien se generaria un error al crear los Phenopackets
        if len(lista) == longitud:
            return lista
        if len(lista) == 0:
            return [default] * longitud
        if len(lista) == 1:
            return lista * longitud
        return lista[:longitud]


    #-------------------------------------------------------
    # Función: normalizar_interpretations_genomic
    # Normaliza y autocompleta todos los datos necesarios para crear variantes.
    # Devuelve todas las listas preparadas para usarse
    #-------------------------------------------------------

    def normalizar_interpretations_genomic(gi, genomeAssembly, chrom, pos, ref, alt):
    
        # Se extraen los valores de los campos en orden
        biosample_id = asegurar_lista(gi[0])
        genes        = asegurar_lista(gi[1])
        cdnas        = asegurar_lista(gi[2])
        acmg         = asegurar_lista(gi[3])
        descriptor   = asegurar_lista(gi[4])
        variation    = asegurar_lista(gi[5])
        syntax       = asegurar_lista(gi[6])
        hgnc         = asegurar_lista(gi[7])
        alt_ids      = asegurar_lista(gi[8])
        allelic_lbl  = asegurar_lista(gi[9])
        allelic_id   = asegurar_lista(gi[10])

        # Longitud real (tiene que haber tantas variantes como genes)
        n = len(genes)

        # Se autocompleta todo lo demás (este paso es crucial para evitar que se rompa la creación del phenopacket
        # ya que si no está todo perfectamente cuadrado, los valores no se "emparejarian", correctamente, y se 
        # generaria un error)
        # esto tambien se maneja en el archivo de obtener_variables.py, sin embargo, es mejor asegurar el proceso. 
        cdnas        = expandir_lista(cdnas, n, "UNKNOWN")
        hgnc         = expandir_lista(hgnc, n, "UNKNOWN")
        acmg         = expandir_lista(acmg, n, "NOT_PROVIDED")
        descriptor   = expandir_lista(descriptor, n, "var_unknown")
        variation    = expandir_lista(variation, n, "GENOMIC")
        syntax       = expandir_lista(syntax, n, "hgvs")

        # Es necesario asegurarse que alt_ids sea una lista de listas de strings
        new_alt_ids = []
        for x in alt_ids:
            if isinstance(x, list):
                new_alt_ids.append([str(i) for i in x])
            else:
                new_alt_ids.append([str(x)])  #  se convierte string o número en lista de un elemento

        # Se expande para que tenga la longitud correcta
        if len(new_alt_ids) == 0:
            alt_ids = [["UNKNOWN"]] * n
        elif len(new_alt_ids) == 1:
            alt_ids = new_alt_ids * n
        else:
            alt_ids = new_alt_ids[:n]


        allelic_lbl  = expandir_lista(allelic_lbl, n, "UNKNOWN")
        allelic_id   = expandir_lista(allelic_id, n, "UNKNOWN")

        genomeAssembly = expandir_lista(asegurar_lista(genomeAssembly), n, "UNKNOWN")
        chrom          = expandir_lista(asegurar_lista(chrom), n, "UNKNOWN")
        pos            = expandir_lista(asegurar_lista(pos), n, "0")
        ref            = expandir_lista(asegurar_lista(ref), n, "N")
        alt            = expandir_lista(asegurar_lista(alt), n, "N")

        biosample_id   = expandir_lista(biosample_id, n, biosample_id[0])

        return (
            biosample_id, genes, cdnas, acmg,
            descriptor, variation, hgnc,  syntax,
            alt_ids, allelic_lbl, allelic_id,
            genomeAssembly, chrom, pos, ref, alt
        )


    # Se lee el archivo que contiene los resultados
    with open("resultados.txt", "r", encoding="utf-8") as f:
        data = json.load(f)


    # Se procesa cada bloque
    for bloque in data:
        # data corresponde a todo el conjunto de variables extraidas, y cada bloque 
        # se refiere a las variables de cada individuo en particular

        print(f"\n=== Procesando archivo: {bloque['archivo']} ===\n")

        phenopacket_id, phenopacket_subject_id, dob_raw = bloque["subject_data"]
        sex_input = bloque["sex_input"]
        sex_detected = bloque["sex_detected"]

        # Fechas
        fecha = dob_raw[:10]
        dt = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        dob = Timestamp()
        dob.FromSeconds(int(dt.timestamp()))

        # Biosample
        biosample_id, tissue_id, tissue_label, type_id, type_label = bloque["biosample_data"]

        # Interpretation
        inter_id, inter_status = bloque["interpretation_data"]

        # Diagnosis
        disease_id, disease_label = bloque["interpretations_diagnosis"]

        # Genomic interpretations
        gi = bloque["interpretations_genomic_interpretations"] 
        genomeAssembly, chrom, pos, ref, alt = bloque["vcf"]

        # Autocompletado robusto de variantes
        (
            gi_biosample,
            gi_genes,
            gi_cdnas,
            gi_acmg,
            gi_descriptor,
            gi_variation,
            gi_hgnc,
            gi_syntax,
            gi_alt_ids,
            gi_allelic_lbl,
            gi_allelic_id,
            gi_genAssembly,
            gi_chrom,
            gi_pos,
            gi_ref,
            gi_alt
        ) = normalizar_interpretations_genomic(gi, genomeAssembly, chrom, pos, ref, alt)

        # Medical actions
        action_id, action_lbl = bloque["Medical_actions"]

        # Files
        file_genAssembly, file_desc, file_uri = bloque["File"]


    #===========================================
    #   CREACION DEL PHENOPACKET
    #===========================================

    #-------------------------------------------------------
    # Función: crear_phenopacket
    # Crea el phenopacket introduciendo en este esquema cada una de las variables extaridas. 
    #-------------------------------------------------------
        def crear_phenopacket():

            # Individual
            individual = Individual(
                id=phenopacket_subject_id,
                date_of_birth=dob,
                sex=sex_input,
                karyotypic_sex=sex_detected
            )

            # Biosample
            biosample = Biosample(
                id=biosample_id,
                individual_id=phenopacket_subject_id,
                sampled_tissue=OntologyClass(id=tissue_id, label=tissue_label),
                sample_type=OntologyClass(id=type_id, label=type_label),
                material_sample=OntologyClass(id="UBERON:0000479", label="Tissue")
            )

            # Disease
            disease = OntologyClass(id=disease_id, label=disease_label)

            # Crear variantes
            genomic_interpretaciones = []

            for i in range(len(gi_genes)):

                gene_context = GeneDescriptor(
                    symbol=gi_genes[i],
                    value_id=gi_cdnas[i],
                    alternate_ids=gi_alt_ids[i]
                )

                expression = Expression(
                    syntax="hgvs",
                    value=gi_hgnc[i]
                )

                # Asegurar que pos sea entero
                try:
                    pos_val = int(gi_pos[i])
                except (ValueError, TypeError):
                    pos_val = 0

                vcf = VcfRecord(
                    genome_assembly=gi_genAssembly[i],
                    chrom=gi_chrom[i],
                    pos=pos_val,
                    ref=gi_ref[i],
                    alt=gi_alt[i]
                )

                variation_desc = VariationDescriptor(
                    id=gi_descriptor[i],
                    gene_context=gene_context,
                    expressions=[expression],
                    allelic_state=OntologyClass(id=gi_allelic_id[i], label=gi_allelic_lbl[i]),
                    vcf_record=vcf,
                    molecule_context="genomic"
                )

                variant_interpretation = VariantInterpretation(
                    acmg_pathogenicity_classification=gi_acmg[i],
                    variation_descriptor=variation_desc
                )

                bloque_genomic_inter = GenomicInterpretation(
                    subject_or_biosample_id=gi_biosample[i],
                    interpretation_status="UNKNOWN_STATUS",
                    variant_interpretation=variant_interpretation
                )

                # Hablar de que esto se hace porque podemos encontrarnos más de una variante por paciente, por lo que 
                # para recogerlas todas y que no se "rompa" el codigo y podamos recoger bien todas las variables. 
                genomic_interpretaciones.append(bloque_genomic_inter)

            # Full Interpretation
            interpretation = Interpretation(
                id=inter_id,
                progress_status=inter_status,
                diagnosis=Diagnosis(
                    disease=disease,
                    genomic_interpretations=genomic_interpretaciones
                )
            )

            # File
            file = File(
                file_attributes={"genomeAssembly": file_genAssembly, "description": file_desc},
                uri=file_uri
            )

            # Resources
            resources = [Resource(
                id="uberon",
                iri_prefix="http://purl.obolibrary.org/obo/UBERON_",
                name="Uberon Anatomy Ontology",
                namespace_prefix="UBERON",
                url="http://purl.obolibrary.org/obo/uberon.owl",
                version="2025-04-09"
            ), Resource(
                id="ncit",
                iri_prefix="http://purl.obolibrary.org/obo/NCIT_",
                name="NCI Thesaurus OBO Edition",
                namespace_prefix="NCIT",
                url="https://www.ebi.ac.uk/ols4/ontologies/ncit",
                version="25.06e"
            ), Resource(
                id="so",
                iri_prefix="http://purl.obolibrary.org/obo/SO_",
                name="The Sequence Ontology",
                namespace_prefix="SO",
                url="http://www.sequenceontology.org/",
                version="2024-11-18"
            ),Resource(
                id="hgnc",
                iri_prefix="https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
                name="HUGO Gene Nomenclature Committee",
                namespace_prefix="HGNC",
                url="https://www.genenames.org/",
                version="2025-10-22"    
            ),Resource(
                id="refseq",
                iri_prefix="https://www.ncbi.nlm.nih.gov/nuccore/",
                name="NCBI Reference Sequence Database (RefSeq)",
                namespace_prefix="RefSeq",
                url="https://www.ncbi.nlm.nih.gov/refseq/",
                version="Release 232"
            ),Resource(
                id="variantvalidator",
                iri_prefix="https://variantvalidator.org/",
                name="VariantValidator",
                namespace_prefix="VV",
                url="https://variantvalidator.org/",
                version="3.0.2.dev143+g6213c80fe"
            ), Resource(
                id="geno",
                iri_prefix="https://www.ebi.ac.uk/ols4/search?lang=en&q=GENO%3A*******&ontology=geno",
                name="GENO Ontology",
                namespace_prefix="GENO",
                url="https://www.ebi.ac.uk/ols4/ontologies/geno",
                version="2025-07-25"
                )]

            # Metadata
            meta_data = MetaData(
                created=datetime.now(),
                created_by="Victoria",
                phenopacket_schema_version="2.0",
                resources=resources,
                submitted_by="_____"
            )

            # Phenopacket final
            ph = Phenopacket(
                id=phenopacket_id,
                subject=individual,
                biosamples=[biosample],
                interpretations=[interpretation],
                meta_data=meta_data,
                files=[file]
            )

            return ph


        # Se crean los phenopackets y se guardan en formato json

        phenopacket = crear_phenopacket()

        carpeta = "phenopackets_v2"
        os.makedirs(carpeta, exist_ok=True)

        salida = os.path.join(carpeta, f"phenopacket_{phenopacket_subject_id}.json")

        with open(salida, "w", encoding="utf-8") as f:
            f.write(MessageToJson(phenopacket, preserving_proto_field_name=True))

        print(f"✔ Phenopacket generado: {salida}")

if __name__ == "__main__":
    creacion_de_phenopackets()

