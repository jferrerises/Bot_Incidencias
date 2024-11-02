from app.browserlogin import login
from app.clickcitrix import runCitrixDesktop, informes_folder, run_anexoB, run_anexoC,click_iconoInformes, max_citrix_win
from app.copy_paste import copy, unzipfiles
from app.utils_files import files_processing
from app.notificacion_analistas import procesamiento
import time
from datetime import datetime
from filtro.filtrado_incidencias import run_filtro
from config.config import dates_app,zonas_datetimes
import json
from loggerObj import logger
import pandas as pd



def main():
    #logger.info("INICIO BOT-INCIDENCIAS")
    print("inicia")
    
    
    ## Se obtiene diccionario con zonas y rango de fechas
    dict_incidencias, excel_incidencias= run_filtro()
    
    
    with open('excel_incidencias.txt', 'w') as ex:
        ex.write(excel_incidencias)

    print("dict incidencias :", dict_incidencias)
    # FUncion que notifica a los analistas por zona acerca del rango de Anexos a tramitar
    enviomail = procesamiento(dict_incidencias)
   

    
    """time.sleep(10)
    dates_app['current_datetime'] = datetime.now()
    
    dates_app['ymes']=datetime.now().strftime('%Y%m')
    ## Run Open Citrix desktop
    #login()
    ## Run runCitrixDesktop() hasta login multasSGI
    #time.sleep(80)
    citrix_pid=runCitrixDesktop()
    print("Objeto Cirtix PID :", citrix_pid)
    

    with open("zonas_datetime.json") as f:
        json_timedate = json.load(f)
    
    with open("zonas_datetime.txt","w") as fle:

        for k,v in dict_incidencias.items():
            zona = k
            #Bucle de ANEXO B
            for f in v:
                dates_app['fecha_inicio']=f[0]
                dates_app['fecha_fin'] = f[1]
                print(f"ANEXO B para ZONA:{zona} en RANGO {dates_app['fecha_inicio']} a {dates_app['fecha_fin']} INICIA {datetime.now()}")
                run_anexoB(zona)
            
            #Bucle de ANEXO C
            for f in v:
                if f ==v[0]:
                    print(f"PRIMER RANGO : {f}")
                    dateprint=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    json_timedate[f"{zona}"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    fle.write(f"{zona}: {dateprint}\n")
                dates_app['fecha_inicio']=f[0]
                dates_app['fecha_fin'] = f[1]   
                print(f"ANEXO C para ZONA:{zona} en RANGO {dates_app['fecha_inicio']} a {dates_app['fecha_fin']} INICIO {datetime.now()}")
                run_anexoC(zona)
        fle.write(f"-----------\n")
    
    
    with open("zonas_datetime.json","w") as f:
        json.dump(json_timedate,f)
    # Cierra Ventana MUltas SGI
    click_iconoInformes()
    time.sleep(5)
    # Abre folder donde son exportados los Anexos
    informes_folder()
    # Copia a Folder local Anexos desde Citrix
    x,y= copy()
    #print("Objeto Cirtix PID :", citrix_pid)
    #Espera 15 seg para procesar contenido de folder ANEXOS_TEMP
    time.sleep(15)
    #Retorna a maximizar ventana citrix 
    print("maximizar ventana citrix ")
    max_citrix_win(citrix_pid, x,y)
    time.sleep(5)
    unzipfiles()
    time.sleep(10)
    #Procesa ANEXOS en carpeta ANEXOS_TEMP y crea Peticiones en Redmine
    # Lee ruta de archivo excel y convierte en un dataframe para ser procesado
    with open('excel_incidencias.txt', 'r') as exfile:
       l =  exfile.read()
    dfExcel = pd.read_excel(l, index_col=False)
    dfExcel = dfExcel.reset_index(drop=True)
    print(dfExcel.head())
    time.sleep(5)
    files_processing(dfExcel)"""




if __name__ =='__main__':
    main()