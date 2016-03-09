import psycopg2
from database import login_info

def get_connector(db = None, 
               create_new_tables=False
               ):
    """Establishes connection to a database; creates it if it doesn't exist;
       returns a conn object"""

    #Create a new db if needed.  A bit convoluted in psql because you need to establish a new connection
    #   to address a different db.  (In MySQL, it's as simple as going:  USE database;)

    conn = psycopg2.connect(
        user=login_info['user'],
        password=login_info['password']
    )
    curs = conn.cursor()    

    #if the database is not available, try to create it
    try:
        curs.execute('END')
        curs.execute('CREATE DATABASE {}'.format(db))
    except psycopg2.ProgrammingError:      
        pass  #datbase already exists	

    #make a new connection to the right database
    conn.close()
    conn = psycopg2.connect(database = db,
                            user=login_info['user'],
                            password=login_info['password']
                            )
    return conn   		

def make_tables(db=None):
    "creates database tables"
    
    """As this builds out, the database needs to be designed better. 
       It needs separate, normalized tables to include:
       - images (raw, thumb, source, id_authority, GPS, etc.
       - id items (latin name, english name, etc.)"""
    
    conn=get_connector(db=db)
    curs = conn.cursor() 
    
    main_table_name='snake_info'
    sql="DROP TABLE IF EXISTS {} CASCADE".format(main_table_name)
    curs.execute(sql)
    sql="CREATE TABLE {}( ".format(main_table_name)
    sql+="id SERIAL UNIQUE PRIMARY KEY, "
    sql+="thumb_file VARCHAR(120), "
    sql+="orig_image_file VARCHAR (120), "
    sql+="web_image_file VARCHAR (120), "
    sql+="species VARCHAR(50), "
    sql+="identifying_authority VARCHAR (100), "   
    sql+="img_file VARCHAR(80), "    
    sql+="source VARCHAR(100)"  
    sql+=')'
    curs.execute(sql) 
    conn.commit()
    
    table_name='snake_colors'
    sql="DROP TABLE IF EXISTS {}".format(table_name)
    curs.execute(sql)
    sql="CREATE TABLE {}( ".format(table_name)
    sql+="id SERIAL UNIQUE PRIMARY KEY, "
    sql+="pct INTEGER, "
    sql+="r INTEGER, "
    sql+="b INTEGER, "
    sql+="g INTEGER, "
    sql+="h FLOAT, "
    sql+="s FLOAT, "
    sql+="v FLOAT, "
    sql+="html VARCHAR(8), "
    sql+="snake_id integer REFERENCES {}(id)".format(main_table_name)
    sql+=')'
    curs.execute(sql)

    conn.commit()
    conn.close()
    
if __name__=='__main__'    :
    make_tables(db='snakes')
    