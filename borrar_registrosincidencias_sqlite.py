import sqlite3
import pandas as pd
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from redminelib import Redmine
from datetime import datetime
from config.config import *
import time

def findinlistdelete():
    # Connect to the SQLite database
    conn = sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
    cursor = conn.cursor()
    # Specify the table name and the column for searching
    table_name = 'trazabilidad'
    search_column = 'incidencia'
    list_incidencias=['996094', '996019', '996167', '995702', '995758', '995694', '995656', '995838', '995752', '995405', '995733', 
                      '995796', '996081', '995983', '995414', '995781', '995158', '995804', '995325', '995756', '995139', '995790', 
                      '995399', '995753', '995657', '994856', '995169', '995779', '995959', '995260', '996038', '995783', '995658', 
                      '995772', '996082', '995654', '995891', '995685', '995296', '994855', '994836', '996074', '995982', '996149', 
                      '995745', '996075', '995679', '995978', '995145', '995980', '995160', '995334', '995331', '995827', '995810', 
                      '995689', '996165', '995841', '995795', '995766', '995856', '996021', '995302', '996012', '995931', '994879', 
                      '994829', '996042', '996062', '996040', '995965', '995544', '995153', '995703', '995839', '995774', '995697', 
                      '996008', '996018', '994499', '994818', '995771', '995879', '995375', '995680', '995651', '995731', '995882', 
                      '995526', '994822', '994541', '996146', '995368', '995709', '996052', '996025', '995961', '995968', '995941', 
                      '996006', '996136', '995990', '995659', '995916', '995845', '995895', '994863', '994531', '995829', '995919', 
                      '995812', '995822', '995724', '995945', '995692', '995897', '994522', '996017', '995887', '995896', '995792', 
                      '994529', '994508', '995505', '995901', '995004', '995430', '995280', '995527', '996137', '995276', '995323', 
                      '995878', '995308', '995306', '995784', '995682', '995431', '995669', '995283', '995948', '995429', '995665', 
                      '995298', '994888', '995881', '995877', '996023', '996139', '996104', '995393', '995824', '995351', '995940', 
                      '995290', '995650', '995911', '995926', '994821', '996129', '995832', '996153', '996027', '996020', '994834', 
                      '995820', '995854', '995797', '995630', '995927', '995751', '995967', '995855', '995681', '995846', '995853', 
                      '995010', '995345', '996068', '996046', '996093', '995438', '995972', '995986', '995828', '994841', '994848', 
                      '995750', '995768', '995801', '995155', '996100', '995718', '996064', '995930', '995711', '996110', '996107', 
                      '995999', '995164', '995900', '995676', '994842', '994826', '994824', '995427', '995921', '995826', '995126', 
                      '995992', '995950', '995722', '996134', '994993', '995151', '995791', '995809', '996150', '996002', '994536', 
                      '995957', '995741', '996031', '995717', '995012', '996055']

    for search_value in list_incidencias:
        # Check if the row exists
        cursor.execute(f"SELECT * FROM {table_name} WHERE {search_column} = ?", (search_value,))
        row = cursor.fetchone()
        print("row :", row)


        if row:
            print(f"Row with {search_column} = {search_value} found. Deleting...")

            # Delete the row
            cursor.execute(f"DELETE FROM {table_name} WHERE {search_column} = ?", (search_value,))
            
            # Commit the changes
            conn.commit()
            print("Row deleted successfully.")
        else:
            print(f"Row with {search_column} = {search_value} not found.")

        # Close the database connection
    conn.close()




def findduplicates(excel_file):
    # Read Excel file
    excel_data=None
    #excel_data = pd.read_excel(excel_file,sheet_name="Duplicadas")
    excel_data = pd.read_excel(excel_file)
    column_names = excel_data.columns.tolist()
    print("column_names :", column_names)
    print("excel_data :", excel_data.head())
    incidencias = excel_data['Incidencia'].tolist()
    # Connect to SQLite database
    conn = sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
    cursor = conn.cursor()
    existing_incidencias = []
    for incidencia in incidencias:
        cursor.execute("SELECT incidencia FROM trazabilidad WHERE incidencia = ?", (incidencia,))
        result = cursor.fetchone()
        if result:
            existing_incidencias.append(result[0])
    
    """placeholders = ','.join(['?'] * len(incidencias)) 
    # Find duplicates in the specified table and column
    cursor.execute(f"SELECT incidencia, COUNT(*) FROM trazabilidad WHERE incidencia IN ({placeholders}) GROUP BY incidencia HAVING COUNT(*) > 1", incidencias)

    duplicates = cursor.fetchall()"""
    # Close connection
    conn.close()
    return existing_incidencias

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


def delete_rows_from_excel(excel_file, existing_incidencias):
    try:
        # Read Excel file
        print("delete_rows_from_excel")
        excel_data = pd.read_excel(excel_file)
        for x in existing_incidencias:
            cond = str(excel_data['Incidencia']) == str(x)
            print("cond :", cond)
            if cond:
                excel_data = excel_data.drop(excel_data[cond].index)
            #excel_data = excel_data[cond]
                
            
        """# Delete rows where 'Incidencia' exists in existing_incidencias list
        modified_excel_data = excel_data[~excel_data['Incidencia'].isin(existing_incidencias)]
        print("modified_excel_data :", modified_excel_data.head())"""
        # Save modified Excel file with the same name
        print("excel modified : ", excel_data.head())
        excel_data.to_excel(excel_file, index=False)
    except Exception as e:
        print("Execption :", e)



def checkIncidenciaRedmine(excel_file):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_day = datetime.now().day
    excel_data = pd.read_excel(excel_file)
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
    newDF = excel_data.drop(delete_indices)
    newDF.to_excel(excel_file, index=False)
    """for index,row in excel_data.iterrows():
        print(f"index {index} , Incidencia: {row['Incidencia']}")
        # Print the filtered issues
        for issue in filtered_issues:
            if str(row['Incidencia']) in issue.subject:
                print("Issue encontrado :", row['Incidencia'])
                print("Issue ID:", issue.id)
                print("Subject:", issue.subject)
                print("-"*30)
            else:
                print("No Issue encontrado ")
        time.sleep(0.2)"""
    
        
    
    
    
if __name__ == "__main__":
    #excel_file="tickets_duplica2.xlsx"
    excel_file="C:\\Users\\gutie\\OneDrive\\Documentos\\PROYECTOS_ISES\\Incidencias_CF_FM\\filtro\\REPORTES_INCIDENCIAS_PROCESADAS\\COPIA_INCIDENCIAS_NUEVAS_GESTIONAR_20240126_1407.xlsx"
    checkIncidenciaRedmine(excel_file)
    
    
    """existing_incidencias = findduplicates(excel_file)
    print("existing_incidencias :",existing_incidencias)
    delete_rows_from_excel(excel_file, existing_incidencias)
    print("duplicates :", existing_incidencias)"""