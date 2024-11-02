
import configparser
import os,time
import py7zr
import pandas as pd
from app.utils_files import files_processing

config_file = 'config.ini'
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file)
root_folder=r'D:\\SHAREPOINT_ISES\\ISES S.A.S\\Servicios de Catálogo - 3. Desarrollo y Mantenimiento\\Automatizacion generacion de Incidencias\\'

FOLDER_ZIPS = os.path.join(root_folder,f"{config.get('AppConfig', 'folder_cargazip')}")
FOLDER_ANEXOS = os.path.abspath(f"{config.get('AppConfig', 'folder_anexos')}")

def readZips():
    for filename in os.listdir(FOLDER_ZIPS):
        if filename.endswith(".7z"):
            source_path = os.path.join(FOLDER_ZIPS, filename)
            
            # Use py7zr to extract the .7z file
            with py7zr.SevenZipFile(source_path, mode='r') as archive:
                archive.extractall(path=FOLDER_ANEXOS)
            
            os.remove(source_path)
        
        print("folder zip ", FOLDER_ZIPS)

def processAnexos():
    with open('excel_incidencias.txt', 'r') as exfile:
       l =  exfile.read()
    dfExcel = pd.read_excel(l, index_col=False)
    dfExcel = dfExcel.reset_index(drop=True)
    print(dfExcel.head())
    time.sleep(5)
    files_processing(dfExcel)

if __name__ =='__main__':
    readZips()
    time.sleep(5)
    processAnexos()