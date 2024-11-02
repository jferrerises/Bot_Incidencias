
# coding: utf-8

import sys
import json

from config.config import *
from app.zonas_spa import remove_stop_words


"""def read_anexoB(filename):
    with open(filename, 'r', encoding='latin-1') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if "CASO" in line:
                caso = line.split("    ")
                for x in caso:
                    if "X" in x:
                        l = x.split("(X)")
                        c = " ".join(l[0].split()[-2:])
          
            if "Detalle:" in line:
                detalle = remove_stop_words(line)
    return c,detalle

def tipo_causa(anexob):
    # Abre json de tipos de causa kw
    with open(f'{DIR_PATH}/app/tipo_causa_kw.json', "r",encoding='utf-8') as file_tc:
        data_tc = file_tc.read()
    dit_tc = json.loads(data_tc)

    caso,detalle = read_anexoB(anexob)
    
    ti_caso = []
    best_case = ''
    best_score = 0

    for f in dit_tc[caso.lower()].items():
        f=tuple(f)
        similarity = len(set(f[1]) & set(detalle)) / len(set(f[1]) | set(detalle))
        if similarity >0:
            ti_caso.append(f[0])
            if similarity > best_score:
                best_case = f[0]
                best_score = similarity
    if len(ti_caso)==0:
        ti_caso.append("Otros")
        best_case = 'Otros'
    return best_case


def read_anexoC(filename):
    with open(filename, 'r' ,encoding='latin-1') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if "Fecha de la interrupción objeto" in line:
                fecha_int = lines[i+1].strip()
            if "Nombre de la Empresa de Distribución" in line:
                comp = lines[i+1].strip()
            if "Denominación y ubicación de las instalaciones" in line:
                zona = lines[i+1].strip()
            if "Descripción del evento o incidente" in line:
                desc = lines[i+1].strip()
            if "Causa del evento o incidente" in line:
                start=i+1
                causa=""
                for i in range(start, len(lines)):
                    if lines[i].strip() =="":
                        break
                    causa += lines[i]
                break
        return fecha_int,desc


def checklists(tc,causal):
    # Abre json de tipos de causa kw
    with open(f'{DIR_PATH}/app/tipo_causa.json', "r",encoding='utf-8') as file_tcc:
        data_tcc = file_tcc.read()
    dit_tcc = json.loads(data_tcc)
    anexos=[]
    for x in dit_tcc[tc].items():
        if x[0]==causal:
            for y in x[1].items():
                for a in y[1]:
                    anx={"subject":"({}) {}".format(y[0],a),
                        "is_done":False}
                    anexos.append(anx)
    return anexos, len(anexos)
"""

def getTipoCausa(filename, dfExcel):
    if filename.endswith('.doc'):
       
        basename = os.path.splitext(filename)[0]
        
        # Find the index of "ANEXOB" in the string
        start_index = basename.index("ANEXOB") + len("ANEXOB")

        # Extract the substring starting from the index after "ANEXOB"
        substring = basename[start_index:start_index + 6]
        
        df = dfExcel[dfExcel['Incidencia']==int(substring)]
        tipoCausa=""
        causa=""
        zona =""
        analista=""
        if not df.empty:
            index = dfExcel[dfExcel['Incidencia']==int(substring)].index
            print("df encontrado :", df.head())
            print("tipo de causa :", dfExcel.loc[index[0],'Tipo de Causa'])
            
            #Obtencion tipo de causa
            tipoCausa = dfExcel.loc[index[0],'Tipo de Causa']

            # Obtencion de causa
            with open(f'{DIR_PATH}/app/tipo_causaNuevo.json', "r",encoding='utf-8') as file_tc:
                data_tc = file_tc.read()
            dit_tc = json.loads(data_tc)
           
            causaDf = dfExcel.loc[index[0],'Causa']
            for key, value in dit_tc[tipoCausa.lower()].items():
                if causaDf in value:
                    causa = key
                    break
                else:
                    causa = 'Otros'
            
            # Obtencion de zona
            #ambito= dfExcel.loc[index[0],'Ámbito'] -- #Original
            ambito= dfExcel.loc[index[0],'Zona']
            print("zona ambito excel:", ambito)
            #with open(f'{DIR_PATH}/app/ambitoyanalistas.json', "r",encoding='utf-8') as file_ambito: -- #oRIGINAL
            with open(f'{DIR_PATH}/app/ambitoyanalistas_central_azuero.json', "r",encoding='utf-8') as file_ambito:
                dic_ambito = file_ambito.read()
            jsonAmbito = json.loads(dic_ambito)
            
            for key, value in jsonAmbito.items():
                if ambito in value['ambito']:
                    zona = key
                    break
            
            # Obtencion Analista
            print("zona redmine: ",zona)
            analista = jsonAmbito[zona]['id_redmine']
        

        return tipoCausa, causa, zona, analista
    

