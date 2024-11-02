import pandas as pd
import sqlite3
import time


connection = sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
cursor = connection.cursor()
def getDbList():
    # 1. Get 'incidencias' from the database
    query = "SELECT incidencia FROM trazabilidad WHERE start_date = '2023-10-19'"

    cursor.execute(query)
    query_results = [row[0] for row in cursor.fetchall()]
    connection.close()
    return query_results



def db_trazabilidad(row, datehoy):
    try:
        conn= sqlite3.connect('trazabilidad_issues_NOBORRAR.db')
        c = conn.cursor()
       
        c.execute("""INSERT INTO trazabilidad (incidencia, start_date, due_date,
        estado, excepcion, tipo_causa,descripcion, fecha_incidencia, zona, causa, cnt_anexos, assigned_to,
        uploads) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",(row['Incidencia'],datehoy,"",
                                                    "Creado","",row['Tipo de Causa'],row['Descripción'],row['Fecha Detección'],
                                                    row['Zona'],row['Causa'],"","",""))
        conn.commit()
        conn.close()
    except Exception as e:
        print("exception as e:", e)
        raise


def editDB(d):
    # 2. Read an Excel file as a DataFrame
    df = pd.read_excel(r'C:\\Users\\gutie\\OneDrive\\Documentos\\PROYECTOS_ISES\\Incidencias_CF_FM\\filtro\\INCIDENCIAS_PROCESADAS_2023-10-19.xlsx')
    print(df.head())
    print("len dataframe :",len(df))
    # 3. Compare and insert
    ls = []
    for index, row in df.iterrows():
        incidencia = str(row['Incidencia'])
        if incidencia not in d:
            print(f"row : {row}")
            ls.append(incidencia)
            # 4. Insert the row into the database
            db_trazabilidad(row, '2023-10-19')
            time.sleep(2)
           
    print("list de no guardados :", ls)
    print("len de no guardados :", len(ls))





if __name__=="__main__":
    get_db_list = getDbList()
    print("len guardados hoy :", len(get_db_list))
    editDb = editDB(get_db_list)