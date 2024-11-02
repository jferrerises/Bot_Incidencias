import os


login_cred ={
'username' : '90082471',
'passwd':'MS0823',
'username_multas' : '90082471',
'passwd_multas':'MS0823',
}

DIR_PATH=os.getcwd()

API_KEY="2625e3ad722c4499c69c8a3321ca6189bcd1cc6c" #Se consigue en la interfaz de redmine

ANEXOS=['B','C']
dict_zonas={
    'GER_PANAMA':{
        'coords':None,
        'Oeste':None,
        'Metro':None
        
},
'GER_INTERIOR':{
    'coords':None,
    'sectores':None
},
'GER_CHIRIQUI':{
    'coords':None,
    'sectores':None
}
}

btnXY={
    'informes_folder':None,
    'desde':None,
    'hasta':None
}

monitor={
    'size':None
}

dates_app={
    'fecha_inicio':None,
    'fecha_fin':None,
    'ymes':None,
    'current_datetime':None
}

zonas_datetimes={
              'Oeste':None,
              'Metro':None,
              'Interior':None,
              'Chiriqui':None

}

## REnombre zonas desde excel
"""zonas_oldnew = {
    'PANAMA OESTE': 'Oeste',
    'PANAMA METRO': 'Metro',
    'COCLE VER - HERRERA L.S.': 'Interior',
    'CHIRIQUI': 'Chiriquí'
}"""
zonas_oldnew = {
    'PANAMA OESTE': 'Oeste',
    'PANAMA METRO': 'Metro',
    'AZUERO': 'Azuero',
    'CENTRAL': 'Central',
    'CHIRIQUI': 'Chiriquí'
}