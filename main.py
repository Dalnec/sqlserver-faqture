import schedule
import time
import sys
import os

if __name__ == "__main__":
    sys.path.append('kulami')
    sys.path.append('base')
    sys.path.append('pseapi')

    from kulami.models import leer_db_access
    from pseapi.api import create_document  

    while True:
        lista_ventas = leer_db_access()    
        create_document(lista_ventas)
        time.sleep(1)