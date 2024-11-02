from pywinauto.application import Application
import pyautogui
import time
from config.config import *
from pywinauto.controls import *
from pywinauto.keyboard import *
from .detectxy import detectImage
from loggerObj import logger
import sys
import py7zr

def copy():
    try:
        ps=monitor['size']
        # Ubica ventana de Informes previamente minimizada y la abre
        time.sleep(10)
        # ESCRIBIR EN CAMPO SEARCH : ANEXO*[AÑO][MES] ... ANEXO*202301 AÑO MES EN CURSO
        curym = dates_app['ymes']
        search_field=f'ANEXO*{curym}'
        """xr,yr=False, False
        x,y=0,0
        while True:
            print("Ubica elemento Search Informes")
            try:
                x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/search_informes.png')
                
                print(f'''x = {x} y={y}''')
                yr=True if y in range(int(ps[1]*0.03),int(ps[1]*24)) else False
                xr=True if x in range(int(ps[0]*0.80),int(ps[0])) else False
                print(f'''btnx = {xr} btny={yr}''')
                if (xr == True) and  (yr == True):
                    print(f"Search field -- Found {x} | {y}")
                    break
                
            except Exception as e:
                print("No encontrado ", e)
                pass
            time.sleep(0.5)

        time.sleep(3)
        pyautogui.click(x,y)"""
        send_keys('^f')
        time.sleep(3)
        pyautogui.typewrite(search_field,interval=0.3)
        time.sleep(5)


        # CLIC EN 1ER ARCHIVO
        print(f"click archivo {int(ps[0]/2)},{int(ps[1]/2)}")
        pyautogui.click(int(ps[0]/2),int(ps[1]/2))
        time.sleep(5)
        # CTRL+A
        send_keys('^a')
        time.sleep(10)
        #INSERTA FUNCION ZIP
        zipfiles()
        
        pyautogui.click(int(ps[0]*0.345),int(ps[1]*0.155))
        time.sleep(2)
        # CTRL+C
        send_keys('^c')
        time.sleep(1)
        #Recupera objeto ventana de citrix
        try:
            app= Application(backend="uia").connect(title='Escritorio Naturgy Cloud - Desktop Viewer', timeout=100)  
        except Exception as e:
            print("exception : ",e)

        rdw = app.window(best_match='Citrix Escritorio Naturgy - Desktop Viewer')
        # Maximiza tamaño de la ventana Citrix para óptimo trabajo
        rdw.minimize()
        dst_folder = f'{DIR_PATH}/ANEXOS_TEMP'
        os.startfile(dst_folder)
        time.sleep(3)
        pyautogui.click(ps[0]/2,ps[1]/2)
        time.sleep(3)
        send_keys('^v')
        return int(ps[0]*0.345),int(ps[1]*0.155)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def zipfiles():
    try:
        #click derecho
        pyautogui.click(button='right')
        #detecta menu zip
        xw,yw=0,0
        while True:
            try:
                xw,yw= detectImage(f'{DIR_PATH}/app/IMAGENES/menu7zip_item.png')
                if xw !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.2)
        pyautogui.click(xw,yw)
        time.sleep(3)
        #abre menu anadir Informes.7z 
        xw,yw=0,0
        while True:
            try:
                xw,yw= detectImage(f'{DIR_PATH}/app/IMAGENES/menu7zip_2.png')
                if xw !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.2)
        time.sleep(3)
        #hace clic en añadir
        pyautogui.click(int(xw*0.94),int(yw*1.10))
        time.sleep(3)
        
        # busca .zip
        send_keys('^f')
        time.sleep(3)
        pyautogui.typewrite("Informes.7z",interval=0.3)
        time.sleep(3)


    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def unzipfiles():
    try:
        print("unzip")
        archive_file="Informes.7z"
        dst_folder = f'{DIR_PATH}/ANEXOS_TEMP'
        print("folder :", dst_folder)
        os.chdir(dst_folder)
        with py7zr.SevenZipFile(archive_file, 'r') as seven_zip:
            seven_zip.extractall()
        os.remove(archive_file)
        
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise