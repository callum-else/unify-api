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

# from contextlib import contextmanager
# from .db_init import Session

# @contextmanager
# def session_scope():
#     """Provide a transactional scope around a series of operations."""
#     session = Session()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         session.close()