# coding: utf-8

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from config.config import *

#Para evitar el error por SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from redminelib import Redmine
from datetime import datetime, timedelta
import json, time
from unidecode import unidecode
import pandas as pd

def connect_redmine():
    headers={
        "X-Redmine-API-Key":API_KEY,
        "Content-Type": "application/json"
    }

    try:
        redmine = Redmine('https://35.84.21.122/redmine', key=API_KEY,requests={'verify': False,'headers':headers})
    except Exception as e:
        print(e)
    print(redmine)
    return redmine

def connect_middlewareNuevo(ticket_data):
    try:
        #Parametros de conexión a servidor
        url = 'https://incidencias.ises.com.co/ises/secure'
        #url = 'http://127.0.0.1:5000/ises/secure'
        jwt_token = str(ticket_data['tecnicoToken'])
        #jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJpb0B3aXNlbHl4LmNvbSIsImV4cCI6MTcwMDA2MjUwMX0.SrxoKUF815LuKZY1EmgAFiVqnQ1i-UhgDAGxN5icEco'

        headers = {
            'Authorization': f'{jwt_token}',
            'Content-Type': 'application/json'
        }
        ticket_data['checklist'] = json.dumps(ticket_data['checklist'])
        time.sleep(0.5)
        response = requests.post(url, headers=headers, json=ticket_data)
        time.sleep(0.5)
        print("response connect_middlewareNuevo:", response)
        return response
    except Exception as e:
        print(f"Exception  connect_middlewareNuevo {ticket_data['idissue']}: {e}")
        return None
        
    

def connect_middleware(ticket_data):
    #Parametros de conexión a servidor
    url = 'http://135.148.4.98/ises/secure'
    #url = 'http://127.0.0.1:5000/ises/secure'
    jwt_token = str(ticket_data['tecnicoToken'])
    #jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJpb0B3aXNlbHl4LmNvbSIsImV4cCI6MTcwMDA2MjUwMX0.SrxoKUF815LuKZY1EmgAFiVqnQ1i-UhgDAGxN5icEco'

    headers = {
        'Authorization': f'{jwt_token}',
        'Content-Type': 'application/json'
    }
    ticket_data['checklist'] = json.dumps(ticket_data['checklist'])
    time.sleep(0.5)
    response = requests.post(url, headers=headers, json=ticket_data)
    time.sleep(0.5)
    print("response :", response)
    return response


def getChecklist(idissue):
    checklistData=None
    #URL https://35.84.21.122/redmine/issues/42718/checklists.json
    headers={
    "X-Redmine-API-Key":API_KEY,
    "Content-Type": "application/json"
}
    try:
        # Endpoint URL
        url = f"https://35.84.21.122/redmine/issues/{idissue}/checklists.json"
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            checklist = response.json()
            checklistData=checklist['checklists']
            
    except Exception as e:
        print("Escepcion al obtener checklist")
    
    return checklistData



    
def checkDup(lstItems,incidencia):
    crear = None
    for issue in lstItems:
        print(issue)
    
        filtered_issues = [elem for elem in issue if incidencia in elem.subject]
        print("filtered_issues :", filtered_issues)
        if len(filtered_issues)==0:
            crear = True
            
        else:
            crear = False
            break
        
    return crear

def creacion_ticket(redmine,ticket_data,lstItems):
    print(f"Creando Incidencia {ticket_data['incidencia']}")
    #filtra incidencias por numero de incidencia en subject
    
    crearTicket = checkDup(lstItems,str(ticket_data['incidencia']))
    print(f"Respuesta filtrado {str(ticket_data['incidencia'])} - {crearTicket}")
    if crearTicket:
        # Crear un nuevo issue
        # Importante en el campo uploads colocar el filename , el path es la ruta donde esta el archivo en el pc local
        issue_new = redmine.issue.create(
            project_id=5, # Por Defecto, es el id del proyecto
            subject=f"Incidencia: {ticket_data['incidencia']} {ticket_data['zona']} | Fecha : {ticket_data['fecha_incidencia']}", #XXX= Numero de incidencia - Fecha Incidencia
            tracker_id=16, #Por defecto , un tracker referente al proyecto
            description=ticket_data['descripcion'], # Descripcion de la incidencia segun Anexo C item 8
            status_id=7, # Estados. 7: Asignado, 6:Rechazada, 1: Nueva
            priority_id=2,#Prioridad. 2:Normal,1: Baja, 3: Alta, 4: Urgente, 5: Inmediata
            assigned_to_id=ticket_data['assigned_to'],# asignado a. 204: Angie Castillo, 32: Jose Vargas, 363: Mario Gutierres
            watcher_user_ids=[ticket_data['assigned_to'],363], #id de usuarios que tienen acceso al issue
            start_date=ticket_data['start_date'], #Fecha actual en que se crea el ticket
            due_date=ticket_data['due_date'],# Fecha actual en que se crea el ticket
            estimated_hours=0.5, # horas estimadas 30min
            done_ratio=0,# porcentaje realizado
            custom_fields=[
                {'id':21,'value':ticket_data['fecha_incidencia']}, #fecha de incidencia reportada en anexo
                {'id':15,'value':ticket_data['zona']}, #zona de incidencia
                {'id':17,'value':ticket_data['tipo_causa']}, #Tipo de Causa. Viene de Anexo B
                {'id':16,'value':ticket_data['causa']}, #Causa. Se determina interpretando item Anexo C #9
                {'id':20,'value':0},
                {'id':42,'value':ticket_data['cnt_anexos_obligatorio']},                
                {'id':19,'value':ticket_data['cnt_anexo']} # Num de anexos obligatorios. Obtenido de len(tipo_causa.json[obligatorio])
            ],
            checklists=ticket_data['checklist']
            #uploads=ticket_data['uploads']
            
            
        )

        isn=f"Incidencia : {ticket_data['incidencia']} Creada | Id Issue: {issue_new.id}"
        print(isn)
        
        ## Nuevo módulo de asignación de solicitudes a técnicos
        if issue_new['id'] is not None:
            try:
                ticket_data['idissue'] = issue_new['id']
                
                #obtiene llave de tecnico y zona de tecnicosZonas.json
                with open(f'{DIR_PATH}/app/tecnicosZonas.json','r') as filetecnicos:
                    tecnicos = json.load(filetecnicos)
                    
                print("Json tenicos zona obtenido")
                tcn = unidecode(ticket_data['zona']).lower()
                ticket_data['tecnico'] = tecnicos[tcn]['email']
                print("TEcnico:",ticket_data['tecnico'])
                ticket_data['tecnicoToken'] = tecnicos[tcn]['token']
                #Obtiene checklist con id
                ticket_data['checklist']=getChecklist(issue_new['id'])
                time.sleep(1)
                
                #remover Key : cnt_anexos_obligatorio
                del ticket_data['cnt_anexos_obligatorio']
                #TODO: Anexar llave : cnt_anexos_obligatorio a servidor middleware
                # Envia datos de ticket a servidor Middleware
                response = connect_middleware(ticket_data)
                time.sleep(3)
                connect_middlewareNuevo(ticket_data)
                time.sleep(6)
            
                return response
            except Exception as e:
                print("excepcion al procesar nueva asignatión de ticket a tecnico")
                pass
        else:
            return issue_new.id
    else:
        return False




def checkIncidenciaRedmine(excel_data):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_day = datetime.now().day
    #excel_data = pd.read_excel(excel_file)
    incidencias_set = set(excel_data['Incidencia'])
    redmine = connect_redmine()
    delete_indices = []
    filtered_issues = redmine.issue.filter(project_id=5, created_on='><%d-%02d-01|%d-%02d-%02d' % (current_year, current_month, current_year, current_month,current_day))
    print("len filter :", len(filtered_issues))
    for issue in filtered_issues:        
        for incidencia in incidencias_set:
            if str(incidencia) in issue.subject:
                row = excel_data[excel_data['Incidencia']==incidencia]
                index=row.index
                print("Issue encontrado :", incidencia)
                print("Issue ID:", issue.id)
                print("Subject:", issue.subject)
                delete_indices.append(index[0])
                print("-" * 30)
    print("INDICES ELIMINADOS :", delete_indices)
    newDF = excel_data.drop(delete_indices)
    #newDF.to_excel(excel_file, index=False)
    return newDF