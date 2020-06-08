import pyodbc 
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

db_driver = config['BASE']['DB_DRIVER']
db_server = config['BASE']['DB_SERVER']
db_name = config['BASE']['DB_NAME']

def __conectarse():
    try:
        # nos conectamos a la bd SQLServer
        cnx = pyodbc.connect('Driver={'+db_driver+'};' 'Server='+db_server+';'
                            'Database='+db_name+';' 'Trusted_Connection=yes;')
        return cnx
    except (Exception, pyodbc.Error) as error:
        print("Error fetching data from SQLServer table", error)


def update_venta_pgsql(id):
    try:
        cnx = __conectarse()
        cursor = cnx.cursor()
        cursor.execute(
            "UPDATE Labbio.dbo.TBLVentas SET Obs ='PROCESADO' WHERE IdVen = ?", id)
        cnx.commit()
    finally:
        # closing database connection
        if (cnx):
            cursor.close()
            cnx.close()


