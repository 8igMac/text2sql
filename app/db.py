import pymysql.cursors

# TODO: Move credential away.
connection = pymysql.connect(
    host='localhost',
    user='text2sql',
    password='text2sql',
    database='text2sql',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# TODO: How to close connection when program exit?

def execute(sql: str) -> dict:
    '''Execute given sql command and return the result as string.'''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result_dict = cursor.fetchall()
    return result_dict

def get_all_data():
    '''Get all data from the table.'''
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM accounting;')
        result_dict = cursor.fetchall()
    return result_dict
