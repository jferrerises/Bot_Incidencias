
from filtro.nuevoFiltradoIncidencias import run_filtro
import json
from datetime import datetime
from loggerObj import logger
import pandas as pd
from app.nuevoUtilFiles import files_processing
import os,time, sys,time
from app.api_redmine import checkIncidenciaRedmine

currDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    #logger.info("INICIO BOT-INCIDENCIAS")
    print("inicia")
    
    
    ## Se obtiene diccionario con zonas y rango de fechas
    dict_incidencias, excel_incidencias= run_filtro()
    
    
    with open('excel_incidencias.txt', 'w') as ex:
        ex.write(excel_incidencias)

    print("dict incidencias :", dict_incidencias)



## Lectura del archivo excel con incidencias y creación de tickets
def processExcel():
    with open('excel_incidencias.txt', 'r') as exfile:
       l =  exfile.read()
    dfExcel = pd.read_excel(l, index_col=False)
    #REvisa en redmine posibles duplicados
    newDF= checkIncidenciaRedmine(dfExcel)
    newDF = newDF.reset_index(drop=True)
    dfExcel = dfExcel.reset_index(drop=True)
    time.sleep(2)
    files_processing(dfExcel)



if __name__ =='__main__':
    try:
        
        logger.info(f"INICIO INCIDENCIAS: {currDate}")
        main()
        print(f"INICIO PROCESAMIENTO DE EXCEL FILTRADO : {currDate}")
        processExcel()
        #time.sleep(30)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise