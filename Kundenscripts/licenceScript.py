import schedule
import time
from datetime import datetime
import re
import os
import hashlib
import requests
from rest_framework.decorators import api_view

"""
Globale Url des Management-Portals mit der subdirectory /heartbeat welche REST (POST) Abfragen bearbeitet
"""
URL = "http://localhost:8000/licences"

"""
dir: Root Ordner von dem aus angefangen wird nach dem /Kundenscripts subordner zu suchen
zaehler: Hilfsvariable für rekursiven Methodenaufruf mit anderem Root Ordner

"""
def searchFiles(dir: str, zaehler = 0):
    global URL
    abspathLog = ""
    abspathConfig = ""

    if zaehler == 2:
        return

    for root, dirs, files in os.walk(dir):
        print(root)
        if os.path.basename(root) != 'Kundenscripts':
            continue

        abspathLog = str(files[files.index('LOG.txt')])
        abspathConfig = str(files[files.index('config.txt')])
        path = open("./path.txt", "w")
        path.write(os.path.abspath(root))
        path.close()
        break

    if not abspathLog and not abspathConfig:
        searchFiles("D:/", zaehler + 1)

    PARAMS = readData(str(os.path.abspath(root)), abspathLog, abspathConfig)
    print(PARAMS)

    #encrypted = hashlib.sha256('1234').hexdigest()
    #print(encrypted)

    requests.post(url=URL, data=PARAMS)

"""
Liest die Daten aus config.txt und LOG.txt aus und speichert sie im PARAMS dict

@return dictionary
"""
def readData(dir: str, abspathLog: str, abspathConfig: str):
    if not dir or not abspathLog or not abspathConfig:
        return None

    abspathLog = dir + "\\" + abspathLog
    abspathConfig = dir + "\\" + abspathConfig
    print(abspathLog + "      " + abspathConfig)

    log = open(abspathLog, "r")
    meldung = str(log.read())
    log.close()

    pattern = "[0-2]{1}[0-9]{1}[:][0-5]{1}[0-9]{1}\s[0-3]{1}[0-9]{1}[.][0-1]{1}[0-9]{1}[.][2]{1}[0-1]{1}[0-9]{2}"
    try:
        meldung = re.findall(pattern + "\s[\[\]a-zA-Z0-9_ ]*", meldung)[-1]
    except:
        meldung = ''

    config = open(abspathConfig, "r")
    lizenz = config.read()
    config.close()

    PARAMS = {
        "key": lizenz,
        "log": meldung
    }

    return PARAMS


"""
Sendet den Request an die LIZENZEN API
"""
def directRequest(dir: str):
    PARAMS = readData(dir, "LOG.txt", "config.txt")
    #print(PARAMS)
    #print("URL:                   " + URL)
    x = requests.post(url= URL, data= PARAMS)
    overwrite(x)

"""
Führt den Lizenz Request aus und prüft vorher ob path.txt einen Inhalt besitzt, 
um basierend darauf zwei verschiedene Wege zu gehen (searchFiles/directRequest)
"""
def execute():
    try:
        path = open("./path.txt", "r")
        abspathPath = path.read()
        path.close()
    except FileNotFoundError:
        abspathPath = ""

    if not abspathPath:
        searchFiles("C:/")
    else:
        directRequest(abspathPath)

#schedule.every(1).seconds.do(execute)

#while True:
 #   schedule.run_pending()
  #  time.sleep(1)

"""
Öffnet die Config-Datei, leer diese und fügt neue Lizenzschlüssel hinein
"""
def overwrite(request):
    print(request)

    try:
        config = open("KundenScripts\config.txt","w")
        config.truncate(0) #leert den Inhalt der config-Datei
        config.write(request.data) #schreibt neue Lizenz "newLicense"(aus response) in die config
        config.close()
    except:
        pass

