import os,sys
from datetime import datetime
import json
from config.config import *
from loggerObj import logger



def zona_incidencia(file_path):
    try:
        #cuando se lee el anexo C
        fmt = "%Y-%m-%d %H:%M:%S"
        zona_inc =""
        
        with open("zonas_datetime.json","r") as f:
            datetimes = json.load(f)
        #chr="Chiriqu\u00ed".replace("\u00ed", "í")
        timestamps = {
                    "Oeste":datetime.strptime(datetimes["Oeste"],fmt),
                    "Metro":datetime.strptime(datetimes["Metro"],fmt),
                    "Interior":datetime.strptime(datetimes["Interior"],fmt),
                    "Chiriquí":datetime.strptime(datetimes["Chiriqu\u00ed"],fmt)
        }
        """timestamps = {
                    "Oeste":datetime.strptime("2023-04-02 19:29:00",fmt),
                    "Metro":datetime.strptime("2023-04-02 19:56:00",fmt),
                    "Interior":datetime.strptime("2023-04-02 20:27:00",fmt),
                    "Chiriquí":datetime.strptime("2023-04-02 21:04:00",fmt)
                    
        }"""
        mod_time = os.path.getmtime(file_path)
        mod_date = datetime.fromtimestamp(mod_time)

        keys = list(timestamps.keys())
        for i, key in enumerate(keys):
            if mod_date >= timestamps[key] and (i ==len(keys)-1 or mod_date < timestamps[keys[i+1]]):
                zona_inc=key
                break


        analista=""
        # Abre json de analistas por zonas
        with open(f'{DIR_PATH}/app/zonas_analista.json', "r",encoding='utf-8') as file_al:
            dat_al = file_al.read()
        dit_al = json.loads(dat_al)

        print("zona : ",zona_inc)

        for x in dit_al.items():
        
            for val in dit_al[x[0]]:
                if zona_inc in val['zonas']:
                    print(f"id_remine: {val['id_redmine']} analista : {val['nombre']}")
                    analista = val['id_redmine']
                    break

        return zona_inc,analista
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

