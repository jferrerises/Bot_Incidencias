import os
import sqlite3
import difflib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time,json
import sys
from config.config import *
from app.api_redmine import creacion_ticket,connect_redmine
from app.files_mod_datetime import zona_incidencia
from loggerObj import logger
from app.incidenciasToExcel import inctoExc
import pytz

colombia_timezone = pytz.timezone('America/Bogota')


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
            estado, excepcion, tipo_causa,descripcion, fecha_incidencia, zona, causa, cnt_anexos, assigned_to,
            uploads) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",(issue['incidencia'],issue['start_date'],issue['due_date'],
                                                        issue['estado'],issue['excepcion'],issue['tipo_causa'],issue['descripcion'],issue['fecha_incidencia'],
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
    new_date = actual_date + relativedelta(day=5, months=1)
    return new_date

##--NUEVAS FUNCIONES --###

##---NUEVA DB --##
def checkDB(incidencia):
    try:
        conn= sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS trazabilidad (incidencia CHAR,
        start_date TEXT, due_date TEXT, estado TEXT, excepcion TEXT, tipo_causa TEXT,
        fecha_incidencia TEXT, zona TEXT, causa TEXT, cnt_anexos TEXT,
            assigned_to TEXT, uploads TEXT)""")
        
       
        c.execute("""SELECT incidencia FROM trazabilidad WHERE incidencia = ?""",(incidencia,))
        result = c.fetchall()
        
        return result
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise


## Get Tickets ultimos dias
def getTickets(redmine):
    hoy = datetime.now()
    mes = hoy - timedelta(days=40)
    crear = None
    lstStatus=[7]
    lstItems=[]
    for lst in lstStatus:
        filterInc = redmine.issue.filter(
            project_id=5,
            status_id =lst, #7 asugnada , 2 en curso , 3 resuelta
            created_on=f'><{mes.strftime("%Y-%m-%d")}|{hoy.strftime("%Y-%m-%d")}'
        )
        lstItems.append(filterInc)
    
    return lstItems

## Fecha de Finalizacion
def set_new_date(actual_date, incidencia_date, start_date):
    due_date = None
    # Check if incidencia_date is from the previous month
    if incidencia_date.month == (actual_date.month - 1) % 12:
        if actual_date.day <= 5:
            due_date = actual_date.replace(day=5)
        
        if actual_date.day > 5:
            due_date = start_date = actual_date.replace(day=5)
    elif incidencia_date.month == actual_date.month:
        
        due_date = actual_date + relativedelta(day=5, months=1)
    return due_date,start_date
    

##Se obtienen parámetros del DF
def getParams(incidencia,dfExcel):
    #fecha_inc,desc, tipoCausa,causa,zonaAmbito,zonaAnalista
    dictParams={}
    
    df = dfExcel[dfExcel['Incidencia']==int(incidencia)]

    if not df.empty:
        index = dfExcel[dfExcel['Incidencia']==int(incidencia)].index
        print("df encontrado :", df.head())
        
        #Obtencion tipo de causa
        dictParams['tipoCausa'] = dfExcel.loc[index[0],'Tipo de Causa']
        #Obtención de descripcion
        dictParams['desc'] =  dfExcel.loc[index[0],'Descripción']
        #Obtención de fecha de Incidencia
        dictParams['fecha_inc'] = dfExcel.loc[index[0],'Fecha Detección']

        # Obtencion de causa
        with open(f'{DIR_PATH}/app/tipo_causaNuevo.json', "r",encoding='utf-8') as file_tc:
            data_tc = file_tc.read()
        dit_tc = json.loads(data_tc)
        
        causaDf = dfExcel.loc[index[0],'Causa']
        for key, value in dit_tc[dictParams['tipoCausa'].lower()].items():
            if causaDf in value:
                dictParams['causa'] = key
                break
            else:
                dictParams['causa'] = 'Otros'
        
        # Obtencion de zona
        ambito= dfExcel.loc[index[0],'Zona']
        print("zona ambito excel:", ambito)
        #with open(f'{DIR_PATH}/app/ambitoyanalistas.json', "r",encoding='utf-8') as file_ambito: -- #oRIGINAL
        with open(f'{DIR_PATH}/app/ambitoyanalistas_central_azuero.json', "r",encoding='utf-8') as file_ambito:
            dic_ambito = file_ambito.read()
        jsonAmbito = json.loads(dic_ambito)
        
        for key, value in jsonAmbito.items():
            if ambito in value['ambito']:
                dictParams['zona'] = key
                break
        
        # Obtencion Analista
        print("zona redmine: ",dictParams['zona'])
        zonaAnalista =dictParams['zona']
        dictParams['analista'] = jsonAmbito[zonaAnalista]['id_redmine']
        
        return dictParams


def checklists(tc,causal):
    # Abre json de tipos de causa kw
    with open(f'{DIR_PATH}/app/tipo_causa.json', "r",encoding='utf-8') as file_tcc:
        data_tcc = file_tcc.read()
    dit_tcc = json.loads(data_tcc)
    anexos=[]
    counter =0
    for x in dit_tcc[tc].items():
        if x[0]==causal:
            for y in x[1].items():
                for a in y[1]:
                    anx={"subject":"({}) {}".format(y[0],a),
                        "is_done":False}
                    if "OBLIGATORIO" in anx['subject']:
                        counter+=1   
                    anexos.append(anx)
    return anexos, len(anexos),counter

def files_processing(dfExcel):
    try:
        # Abre Conexion Redmine
        obj_redmine = connect_redmine()
        lstItems=getTickets(obj_redmine)
        delete_indices=[]
        # Se general listado con anexos a procesar
        for index,element in enumerate(dfExcel['Incidencia']):
            print("Elemento : ", element)
            result = checkDB(element)
            time.sleep(0.3)
            if len(result)>=1:
                delete_indices.append(index)

        newDF = dfExcel.drop(delete_indices)
        print(f"newDF: {newDF.head()}")
        print(f"Tickets a procesar: {len(newDF['Incidencia'])}")
        
        # Lectura de parejas de anexos
        ticket_creado=[]
        inc_no_proc =[]
        for index, row in newDF.iterrows():
            issue={}
            #fecha_inc,desc= read_anexoC(anexoc)
            time.sleep(1)
            #tipoCausa,causa,zonaAmbito,zonaAnalista = getTipoCausa(anexob,dfExcel)
            dictParams = getParams(row['Incidencia'],newDF)
            print("dictParams :", dictParams)
            if dictParams['tipoCausa'] !="":

                time.sleep(0.5)
                anexos, cnt_anexos, cnt_obligatorios=checklists(dictParams['tipoCausa'],dictParams['causa'])
                
                # Obtener Numero de Incidencia
                issue['incidencia'] = row['Incidencia']
                # fecha de incidencia
                
                if not isinstance(dictParams['fecha_inc'], datetime):
                    dton=datetime.strptime(dictParams['fecha_inc'],"%d/%m/%Y %H:%M:%S")
                    
                else:
                    dton = dictParams['fecha_inc']
                dton = datetime.strftime(dton,"%Y-%m-%d")
                issue['fecha_incidencia']=dton
                # Parametros set_new_date: [Fecha actual], [Fecha de incidencia], [Fecha de Inicio - Redmine]
                #Return : [Fecha finalizacion - Redmine , Fecha Inicio - Redmine]
                due_date,start_date = set_new_date(colombia_timezone.localize(datetime.now()), datetime.strptime(dton,"%Y-%m-%d"), 
                                                   colombia_timezone.localize(datetime.now()))
                
                # fecha en que se crea el ticket
                #issue['start_date'] = datetime.strftime(datetime.now(), '%Y-%m-%d')
                issue['start_date'] = datetime.strftime(start_date, '%Y-%m-%d')
                # fecha de finalizacion de ticket
                #dtime=set_new_date(datetime.now())
                #issue['due_date'] = datetime.strftime(dtime, '%Y-%m-%d')
                issue['due_date'] = datetime.strftime(due_date, '%Y-%m-%d')
                
                # Para cada Anexo B. leer caso
                issue['tipo_causa'] = dictParams['tipoCausa'] #CASO FORTUITO / FUERZA MAYOR
                # causa
                issue['causa'] = dictParams['causa'] # LAS DE REDMINE
                # zona de incidencia
                issue['zona'] = dictParams['zona']
                # para cada Anexo C leer todos los parametros necesario

                # descripcion incidencia
                issue['descripcion'] =f"""
                Tipo de Causa: {dictParams['causa']} 
                Descripción: {dictParams['desc']}"""

                # fecha de incidencia
                """dton=datetime.strptime(dictParams['fecha_inc'],"%d/%m/%Y %H:%M:%S")
                dton = datetime.strftime(dton,"%Y-%m-%d")
                issue['fecha_incidencia']=dton"""
                #cnt_anexos obligatorios
                issue['cnt_anexos_obligatorio'] = cnt_obligatorios
                # cnt anexos requeridos
                issue['cnt_anexo'] =cnt_anexos
                # asignado a id, parametrizado:
                #issue['assigned_to'] = assig_to
                issue['assigned_to'] =dictParams['analista']
                # checklists anexo
                issue['checklist']=anexos
                # Uploads anexo
                issue['uploads']=[]
                """issue['uploads'] = [{'path':anexob,'filename':filetuple[0]+".doc",'content_type':'application/msword'},
                {'path':anexoc,'filename':filetuple[1]+".doc",'content_type':'application/msword'}]"""
                
                try:
                    
                    issue['estado'] = "Creado"
                    issue['excepcion'] = "Ninguna"
                    
                    tq = creacion_ticket(obj_redmine,issue,lstItems)
                    print("ticket : ", issue['incidencia'])
                    
                    
                    if tq.status_code==200:
                        print("response redmine : ", tq)
                        ticket_creado.append(issue)
                    print("-------------------")

                    
                except Exception as e:
                    """issue['estado'] = "Excepcion"
                    issue['excepcion'] = e
                    ticket_creado.append(issue)"""
                    inc_no_proc.append({'Incidencia':row['Incidencia'],'Causal':f"Excepcion en Creación Ticket - {e}"})
                    print(f"Excepcion ha ocurrido al crear el ticket : {e}")
                    pass
                time.sleep(3)
            else:
                """with open('INCIDENCIAS_NO_PROCESADAS.txt', 'w') as ex:
                    ex.write(f"{row['Incidencia']}\n")"""
                logger.error(f"Incidencia NO PROCESADA - NO ENCONTRADA EN INFORME: #{row['Incidencia']}")
                inc_no_proc.append({'Incidencia':row['Incidencia'],'Causal':"Incidencia NO PROCESADA - NO ENCONTRADA EN INFORME"})
                print(f"SIn Row en Dataframe encontrado, Issue:", row['Incidencia'])
                continue
            
        try:
            db_trazabilidad(ticket_creado)
            
            print("Creado Trazabilidad DB -- Enviando Email")
        except Exception as e:
            print("Exception Almacenando en DB: ",e)
            pass

        
        inctoExc(ticket_creado,"GESTIONADAS")
        inctoExc(inc_no_proc,"NO_GESTIONADAS")
        print('________________________________')

    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise