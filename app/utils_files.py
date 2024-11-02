import os
import sqlite3
import difflib
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import sys
from config.config import *
from app.get_data_doc import *
from app.api_redmine import creacion_ticket,connect_redmine
from app.files_mod_datetime import zona_incidencia
from loggerObj import logger
from app.incidenciasToExcel import inctoExc



def savedb_filesnames(folder, list_anexos):
    try:
        # Lee los archivos pegados desde citrix, guarda en BD SQLite aquellos archivos nuevos los ya procesados se eliminan
        # Solo quedan disponibles archivos que se van a procesar
        conn= sqlite3.connect('files_saved.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS files (name text)''')
        found_files = []
        for filename in os.listdir(folder):
            if filename.endswith('.doc'):
                filename_nodate=filename[:-12]
                match_found= False
                print(f"ANEXO: {filename_nodate}")
                for tup in list_anexos:
                    if (filename_nodate in tup[0]) or (filename_nodate in tup[1]):
                        match_found = True
                        c.execute("SELECT name FROM files WHERE name=?",(filename_nodate,))
                        result = c.fetchone()
                        if result:
                            # Elimina si nombre de archivo ya existe en base de datos
                            print(f"Eliminando ya existente: {filename_nodate}")
                            os.remove(os.path.join(folder, filename))
                        else:
                            print(f"Almacenando: {filename[:-4]}")
                            found_files.append(filename[:-4])
                            c.execute("INSERT INTO files (name) VALUES (?)", (filename_nodate,))
                            conn.commit()
                        break
                if not match_found:
                    print(f"Eliminando registro incompleto: {filename_nodate}")
                    os.remove(os.path.join(folder, filename))
        conn.close()
        return found_files
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def get_filesmatch(folder):
    try:
        # Genera listado de tuples de Anexos correspondientes B y C
        filenames_match=[]
        for filename in os.listdir(folder):
            if filename.endswith('.doc'):
                basename = os.path.splitext(filename)[0]
                basename2 = basename[6:]
                for other_filename in os.listdir(folder):
                    if other_filename== filename or not other_filename.endswith('.doc'):
                        continue
                    other_basename = os.path.splitext(other_filename)[0]
                    other_basename2 = other_basename[6:]
                    ratio = difflib.SequenceMatcher(None, basename2[:-8], other_basename2[:-8]).ratio()
                    if ratio==1 and basename[:6]=='ANEXOB':
                        #print(f"files: {basename} & {other_basename} ratio: {ratio*100}")
                        filenames_match.append(tuple((basename,other_basename)))
        return filenames_match
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def match_list_files(list_match):
    try:
        # Genera listado de tuples de Anexos correspondientes B y C
        filenames_match=[]
        for filename in list_match:  
            basename = os.path.splitext(filename)[0]
            basename2 = basename[6:]
            for other_filename in list_match:
                if other_filename== filename:
                    continue
                other_basename = os.path.splitext(other_filename)[0]
                other_basename2 = other_basename[6:]
                ratio = difflib.SequenceMatcher(None, basename2, other_basename2).ratio()
                if ratio==1 and basename[:6]=='ANEXOB':
                    #print(f"files: {basename} & {other_basename} ratio: {ratio*100}")
                    filenames_match.append(tuple((basename,other_basename)))
        return filenames_match
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


def db_trazabilidad(listissues):
    try:
        conn= sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS trazabilidad (incidencia CHAR,
        start_date TEXT, due_date TEXT, estado TEXT, excepcion TEXT, tipo_causa TEXT,
        fecha_incidencia TEXT, zona TEXT, causa TEXT, cnt_anexos TEXT,
            assigned_to TEXT, uploads TEXT)""")
        
        for issue in listissues:
            c.execute("""INSERT INTO trazabilidad (incidencia, start_date, due_date,
            estado, excepcion, tipo_causa, fecha_incidencia, zona, causa, cnt_anexos, assigned_to,
            uploads) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",(issue['incidencia'],issue['start_date'],issue['due_date'],
                                                        issue['estado'],issue['excepcion'],issue['tipo_causa'],issue['fecha_incidencia'],
                                                        issue['zona'],issue['causa'],issue['cnt_anexo'],issue['assigned_to'],
                                                        str(issue['uploads']),))
            conn.commit()
        conn.close()
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def set_new_date(actual_date):
    new_date = actual_date + relativedelta(day=15, months=1)
    return new_date

def files_processing(dfExcel):
    try:
        folder_path = f'{DIR_PATH}/ANEXOS_TEMP'

        # crea parejas de anexos en folder local
        filenames_match = get_filesmatch(folder_path)

        # Se general listado con anexos a procesar
        filenames_match = savedb_filesnames(folder_path,filenames_match)

        # se toma la lista y se procesa en parejas
        filenames_match = match_list_files(filenames_match)
        

        #print("files match: ",filenames_match)
        print(f"Tickets a procesar: {len(filenames_match)}")
        # Abre Conexion Redmine
        obj_redmine = connect_redmine()
        # Lectura de parejas de anexos
        ticket_creado=[]
        inc_no_proc =[]
        for filetuple in filenames_match:
            time.sleep(0.2)
            anexob = os.path.join(f'{folder_path}', filetuple[0]+".doc")
            anexoc = os.path.join(f'{folder_path}', filetuple[1]+".doc")
            issue={}
            print(filetuple[0])
            time.sleep(0.2)
            fecha_inc,desc= read_anexoC(anexoc)
            time.sleep(0.3)
            tipoCausa,causa,zonaAmbito,zonaAnalista = getTipoCausa(anexob,dfExcel)
            if tipoCausa !="":
                print(f"Tipo de Causa : {tipoCausa} - Causa: {causa} - Zona: {zonaAmbito} - Analista : {zonaAnalista}")

                time.sleep(0.3)
                anexos, cnt_anexos=checklists(tipoCausa,causa)
                # Obtener Numero de Incidencia
                issue['incidencia'] = filetuple[0][6:-8]
                # fecha en que se crea el ticket
                issue['start_date'] = datetime.strftime(datetime.now(), '%Y-%m-%d')
                # fecha de finalizacion de ticket
                dtime=set_new_date(datetime.now())
                issue['due_date'] = datetime.strftime(dtime, '%Y-%m-%d')
                # Para cada Anexo B. leer caso
                issue['tipo_causa'] = tipoCausa #CASO FORTUITO / FUERZA MAYOR
                # causa
                issue['causa'] = causa # LAS DE REDMINE
                # zona de incidencia
                issue['zona'] = zonaAmbito
                # para cada Anexo C leer todos los parametros necesario

                # descripcion incidencia
                issue['descripcion'] =f"""
                Tipo de Causa: {causa} 
                Descripción: {desc}"""

                # fecha de incidencia
                dton=datetime.strptime(fecha_inc,"%d/%m/%Y %H:%M:%S")
                dton = datetime.strftime(dton,"%Y-%m-%d")
                issue['fecha_incidencia']=dton
                # cnt anexos requeridos
                issue['cnt_anexo'] =cnt_anexos
                # asignado a id, parametrizado:
                #issue['assigned_to'] = assig_to
                issue['assigned_to'] =zonaAnalista
                # checklists anexo
                issue['checklist']=anexos
                # Uploads anexo
                issue['uploads'] = [{'path':anexob,'filename':filetuple[0]+".doc",'content_type':'application/msword'},
                {'path':anexoc,'filename':filetuple[1]+".doc",'content_type':'application/msword'}]
                
                try:
                    print("ticket : ", issue['incidencia'])
                    
                    time.sleep(1)
                    tq = creacion_ticket(obj_redmine,issue)
                   
                    print("response redmine : ", tq)
                    issue['estado'] = "Creado"
                    issue['excepcion'] = "Ninguna"
                    
                    print(f"--ZONA DETECCION: {issue['zona']}")
                    print("-------------------")
                    ticket_creado.append(issue)
                    os.remove(os.path.join(folder_path, anexob))
                    os.remove(os.path.join(folder_path, anexoc))
                    
                except Exception as e:
                    issue['estado'] = "Excepcion"
                    issue['excepcion'] = e
                    ticket_creado.append(issue)
                    print(f"Una excepcion ha ocurrido al crear el ticket : {e}")
                    pass
            else:
                #Se obtiene el num ticket de anexobfilepath
                anexob
                basename = os.path.splitext(anexob)[0]
                # Find the index of "ANEXOB" in the string
                start_index = basename.index("ANEXOB") + len("ANEXOB")

                # Extract the substring starting from the index after "ANEXOB"
                substring = basename[start_index:start_index + 6]
                with open('INCIDENCIAS_NO_PROCESADAS.txt', 'w') as ex:
                    ex.write(f"{substring}\n")
                logger.error(f"Incidencia NO PROCESADA - NO ENCONTRADA EN INFORME: #{substring}")
                inc_no_proc.append({'Incidencia':substring,'Causal':"Incidencia NO PROCESADA - NO ENCONTRADA EN INFORME"})
                print(f"SIn Row en Dataframe encontrado, Issue:", substring)
                continue
        
        try:
            db_trazabilidad(ticket_creado)
            
            print("Creado Trazabilidad DB -- Enviando Email")
        except Exception as e:
            print("Exception Almacenando en DB: ",e)
            pass

        """with open(f"tickets_creados_{dates_app['ymes']}.txt", "a") as fle:
            for item in ticket_creado:
                fle.write(f"{item}\n")"""
        inctoExc(ticket_creado,"GESTIONADAS")
        inctoExc(inc_no_proc,"NO_GESTIONADAS")
        print("________________________________")

    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise