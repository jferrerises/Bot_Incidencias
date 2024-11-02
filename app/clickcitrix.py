from pywinauto.application import Application
import pyautogui
import mouse
import time
import keyboard
from .detectxy import detectImage
from datetime import datetime
import json
import sys
from config.config import *
from pywinauto.controls import *
from pywinauto.keyboard import send_keys
from pywinauto import Desktop, findwindows
from loggerObj import logger


def runCitrixDesktop():
    try:
        # Función para iniciar el escritorio Citrix y acceder a la carpeta de aplicaciones corporativas. No tiene parámetro.
        # pywinauto.Application captura la ventana del escritorio de citrix. El objeto es almacenado en un objeto tipo pickle
        ps=pyautogui.size()
        monitor['size']=ps
        print("montior dimensions : ", ps)
        time.sleep(5)
        #------#
        try:
            app= Application(backend="uia").connect(title='Escritorio Naturgy Cloud - Desktop Viewer', timeout=100)  

            rdw = app.window(best_match='Escritorio Naturgy Cloud - Desktop Viewer')
            # Maximiza tamaño de la ventana Citrix para óptimo trabajo
            time.sleep(5)
            rdw.maximize()
            time.sleep(5)
        except Exception as e:
            print("exception : ",e)
            _, _, tb  = sys.exc_info()
            functionName = tb.tb_frame.f_code.co_name
            logger.error(f"Excepción de ejecución en {functionName} : {e}")
            raise

        # Los bucles While permiten esperar hasta que la función de detección de imagen reconozca el ícono correspondiente
        # While espera a que aparezca en el escritorio el icono de aplicaciones corporativas
        btnx,btny = 0,0
        while True:
            print("Esperando aplicaciones_corporativas_icono")
            try:
                btnx,btny= detectImage(f'{DIR_PATH}/app/IMAGENES/aplicaciones_corporativas_icono.png')
                if (btny >0) and (btnx>0):
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.5)
        #guardar como pickle
        time.sleep(8)
        print(f"coordenadas icono x={btnx} y={btny}")
        # Abre acceso a folder informes
        print(f"click en aplicaciones corporativas (btnx,btny)")
        #s = informes_folder(btnx,btny)
        # Abre Aplicaciones Corportativas
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/aplicaciones_corporativas_icono.png') 
        mouse.move(btnx,btny)
        mouse.double_click()
        time.sleep(7)
        
        #if s==1:
        send_keys('%{VK_SPACE}+x')
        time.sleep(3)
        login_multas()
        process_id = rdw.process_id()
        return process_id
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def login_multas():
    try:
        ps=monitor['size']
        #Maximiza la ventana de los accesos directo s
        #keyboard.press_and_release('windows+up')
        #Localiza acceso a Multas SGI
        print("Localiza acceso a Multas SGI")
        x,y=0,0
        while True:
            print("Localiza acceso a Multas SGI")
            try:

                x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/acceso_multas_sgi.png')
                print(f"coordenadas multassgi {x} | {y}")
                break
            except Exception as e:
                print("No encontrado")
                pass
            time.sleep(0.5)

        mouse.move(x,y)
        mouse.double_click()
        time.sleep(1)
        # ALT+F4 cierra ventana 
        #send_keys('%{F4}')
        time.sleep(5)
        
        print("Carga Multas SGI")
        ym1,ym2=calculate_point_range(0.55*ps[1], 15)
        xm,ym=0,0
        while True:
            print("Localiza acceso a Multas SGI")
            try:

                xm,ym= detectImage(f'{DIR_PATH}/app/IMAGENES/multas_sgi.png')
                print(f"coordenadas multassgi {xm} | {ym}")
                xp= True if ym in range(ym1,ym2) else False
                if xp==True:
                    break
            except Exception as e:
                print("No encontrado")
                pass
            time.sleep(0.5)

        time.sleep(10)
        #Ingreso de credenciales de Multas SGI
        print("Ingreso de credenciales de Multas SGI")
        mouse.move(int(0.55*ps[0]),int(0.55*ps[1]))
        #mouse.move(int(xm+20),int(ym+8))
        mouse.click('left')
        keyboard.write(login_cred['username_multas'], delay=0.5)
    
        time.sleep(4)
        mouse.move(int(0.55*ps[0]),int(0.57*ps[1]))
        #mouse.move(int(xm+20),int(ym+40))
        mouse.click('left')
        keyboard.write(login_cred['passwd_multas'], delay=0.5)
        time.sleep(4)
        keyboard.press('enter')
        time.sleep(10)    
        x,y=0,0
        while True:
            print("Cierra cuadro emergente")
            try:
                x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/cerrar_info_multasSGI.png')
                break
            except Exception as e:
                print("No encontrado")
                pass
            time.sleep(0.5)
        mouse.move(int(x+199),y)
        mouse.click('left')
        time.sleep(4)
       
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def run_anexoB(zona):
    menu_reportes()
    try:
        ps=monitor['size']
        #Abre submenu AnexoC
        # Toma como parametro tamaño de monitor
        print(f"menu_anexo_B() - monitor_size {ps}")
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/menu_anexo_c_multas_sgi.png')
        print(f"menu_anexo_B() - {int((float(0.06)*ps[0]))} , {int((float(0.23)*ps[1]))}")
        mouse.move(int((float(0.06)*ps[0])),int((float(0.23)*ps[1])),duration=0.5)
        mouse.click('left')
        time.sleep(3)
        sel_x,sel_y = seleccion_reportes()
        ACT_ZONA =""
        ACT_SECTOR=""
        if zona in ['Oeste', 'Metro']:
            ACT_ZONA="GER_PANAMA"
            ACT_SECTOR = zona
            
        elif zona =="Interior":
            ACT_ZONA="GER_INTERIOR"

        elif zona =="Chiriquí":
            ACT_ZONA="GER_CHIRIQUI"
        
        reporte_zonas(sel_x,sel_y,ACT_ZONA,ACT_SECTOR)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def run_anexoC(zona):
    menu_reportes()
    try:
        ps=monitor['size']
        #Abre submenu AnexoC
        # Toma como parametro tamaño de monitor
        print(f"menu_anexo_c() - monitor_size {ps}")
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/menu_anexo_c_multas_sgi.png')
        print(f"menu_anexo_c() - {int((float(0.06)*ps[0])),int((float(0.25)*ps[1]))}")
        mouse.move(int((float(0.06)*ps[0])),int((float(0.25)*ps[1])),duration=0.5)
        mouse.click('left')
        time.sleep(3)
        sel_x,sel_y = seleccion_reportes()
        ACT_ZONA =""
        ACT_SECTOR=""
        if zona in ['Oeste', 'Metro']:
            ACT_ZONA="GER_PANAMA"
            ACT_SECTOR = zona
            
        elif zona =="Interior":
            ACT_ZONA="GER_INTERIOR"

        elif zona =="Chiriquí":
            ACT_ZONA="GER_CHIRIQUI"
        zonas_datetimes[zona]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reporte_zonas(sel_x,sel_y,ACT_ZONA,ACT_SECTOR)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def menu_reportes():
    try:
        ps=monitor['size']
        # Detecta y abre menu Reportes.
        # Toma como parametro tamaño de monitor
        print(f"menu_reportes() - monotor_size {ps}")
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/menu_reportes_multas_sgi2.png')
        mouse.move(int((float(0.06)*ps[0])),int((float(0.045)*ps[1])),duration=0.5)
        mouse.click('left')
        time.sleep(3)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def seleccion_reportes():
    try:
        # Detecta cuadro de seleccion de reportes
        print("seleccion_reportes()")
        sel_x,sel_y = detectImage(f'{DIR_PATH}/app/IMAGENES/seleccion_cuadro.png')
        print(f'{sel_x} | {sel_y}')
        return sel_x,sel_y
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def generate_report(sel_x, sel_y):
    try:
        time.sleep(2)
        # Type "Desde" casilla. Corresponde al 1er día del mes
        pyautogui.click(int(sel_x*0.88),int(sel_y*1.15))
        pyautogui.typewrite(dates_app['fecha_inicio'], interval=0.5)
        time.sleep(2)
        # Type "Hasta" casilla. Corresponde al día actual del mes
        pyautogui.click(int(sel_x*1.20),int(sel_y*1.15))
        pyautogui.typewrite(dates_app['fecha_fin'], interval=0.5)
        time.sleep(2)
        # Clic en Boton Aceptar
        pyautogui.click(int(sel_x*0.90),int(sel_y*1.35))
        # Ejecuta la funcion de exportar los Anexos
        ef = exportar_files()
        if ef ==1:
            time.sleep(3)
        else:
            raise("Error de exportación")
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def reporte_zonas(sel_x,sel_y,ACT_ZONA,ACT_SECTOR):
    try:
        print(f'''reporte zonas: {ACT_ZONA} - {ACT_SECTOR}''')
        #reporte_zonas(sel_x,sel_y,ACT_ZONA,ACT_SECTOR):
        ###LAS ZONAS Y SECTORES ENTRAN EN UN LOOP FOR PARA SELECCIONAR ZONA X ZONA Y SECTOR CORRESPONDIENTE
        #Despliega ZOna coords (sel_x, se_y*0.74)
        pyautogui.click(int(sel_x),int(sel_y*0.74))
        # Funcion para almacenar en dict las coordenadas de los Sectores y Zonas
        coords_zonas(sel_x,sel_y)
        #Genera el dia actual en formato dd/mm/aaaa
        #Selecciona la gerencia de trabajo
        pyautogui.click(dict_zonas[ACT_ZONA]['coords'][0],dict_zonas[ACT_ZONA]['coords'][1])
        time.sleep(0.5)
        if ACT_ZONA=="GER_PANAMA":
            pyautogui.click(sel_x, sel_y*0.98)
            time.sleep(0.5)
            pyautogui.click(dict_zonas[ACT_ZONA][ACT_SECTOR][0], dict_zonas[ACT_ZONA][ACT_SECTOR][1])
            time.sleep(2)
            generate_report(sel_x, sel_y)
        else:
            generate_report(sel_x, sel_y)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise
    
def calculate_point_range(point, prc):
    try:
        plus = point*(1+(prc/100))
        minus = point*(1-(prc/100))
        return int(minus),int(plus)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def exportar_files():
    try:
        ps=monitor['size']
        # Exporta Anexo a FOlder Informes en Escritorio Remoto
        #time.sleep(60)
        x,y=0,0
        while True:
            print("esperando ventana informes")
            try:
                #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/barra_informes_multaSGI.png')
                x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/anexo_confirmado_generacion.png')
                print(f'coordenadas barra anexo : {x} | {y}')
                #byy = True if by in range(by1,by2) else False
                barry=True if y in range(75,707) else False
                barrx=True if x in range(5,1358) else False
                print(f"barra_informes_multaSGI OK {x} | {y}")
                
                if (barry == True) and  (barrx == True):
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(2)
        """while True:
            print("esperando ventana informes")
            try:
                #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/barra_informes_multaSGI.png')
                x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/anexo_confirmado_generacion.png')
                print(f'coordenadas barra anexo : {x} | {y}')
                break
            except Exception as e:
                print("not found")
                pass
            time.sleep(2)"""
        pyautogui.click(x,y,clicks=2)
        time.sleep(4)
        # menu edicion
        
        pyautogui.click(ps[0]*0.06,ps[1]*0.04)
        time.sleep(1)
        # exportar reporte
        pyautogui.click(ps[0]*0.08,ps[1]*0.19)
        #Bucle para esperar a que se exporten todos los reportes
        btnx1,btnx2=calculate_point_range(ps[0]*0.53, 15)
        btny1,btny2=calculate_point_range(ps[1]*0.53, 15)
        by=ps[1]*0.94
        btnx,btny=0,0
        start_time=time.time()
        interval=10*60
        while True:
            print("Esperando Fin Exportacion")
            try:
                #bx,by= detectImage(f'{DIR_PATH}/app/IMAGENES/exportando_incidencia.png')
                time.sleep(1)
                #btnx,btny= detectImage(f'{DIR_PATH}/app/IMAGENES/fin_exportacion.png')
                btnx,btny= detectImage(f'{DIR_PATH}/app/IMAGENES/fin_exportacion2.png')
                #print(f"Exportando incidencia {bx} {by}")
                
                #byy = True if by in range(by1,by2) else False
                btnyy=True if btny in range(btny1,btny2) else False
                btnxx=True if btnx in range(btnx1,btnx2) else False
                            
                if (btnyy == True) and  (btnxx == True):
                    print(f"Alert Window -- Found {btnx} | {btny}")
                    break
                else:
                    print(f"Alert Window -- Missing {btnx} | {btny}")
                    #funcion para mantener "viva" la pagina
                    if time.time() - start_time >=interval:
                        keep_alive(ps)
                        start_time = time.time()              

            except Exception as e:
                print("ninguna imagen :",e)
                pass
            
            time.sleep(10)
        # detectar aler window de exportacion de datos finalizada -- ok
        """btnx,btny=0,0
        while True:
            print("Esperando alert WIndow")
            try:
                btnx,btny= detectImage(f'{DIR_PATH}/app/IMAGENES/fin_exportacion.png')
                if btnx !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            
            time.sleep(0.5)"""
        time.sleep(2)
        print(f"fin exportacion btn ok")
        # Clic en Boton OK para cerrar alert Window de notificacion - Exportacion finalizada
        #pyautogui.click(btnx+101,btny+52)
        pyautogui.click(btnx+20,btny+29)
        time.sleep(2)
        print("Cierre ventana anexos")
        #pyautogui.click(ps[0]*0.53,ps[1]*0.15)
        pyautogui.click(ps[0]*0.99,ps[1]*0.04)
        time.sleep(5)
        return 1
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise
    

def click_iconoInformes():
    try:
        ps=monitor['size']
        # Cierra ventana Multas SGI
        pyautogui.click(ps[0]/2,ps[1]/2)
        time.sleep(2)
        print("send_close_keys()")
        send_keys("%{F4}")
        time.sleep(2)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def informes_folder():
    try:
        ps=monitor['size']
        # Funcion para dejar activo y minimizado el folder de Multas/Informes y asi usarlo posteriormente para copiar los Anexos B yC. 
        # Toma como parametro el tamaño del escritorio, y coords (X,Y) del icono de aplicaciones corporativas
        print("abrir ventana informes")
        """print(f"mouse.move(btnx,btny) : {btnx,btny}")
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/aplicaciones_corporativas_icono.png') 
        mouse.move(btnx,btny)
        mouse.double_click()
        time.sleep(3)
        # Localiza acceso a Multas SGI
        #print("Maximiza la ventana  Multas SGI")
        send_keys('%{VK_SPACE}+x')"""
        time.sleep(3)
        print("Localiza acceso a Multas SGI")
        xz,yz=0,0
        while True:
            try:
                xz,yz= detectImage(f'{DIR_PATH}/app/IMAGENES/acceso_multas_sgi.png')
                if xz !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.2)
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/acceso_multas_sgi.png')
        pyautogui.click(xz,yz,button='right')
        time.sleep(3)
        # abre folder informes
        xw,yw=0,0
        while True:
            try:
                xw,yw= detectImage(f'{DIR_PATH}/app/IMAGENES/open_file_location.png')
                if xw !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.2)
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/open_file_location.png')
        pyautogui.click(xw,yw)
        #lleva el mouse fuera de la pantalla para deteccion clara de la imagen
        mouse.move(ps[0]/2,ps[1])
        time.sleep(5)
        print("pantalla ejecutable/informes")
        xi,yi=0,0
        while True:
            try:
                xi,yi= detectImage(f'{DIR_PATH}/app/IMAGENES/informes_folder_click.png')
                if xi !=0:
                    break
                keyboard.send('up')
            except Exception as e:
                print("ninguna imagen :",e)
                keyboard.send('up')
                pass
            
            time.sleep(0.2)
                
        time.sleep(5)
        pyautogui.click(xi,yi, clicks=2)
        xii,yii=0,0
        # Espera a que la ventana del folder informes aparezca
        while True:
            print("barra_informes")
            try:
                xii,yii= detectImage(f'{DIR_PATH}/app/IMAGENES/barra_informes_folder2.png')
                if xii !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.5)
        time.sleep(5)
        
        #keyboard.send('alt+space+n')
        #pyautogui.click(monitor['size'][0],2)
        """time.sleep(5)
        # Detecta posicion boton informes folder en barra de accesos
        xa,ya = 0,0
        while True:
            print("barra_informes")
            try:
                xa,ya= detectImage(f'{DIR_PATH}/app/IMAGENES/informes_folder.png')
                if xa !=0:
                    break
            except Exception as e:
                print("ninguna imagen :",e)
                pass
            time.sleep(0.5)
        #x,y= detectImage(f'{DIR_PATH}/app/IMAGENES/informes_folder.png')
        print(f"boton informes barra : {xa} | {ya}")
        btnXY['informes_folder']=tuple((xa,ya))"""
        return 1
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise



def coords_zonas(sel_x, sel_y):
    try:
        #Identifica y almacena en dict() las coordenadas de los sectores y zonas a generar reporte
        # Ger PAnama
        dict_zonas['GER_PANAMA']['coords'] = tuple((int(sel_x),int(sel_y*0.83)))
        dict_zonas['GER_PANAMA']['Oeste'] = tuple((int(sel_x),int(sel_y*1.06)))
        dict_zonas['GER_PANAMA']['Metro']=tuple((int(sel_x),int(sel_y*1.14)))
        # GER_INTERIOR
        dict_zonas['GER_INTERIOR']['coords'] = tuple((int(sel_x),int(sel_y*0.92)))
        # GER_CHIRIQUI
        dict_zonas['GER_CHIRIQUI']['coords'] = tuple((int(sel_x),int(sel_y)))
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def keep_alive(ps):
    try:
        #Funcion para mantener activa la ventana de citrix
        pyautogui.click((ps[0]/2)-20,ps[1]/3)
        pyautogui.click(ps[0]/2,ps[1]/3)
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def max_citrix_win(process_id,x,y):
    try:
        ps=monitor['size']
        w_handle = findwindows.find_windows(title=u'Escritorio Naturgy Cloud - Desktop Viewer')[0]
        print("Handle:",w_handle)
        print("Process id 2:", process_id)
        try:
            app= Application(backend="uia").connect(process=process_id)  
        except Exception as e:
            print("exception : ",e)

        window = app.window(handle=w_handle)
        # Restore the window if it is minimized
        window.restore()
        window.maximize()
        window.set_focus()
        
        """# Ir al centro de la pantalla y hacer clic derecho
        mouse.move(int(ps[0]/4),int(ps[1]/2))
        time.sleep(5)
        send_keys('^d')
        time.sleep(20)
        # ALT+F4 cierra ventana 
        send_keys('%{F4}')
        time.sleep(5)
        app.kill()"""
        # Click en el elemento último : Informes.7z
        pyautogui.click(x,y)
        time.sleep(5)
        # Elimina elemento
        send_keys('^d')
        time.sleep(2)
        # Genera nueva busqueda en el cuadro Search , para los Anexos
        send_keys('^f')
        curym = dates_app['ymes']
        search_field=f'ANEXO*{curym}'
        time.sleep(3)
        pyautogui.typewrite(search_field,interval=0.3)
        time.sleep(5)
        # Click en Elemento central
        print(f"click archivo {int(ps[0]/2)},{int(ps[1]/2)}")
        pyautogui.click(int(ps[0]/2),int(ps[1]/2))
        time.sleep(3)
        # Selecciona todos los resultadosCTRL+A
        send_keys('^a')
        time.sleep(10)
        # Elimina todos los elementos Anexos
        send_keys('^d')
        time.sleep(15)
        # ALT+F4 cierra ventana 
        send_keys('%{F4}')
        time.sleep(2)
        # Elimina Proceso Ventana Citrix
        app.kill()
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise
    
