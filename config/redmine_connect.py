from redminelib import Redmine # install python-redmine
import requests
import sys
from loggerObj import logger
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def redmine_object():
    try:
        API_KEY="2625e3ad722c4499c69c8a3321ca6189bcd1cc6c"
        project_url="https://soporteprocesos.ises.com.co/redmine"

        headers={
            "X-Redmine-API-Key":API_KEY,
            "Content-Type": "application/json"
        }
        #https://soporteprocesos.ises.com.co/redmine/projects/gestion-economica/issues?set_filter=1&tracker_id=13
        try:
            redmine = Redmine(project_url, key=API_KEY,requests={'verify': False,'headers':headers})
        except Exception as e:
            print(e)
        print(redmine)
        return redmine
    except Exception as e:
        _, _, tb  = sys.exc_info()
        functionName = tb.tb_frame.f_code.co_name
        logger.error(f"Excepción de ejecución en {functionName} : {e}")
        raise