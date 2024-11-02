import configparser
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
import json,os
from loggerObj import logger
from datetime import datetime

config_file = 'config.ini'
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file)



def tableEmailHtml():
    return 0

def sendEmail(zona,email,datos, fecha,analista):
    try:
        #Credenciales email de envío
        MAIL_SERVER = 'smtp-mail.outlook.com'
        MAIL_PORT = 587
        MAIL_USE_TLS =  True
        MAIL_USE_SSL= False
        MAIL_USERNAME = 'Notificaciones-serviciosdecatalogo@ises.com.co'
        MAIL_DEFAULT_SENDER = 'Notificaciones-serviciosdecatalogo@ises.com.co'
        MAIL_PASSWORD = 'Wom79665'
        
        MAIL_SUBJECT_PREFIX = u"Generación de Anexos - Servicio de Catalogo"
        
        from_address = formataddr((MAIL_SUBJECT_PREFIX, MAIL_USERNAME))
        mail = MIMEMultipart()
        mail["From"] = from_address
        cc=["mario@wiselyx.com","evargas@ises.com.co"]

        # Configuras propiedades
        mail["Subject"] = f"GENERACIÓN DE ANEXOS B Y C {fecha} | INCIDICENCIAS CF Y FM"
        mail["Cc"] = "; ".join(cc)
        mail["To"] = "evargas@ises.com.co"
   

        # Crea tabla HTML
        html_table = f'Generación de Anexos B y C para {analista} | Zona : {zona}\n<br/>\n<br/>'
        html_table += f'A continuación se encuentran los rangos de fechas requeridos para la exportación de Anexos B y C correspondientes a la zona: {zona} desde MULTAS SGI \n<br/>\n<br/>'
        html_table += '<table>\n'

        # Agrega  headers de tabla
        html_table += '<thead><tr><th>Zona</th><th>Fecha Inicio</th><th>Fecha Fin</th></tr></thead>\n'
        css_style = """
        <html>
    <head>
        <style>\n\
        div {\n\
        width:100%;\n\
        
        }\n\
        table {\n\
                width: 100%;\n\
                border-collapse: collapse;\n\
                border: 1px dotted black;\n\
            }\n\
            th, td {\n\
                padding: 10px;\n\
                background-color:#f4f2f0;\n\
                text-align: center;\n\
                border: 1px dotted black;\n\
            }\n\
        
        
        </style>
        </head>
        <body>
        <div>
        """
        # Encabezado con email del autorizador
        # Add footer 
        footer = """
        Saludos,\n<br/>\n<br/>



        <b>Servicio de Catálogo | Incidencias CF y FM</b>\n<br/>
        
        
        <a href="http://www.ises.com.co">www.ises.com.co</a><br>
        """
        footer = f"""{footer}\n<br/><img src="https://ises.com.co/assets/Cabecero/ISES%20cabecero.png">"""
        
        # Agrega cuerpo de la tabla
        html_table += '<tbody>\n'
        
        # Adjuntos
        
        #mail.attach(email_data["attachment"])
        for x in datos:
            html_table += '<tr>'
            html_table += f"<td>{zona}</td><td>{x[0]}</td><td>{x[1]}</td>"
            html_table += '</tr>\n'

        # Cierra la tabla
        html_table += '</tbody>\n'
        html_table += '</table>\n</div>\n</body>\n</html>'
        
        html_body =f"{css_style}<br>{html_table}<br> {footer}"
        mail.attach(MIMEText(html_body, "html"))


        #mail.HTMLBody = html_body

        # Send the email
        #sent = mail.Send()
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()  # Start a secure TLS connection (if your server supports it)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            print("recipients")
            #recipients = [email] + cc
            recipients = "amaldonado@ises.com.co"
            print("recipients :", recipients)
            response_dict = server.sendmail(MAIL_USERNAME, recipients, mail.as_string())
        
        if not response_dict:
         
            
            # Funcion para eliminar attachments en TEMP
           
            logger.info(f"Email a {email} Zona: {zona} Fecha: {fecha} enviado exitosamente")
            return 200
        else:
            #save_sent_mail(email_data['id_issue'],email_data['recipient'],email_data['subject'],"fallo")
            logger.warning(f"""Email a {email} Zona: {zona} fallo al enviar""")
            print(email, "error")
    except Exception as e:
        print("Exception as :", e)
        
        logger.error(f"""Email a {email}  Zona: {zona} fallo al enviar: {e}""")
        return 500
    return 0







def procesamiento(dict_incidencias):
    fecha = datetime.now().strftime("%d/%m/%Y")
    with open(os.path.abspath(os.path.join('app','ambitoyanalistas_central_azuero.json')),"r",encoding='utf-8') as analistas:
        data = json.load(analistas)

    for key,value in dict_incidencias.items():
        email = data.get(key, {}).get("email")
        analista = data.get(key, {}).get("analista")
        ambito = data.get(key, {}).get("ambito")
        if email:

            resp = sendEmail(zona=ambito, email=email, datos = value, fecha=fecha, analista=analista)
            print(f"{resp} : Key: {key}, Email: {email}")
            time.sleep(5)
    return 0