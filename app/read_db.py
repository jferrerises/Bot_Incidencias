import sqlite3


conn= sqlite3.connect('PRUEBA_trazabilidad_issues_NOBORRAR.db')
c = conn.cursor()
c.execute("""SELECT * FROM trazabilidad where incidencia = ?""",(957677,))

result = c.fetchall()

print(result)