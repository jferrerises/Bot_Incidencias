
# coding: utf-8

#Las ubicaciones detalladas en el ítem # 7 del Anexo C deben de seguir normas de ortografía como las tildes además de 
#separar cada ubicación por coma.
import json
from fuzzywuzzy import fuzz
import unicodedata
from collections import Counter
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import sys
sys.path.append(".")
from config.config import *


def remove_stop_words(text):
    # Elimina las stopwords de cualquier frase o nombre compuesto 
    stop_words = set(stopwords.words("spanish"))
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha()]
    return [word for word in words if word not in stop_words]


def detect_multiword_words(sentence, art):
    # Detecta del string de entrada aquellas zonas que tienen nombre compuesto de multiple palabras
    words = sentence.split()
    multiword_words = []
    single_words=[]
    i = 0
    while i < len(words):
        if words[i].lower() in art:
            if i + 1 < len(words):
                multiword_word = words[i] + " " + words[i+1]
                multiword_words.append(multiword_word)
                i += 1
        else:
            single_words.append(words[i].lower())
        i += 1
    return multiword_words,single_words

def remove_accents(word):
    # Elimina los acentos
    return unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode('utf-8')


def most_common_element(lst):
    # Obtiene el elemento más común de una lista
    count = Counter(lst)
    return count.most_common(1)[0][0]

def retrieve_zona(json_data, search_string,empresa):
    #para zona
    for main_key, nested_dict in json_data[empresa].items():
        #para provincia
        for nested_key, nested_value in nested_dict.items():
            #w = list(filter(lambda x: x == search_string, nested_key))
            if search_string in nested_key:
                return [main_key.capitalize()]
            #para distrito
            for inner_key, inner_value in nested_value.items():
                #e = list(filter(lambda x: x == search_string, inner_key))
                #e1 = list(filter(lambda x: x == search_string, inner_value))
                if search_string in inner_key:
                    return main_key.capitalize(), nested_key, inner_key
                #para corregimiento
                if search_string in inner_value:
                    return main_key.capitalize(), nested_key, inner_key, search_string
                #para iterar en list del corregimiento
                for listitem in inner_value:
                    d = list(filter(lambda x: x == search_string, inner_value))
                    #if search_string in listitem:
                    if search_string in d:
                        return main_key.capitalize(), nested_key, inner_key, listitem, d

                    


                    
def get_dict_multiword(dit,empresa):
    # Se generan dos listados con los nombres de zonas sencillos y de multiple palabras por empresa de servicio
    result = []
    single=[]
    for region, region_info in dit[empresa].items():     
        for district, district_info in region_info.items():
            if " " in district:
                result.append(district)
            else:
                single.append(district)
            for city, neighborhoods in district_info.items():
                if " " in city:
                    result.append(city)
                else:
                    single.append(city)
                for neighborhood in neighborhoods:
                    if " " in neighborhood:
                        result.append(neighborhood)
                    else:
                        single.append(neighborhood)
    return result, single



def zona_get(stn,comp):
    #print("Zona : ", stn)
    # Abre json de zonas ya procesadas, en minúscula todas
    with open(f'{DIR_PATH}/app/zonas_spa.json', "r",encoding='utf-8') as file:
        data = file.read()
    dit = json.loads(data)

    # Lista de artículos en español
    art = ['el', 'la', 'distrito', 'san', 'las', 'los', 'llano', 'río', 'santa', 
        'cerro', 'villa', 'quebrada', 'panama', 'juan', 'nuevo', 'cirí', 'bahía', 
        'santiago', 'bella', 'pueblo', 'parque', 'playa', 'puerto', 'vista', 
        'buenos', 'nueva', 'punta', 'peñas', 'rincón', 'bajo', 'peña', 'santo', 
        'valle', 'guararé', 'tres', 'agua', 'bajos', 'espino', 'oria', 'altos', 
        'isla', 'canto', 'rodrigo', 'o', 'costa', 'unión', 'catorce', 'corral', 'gatú', 
        'rubén', 'rodeo', 'chiguirí', 'barrios', 'piedras','bocas']

    # Crea los diccionarios filtrados por empresa prestadora
    dict_multi, dict_sing=get_dict_multiword(dit,comp)
    multiword_words,single_words = detect_multiword_words(stn, art)

    nl = multiword_words + single_words
    #print(f"nl : {nl}")

    lts=[]
    
    zona=[]

    for z in dict_multi:
        for x in nl:
            x=x.replace(',','')
            sim = fuzz.ratio(remove_accents(z),remove_accents(x.lower()))
            if sim >= 50:
                if remove_accents(x.lower()) in remove_accents(z):
                    lts.append(z)

    for z in dict_sing:
        for x in nl:
            x=x.replace(',','')
            sim = fuzz.ratio(remove_accents(z),remove_accents(x.lower()))
            if sim >= 75:
                if remove_accents(x.lower()) in remove_accents(z):
                    lts.append(z)
    #print(f"dict_sing : {nl}")
    for st in lts:
        #print(f"antes retrieve_zona : {dit} - {st} - {comp}")
        da = retrieve_zona(dit,st.lower(),comp)
        if da:
            zona.append(da[0])
        else:
            zona.append(comp)

    zonac=""
    analista=""


    try:
        zonac = most_common_element(zona)
    except:
        zonac = comp
        pass
    
    # Abre json de analistas por zonas
    with open(f'{DIR_PATH}/app/zonas_analista.json', "r",encoding='utf-8') as file_al:
        dat_al = file_al.read()
    dit_al = json.loads(dat_al)

    for d in dit_al[comp]:
        if zonac in d['zonas']:
            analista = d['id_redmine']


    
    return zonac, analista,stn


"""z = zona_get("OER - EL CAPURI","EDEMET")
print(z)"""