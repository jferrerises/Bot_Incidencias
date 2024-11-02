
#
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pprint
from config.redmine_connect import redmine_object
import os
import xlrd
from loggerObj import logger
import sys,time
from config.config import zonas_oldnew
pp = pprint.PrettyPrinter(indent=4)
import configparser


config_file = 'config.ini'
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file)
#root_folder=r'D:\\SHAREPOINT_ISES\\ISES S.A.S\\Servicios de Catálogo - 3. Desarrollo y Mantenimiento\\Automatizacion generacion de Incidencias\\'
root_folder=r'D:\\ises-dds\\APLICACIONES_ISES\\Incidencias_CF_FM\\filtro\\'

#root_folder=r'C:\\Users\\gutie\\OneDrive\\Documentos\\PROYECTOS_ISES\\Incidencias_CF_FM\\filtro\\'
redmine=redmine_object()

def get_issues_redmine():
    try:
        # Se establece el 01 de Marzo de 2023 como la fecha inicial de creación de incidencias en Redmine, y es 
        # la fecha de inicio del rango de búsqueda.
        fecha1=datetime.now().strftime("2023-10-01")
        fecha2=datetime.now().strftime("%Y-%m-%d")
        issues= redmine.issue.filter(
            project_id='5',
            created_on=f'><{fecha1}|{fecha2}')
        df = pd.DataFrame(columns=['incidencia'])
        l=[]
        for f in issues:
            issue_id=getattr(f,'subject')
            l.append(issue_id[-6:])
        df['incidencia']=l
        return df
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
    

def get_df_excel():
    try:
        
        book = xlrd.open_workbook(filename=os.path.join(root_folder,f"{config.get('AppConfig', 'folder_carga_informe')}\\INFORME.xls"))

        df= pd.read_excel(book)
        print("DF : ", df.head())
        df.dropna()
        # Filtrado por zonas diferentes a todos
        df=df.loc[df['Ámbito']!="<Todos>"]
        # Filtrado por tipo de causa
        df=df.loc[df['Tipo de Causa']!="OTRA CAUSA"]
        #Filtrado por Estado Actual
        df=df.loc[df['Estado Actual']=="Resuelta"]
        #Filtrado por Duracion RS
        df = df.fillna(0)
        df=df.loc[df['Duración RS'].astype(int)>3]
        print("DF : ", df.head())
        return df
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def checkdb():
    listdata=[]
    conn= sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
    c = conn.cursor()
    c.execute("select incidencia from trazabilidad")
    result = c.fetchall()
    if len(result)>0:
        for r in result:
            listdata.append(r[0])
    c.close()
    conn.close()
    df = pd.DataFrame(columns=['incidencia'])
    df['incidencia']=listdata
    df = df.drop_duplicates(subset=['incidencia'], keep='first')
    return df
        

def filter_report():
    try:
        #Se crea un datagrama df2 para comparar Incidencias guardadas vs las Nuevas
        df2 = checkdb()
        df2.applymap(str)
        ## Filtrado de las incidencias pertenecientes al INFORME de OpenSGI
        df1 = get_df_excel()
        circuitos = os.path.join(root_folder,"circuitos.xlsx")
        print("path ciruitos:", circuitos)
        circuitos = pd.read_excel(circuitos)
        #circuitos = pd.read_excel(r"D:\\ises-dds\\APLICACIONES_ISES\\Incidencias_CF_FM\\filtro\\circuitos.xlsx")
        df1['Incidencia']=df1['Incidencia'].astype(str)

        # Merge the dataframes on the 'a1' and 'b' columns
        merged_df = pd.merge(df1, df2, left_on='Incidencia', right_on='incidencia', how='left')

        # Filter the rows where df2['b'] is NaN (not present in df2)
        results = merged_df[merged_df['incidencia'].isnull()].drop(columns='incidencia')

        # Si ambito es COCLE VER - HERRERA L.S. , revisar que pertenezca a una u otra zona de acuerdo a circuitos.xls
        # Check if 'Ámbito' is 'COCLE VER - HERRERA L.S.'
        
        for index,row in results.iterrows():
            if row['Ámbito'] == 'COCLE VER - HERRERA L.S.':
               
                substring_found = False

                # Iterate through 'CIRCUITO' values in 'circuitos' DataFrame
                for circuito in circuitos['CIRCUITO']:
                
                    if circuito in row['Instalación']:
                        substring_found = True
                        break  # Exit the loop if the substring is found
                    
                # Update the 'Zona' column based on the flag
                results.loc[index, 'Zona'] = circuitos.loc[circuitos['CIRCUITO'] == circuito, 'ZONA'].values[0] if substring_found else 'AZUERO'
            else:
                results.loc[index, 'Zona'] = row['Ámbito']

        results.sort_values(by='Fecha Detección')

        #revisa esas incidencias si ya han sido guardadas por error en la db
       
        hr = datetime.now().strftime("%Y%m%d_%H%M")
        
        fl=os.path.join(root_folder,f"{config.get('AppConfig','folder_reportes')}\\INCIDENCIAS_NUEVAS_GESTIONAR_{hr}.xlsx")
        #fl=os.path.join(root_folder,f"INCIDENCIAS_NUEVAS_GESTIONAR_{hr}.xlsx")
        # Save the results to an Excel file
        results.to_excel(fl, index=False)
        return fl
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise

def run_filtro():
    try:
        path_file=filter_report()
        print("Path_file : ", path_file)
        # convert dates to datetime objects
        ddf = pd.read_excel(path_file)
        if 'Zona' in ddf.columns:
            zonas_dates={}
            #Se cambia Ambito por ZOna para incluir Central y Azuero
            uniques_zonas = ddf['Zona'].unique()
            for zona in uniques_zonas:
                df_zona = ddf.loc[ddf['Zona']==zona]
            
                df_zona['Fecha Detección'] = pd.to_datetime(df_zona['Fecha Detección'], format='%d/%m/%Y %H:%M:%S')
                df_zona = df_zona.sort_values(['Fecha Detección'], ascending=True)
                ldates = df_zona['Fecha Detección'].to_list()
                dates = [date for date in ldates]
                start_date = min(dates)
                end_date = min(dates)
                date_ranges = []

                # loop through list of dates
                for date in dates[1:]:
                    # check if the current date is at least 3 days later than the end date of the previous range
                    if date >= end_date + timedelta(days=3):
                        # if so, add the previous date range to the list of date ranges
                        date_ranges.append((start_date, end_date))
                        # set the start date of the new range to the current date
                        start_date = date
                    # set the end date of the current range to the current date
                    end_date = date

                # add the last date range to the list of date ranges
                date_ranges.append((start_date, end_date))
                zonas_dates[zona]=[]
                # print the date ranges
                for i, date_range in enumerate(date_ranges):
                    date1 = datetime.strftime(date_range[0], "%d/%m/%Y")
                    date2 = datetime.strftime(date_range[1], "%d/%m/%Y")
                    zonas_dates[zona].append(tuple((date1,date2)))
            
            #pp.pprint(zonas_dates)
            zonas= {}
            for old_name, values in zonas_dates.items():
                nnm = zonas_oldnew[old_name]
                zonas[nnm] = values
            order=['Oeste','Metro','Central','Azuero','Chiriquí']
            sorted_dict = {order[i]:zonas[order[i]] for i in range(len(order)) if order[i] in zonas}
            logger.info("Diccionario de incidencias creado")
            return sorted_dict,path_file
        else:
            print("Columna ZOna no existe, Datagrama vacío o error.")
            time.sleep(5)
            sys.exit()
            
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise