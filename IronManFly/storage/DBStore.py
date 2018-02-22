

import hashlib
from time import time
import psycopg2
from sqlalchemy import create_engine
from uuid import uuid4



class DBStore:
    """
    about storage, storage is a dict including keys DB_URL and NAME
    support database: mysql, postgresql, sqlite, oracle e.t.
    Mysql:
        db_url: "mysql://name:password@host/dbname",
    and so on
    about get function:
    you can give 3 params: url, default and expiration
    url: the source url you want to request
    default: return to you the default if instance can not find url source stored in disk
    expiration: means that you do not need source stored over expiration
    """
    MYSQL_SQL = """CREATE TABLE IF NOT EXISTS `ToApi`(
                   `url` VARCHAR(100),
                   `html` MEDIUMTEXT NOT NULL,
                   `create_time` FLOAT NOT NULL,
                   PRIMARY KEY ( `url` )) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8;"""
    SQLITE_SQL = """CREATE TABLE IF NOT EXISTS ToApi(
                    url VAR(100) PRIMARY KEY,
                    html TEXT,
                    create_time FLOAT);"""
    POSTGRES_SQL = """CREATE TABLE IF NOT EXISTS ModelActions_v1(
                    model_id varchar,
                    model_name varchar,
                    model_version varchar,
                    model_request varchar,
                    model_result varchar,
                    model_action varchar,
                    user_id varchar,
                    business_id varchar,
                    create_time varchar);"""

    def __init__(self, user, password, db, host='localhost', port=5432):
        self.db = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)
        self.cur = self.db.cursor()
        self.cur.execute(self.POSTGRES_SQL)
        self.db.commit()
        #cur.close()
        #self.db.close()
    def saveActionData(self, model_id, model_name,model_version,model_request,model_result,model_action,user_id,business_id,create_time):
        #cur = self.db.cursor()
        sql = """INSERT INTO ModelActions_v1 
                 (model_id, model_name,
                 model_version,model_request,model_result,
                 model_action,user_id,business_id,
                 create_time)VALUES(%s, %s, %s, %s,%s,%s, %s,%s,%s)"""
        self.cur.execute(sql, (model_id, model_name,model_version,model_request,model_result,model_action,user_id,business_id,create_time))
        
        self.db.commit()
        self.cur.close()
        self.db.close()

    def getActionData(self, query_condition):
        self.cur.execute("SELECT * FROM ModelActions_v1 where %s;"%(query_condition))
        rows = self.cur.fetchall()        # all rows in table
        #print(rows)
        return rows
        self.db.commit()
        #self.cur.close()
        #self.db.close()
        '''
        file_name = hashlib.md5(url.encode()).hexdigest()
        row = self.db.execute("SELECT html, create_time FROM ToApi where url='{}';".format(file_name)).first()
        try:
            origin_data = dict(row).get("html")
            create_time = dict(row).get("create_time")
            if (time() - create_time) > float(expiration):
                self.db.execute("DELETE FROM ToApi WHERE url='{}';".format(file_name))
                return default
            data = eval(origin_data).decode("unicode-escape")
            data = data.replace("toapi###$$$###toapi", "\"").replace("toapi***$$$***toapi", "\'")
        except TypeError as e:
            return default
        return data
        '''
'''
#DBStore(db_url='postgresql://leepand:lipd@123@localhost/leepand')
model_id='xgboost_v1' 
model_name='xgboost'
model_version='v2'
model_result='hh'
model_action='0'
userid= str(uuid4())
businessid=str(uuid4())
create_time=time()
test=DBStore(user='leepand', password='lipd@123', db='leepand', host='localhost', port=5432)
test.saveActionData(model_id=model_id,\
          model_name=model_name,\
          model_version=model_version,\
          model_result=model_result,
          model_action=model_action,
          user_id=userid,
          business_id=businessid,
          create_time=create_time)
'''        