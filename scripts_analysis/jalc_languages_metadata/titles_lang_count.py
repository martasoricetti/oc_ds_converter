import csv
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import zipfile
import json
import pycountry
from langdetect import detect
from tqdm import tqdm
from jalc_languages_metadata_count import CountMetadataLang
from polyglot.text import Text

cartella = "E:\JOCI\JALC_PRE_24" # Sostituisci con il percorso della tua cartella

countLang = CountMetadataLang()

def get_full_language_name(lang_code):
    try:
        return pycountry.languages.get(alpha_2=lang_code).name
    except AttributeError:
        return lang_code  # Se il codice non viene trovato, restituisci il codice originale

def process_file(file):
    source_dict=[]
    zip_f = zipfile.ZipFile(file)
    source_data = [x for x in zip_f.namelist() if not x.startswith("doiList")]
    # here I create a list containing all the json in the zip folder as dictionaries
    for json_file in source_data:
        f = zip_f.open(json_file, 'r')
        my_dict = json.load(f)
        source_dict.append(my_dict)
    local_lingue = []

    for entity in source_dict:
        data = entity.get("data")
        if data.get("title_list"):
            for title in data["title_list"]:
                if title.get("lang"):
                    lingua = title['lang']
                    full_lang_name = get_full_language_name(lingua)
                    local_lingue.append(full_lang_name)
                else:
                    try:
                        lingua = Text(title['title'])
                        full_lang_name= lingua.language.name
                        local_lingue.append(full_lang_name)
                    except:
                        pass

    return local_lingue

def find_korean(file):
    source_dict = []
    zip_f = zipfile.ZipFile(file)
    source_data = [x for x in zip_f.namelist() if not x.startswith("doiList")]
    # here I create a list containing all the json in the zip folder as dictionaries
    for json_file in source_data:
        f = zip_f.open(json_file, 'r')
        my_dict = json.load(f)
        source_dict.append(my_dict)
    korean_doi = set()

    for entity in source_dict:
        data = entity.get("data")
        if data.get("title_list"):
            for title in data["title_list"]:
                full_lang_name = ''
                if title.get("lang"):
                    lingua = title['lang']
                    full_lang_name = get_full_language_name(lingua)
                else:
                    try:
                        lingua = detect(title['title'])
                        full_lang_name = get_full_language_name(lingua)
                    except:
                        pass
                if full_lang_name == "Korean":
                    korean_doi.add(data["doi"])
    return list(korean_doi)

def main():
    # Crea una lista dei file csv nella cartella
    list_of_zips = countLang.find_zip_subfiles(cartella)

    results = []

    totale_file = len(list_of_zips)

    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_file, list_of_zips), total=totale_file, desc="Elaborazione files"))

    lingue = [lang for sublist in results for lang in sublist]

    # Conta quante volte ogni lingua è stata rilevata
    conteggio = Counter(lingue)

    # Salva i risultati in un file CSV
    with open('E:/lingue_in_jalc(citing)_polyglot.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Lingua', 'Conteggio'])
        for lingua, count in conteggio.items():
            writer.writerow([lingua, count])
    print("Elaborazione completata e risultati salvati in risultati.csv!")\

def main2():
    # Crea una lista dei file csv nella cartella
    list_of_zips = countLang.find_zip_subfiles(cartella)

    results = []

    totale_file = len(list_of_zips)

    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(find_korean, list_of_zips), total=totale_file, desc="Elaborazione files"))

    lingue = [lang for sublist in results for lang in sublist]

    # Salva i risultati in un file CSV
    with open('E:/korean_publications.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['doi'])
        for result in lingue:
            writer.writerow([result])
    print("Elaborazione completata e risultati salvati in risultati.csv!")

if __name__ == '__main__':
    main()