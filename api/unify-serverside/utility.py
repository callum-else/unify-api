from pymysql import connect, cursors

def db_connect():
    connection = connect (
        host='localhost',
        port=3306,
        user='unify',
        password='V8oU!LkuYz',
        db='unify',
        charset='utf8mb4',
        cursorclass=cursors.DictCursor
    )
    return connection