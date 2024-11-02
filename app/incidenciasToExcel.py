import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import configparser
config_file = 'config.ini'
config = configparser.ConfigParser()
config.read(config_file)

FOLDER_INC_PROCESADAS = os.path.abspath(f"{config.get('AppConfig', 'folder_inc_procesadas')}")
dateInc = datetime.now().strftime("%Y%m%d_%H%M")




def listToExcel(listIncidencias):
    fname=f"Incidencias_PROCESADAS_Redmine_{dateInc}.xlsx"
    excel_filename=os.path.join(FOLDER_INC_PROCESADAS,fname)
    df = pd.DataFrame(listIncidencias)
    df.to_excel(excel_filename, index=False )
    return excel_filename,fname

def listToExcelNo(listIncidencias):
    fnameNot=f"Incidencias_NO_PROCESADAS_Redmine_{dateInc}.xlsx"
    fNoProc=os.path.join(FOLDER_INC_PROCESADAS,fnameNot)
    df = pd.DataFrame(listIncidencias)
    df.to_excel(fNoProc, index=False )
    return fNoProc,fnameNot

def sendEmail(status,fattachPath, attchFile):
    # Email configuration
    sender_email = 'Notificaciones-serviciosdecatalogo@ises.com.co'
    sender_password = 'Wom79665'
    receiver_email = 'evargas@ises.com.co'

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f'INCIDENCIAS {status} EN REDMINE DESDE AUTOMATIZACION - {dateInc}'

    # Attach the Excel file
    with open(fattachPath, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attchFile}')
        msg.attach(part)

    # Send the email using SMTP
    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Email sending failed: {str(e)}")


def inctoExc(listIncidencias,status):
    path = None
    fname=None
    if status =="GESTIONADAS":
        for x in listIncidencias:
            """newUpList=[]
            for y in x['uploads']:
                newUpList.append(y['filename'])"""
            x['uploads'] = []

            """newChList=[]
            for y in x['checklist']:
                newChList.append(y['subject'])
            x['checklist'] = newChList"""
        path,fname = listToExcel(listIncidencias)
    elif status=="NO_GESTIONADAS":
        path,fname = listToExcelNo(listIncidencias)
    sendEmail(status, path, fname)