import pyautogui
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import keyboard
from loggerObj import logger
import sys
from config.config import *



def login():
    try:
        # Abre el explorador Chrome y permite el login en la página del extranet
        # Una vez verificado el acceso permite ingresar a la ventana de los accesos a citrix y alchemy
        print("login browser")
        # Se obtiene el tamaño real del monitor donde se ejecuta el script para futuro uso
        ps=pyautogui.size()
        monitors= get_monitors()
        mon_left = monitors['left']
        mon_top = monitors['top']
        mon_width = monitors['width']
        mon_height = monitors['height']
        chrome_options = Options()
        
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--lang=es')
        #chrome_options.add_argument(f'--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        time.sleep(5)
        driver.get("https://extranet.gasnaturalfenosa.com.pa")
        
        print("username_login_web1")
        try:
            elm = WebDriverWait(driver,50).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR,"div.card-body.title")
            ))
        except Exception as e:
            print("Exception : ",e)
        print(elm)
        print("ok")
        time.sleep(2)
        log_a=(int(ps[0]*0.36),int(ps[1]*0.43))
        """while True:
            print("wait_username")
            try:
                #log_a = pyautogui.locateCenterOnScreen(f"{DIR_PATH}/app/IMAGENES/username_login_webinicio.png")
                cls=driver.find_element(By.CSS_SELECTOR,"div.card-body.title")
                print("class :", cls)
                if log_a:
                    break
            except Exception as e:
                print("exce :", e)
                pass
            time.sleep(0.5)"""
        print("coordenadas : ", log_a)
        # clic paa ctivar la escritura en casilla
        """pyautogui.click(log_a[0],log_a[1])
        # escribir usuario
        print("escribir usuario")
        time.sleep(1)
        pyautogui.typewrite(login_cred['username'], interval=0.2)
        time.sleep(3)"""
        inp_username= driver.find_element(By.CSS_SELECTOR,'input[formcontrolname="username"]')
        inp_username.send_keys(login_cred['username'])
        # localiza boton de 'proximo' para avanzar con la verificación
        #log_prox = pyautogui.locateCenterOnScreen(f"{DIR_PATH}/app/IMAGENES/boton_login_webinicio.png")
        #pyautogui.click(log_prox[0],log_prox[1])
        time.sleep(1)
        """pyautogui.move(int(ps[0]*0.51),int(ps[1]*0.49))
        pyautogui.click()"""
        btn_prox = driver.find_element(By.CLASS_NAME,'nextBtn')
        time.sleep(0.5)
        btn_prox.click()
        print("proximo coord: ")

        # localiza boton de verificar
        log_ver=None
        print("verificar_login_web1")
        elm_verf=""
        try:
            elm_verf = WebDriverWait(driver,50).until(EC.presence_of_element_located(
                (By.CLASS_NAME,"verifyBtn")
            ))
        finally:
            elm_verf.click()
        """while True:
            print("verificar_boton")
            try:
                log_ver = pyautogui.locateCenterOnScreen(f"{DIR_PATH}/app/IMAGENES/verificar_boton.png")
                if log_ver:
                    break
            except:
                pass
            time.sleep(0.2)
        pyautogui.click(log_ver[0],log_ver[1])"""
        print("verif coord: ", log_ver)
        # esperar hasta encontrar objeto en la pagina emergente
        # login web2
        time.sleep(10)
        wt2= WebDriverWait(driver,1000)
        elem2=wt2.until(EC.visibility_of_element_located((By.ID,'passwd')))
        
        print("elem2: ", elem2)
        time.sleep(10)
        elem2.send_keys(login_cred['passwd'])
        time.sleep(3)
        elem3=driver.find_element(By.ID, "Log_On").click()
        time.sleep(10)
        # localiza boton Detect receiver Citrix
        elem5= wt2.until(EC.visibility_of_element_located((By.ID,'protocolhandler-welcome-installButton')))
        print("elem5: ", elem5)
        elem5.click()
        
        # abrir enlace de detección
        ci_lnk=None
        print("ENLACE_RECEIVER")
        """while True:
            try:
                ci_lnk = pyautogui.locateCenterOnScreen(f"{DIR_PATH}/app/IMAGENES/abrir_citrix_workspace_launcher.png")
                if ci_lnk:
                    break
            except:
                pass
            time.sleep(0.5)"""
        time.sleep(1.5)
        keyboard.send('left')
        print("keyboard.send('left')")
        time.sleep(0.5)
        keyboard.send('enter')
        print("keyboard.send('enter')")
        #pyautogui.click(ci_lnk[0],ci_lnk[1])
        time.sleep(5)
        # objeto es el ícono de acceso a escritorio citrix  
        try:
            elem4= wt2.until(EC.visibility_of_element_located((By.CLASS_NAME,'storeapp-icon')))
        except Exception as e:
            raise e
        else:
            elem4.click()
            print("icono citrix escritorio clic")
            time.sleep(1.5)
            keyboard.send('left')
            time.sleep(0.5)
            keyboard.send('enter')
            """pyautogui.moveTo(ps[0]/2,ps[1]/2)
            time.sleep(5)
            # autorizar abrir enlace escritorio
            ci_lnk2 = pyautogui.locateCenterOnScreen(f"{DIR_PATH}/app/IMAGENES/abrir_citrix_workspace_launcher.png")
            pyautogui.click(ci_lnk2[0],ci_lnk2[1],clicks=2)
            print("link de escritorio citrix abierto")"""
            #Aquí queda abierto hasta que cargue la aplicación de escritorio
            pyautogui.moveTo((mon_left+(mon_width/2)),mon_height/2)
        return mon_left,mon_top,mon_width,mon_height
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise