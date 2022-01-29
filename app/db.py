import pymysql.cursors
import os
import time
import socket

HOST = os.getenv('MYSQL_HOST')
USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASSWORD')
DB = os.getenv('MYSQL_DB')

def wait_port(port: int, host='localhost', timeout=5.0):
    '''Wait for port start acepting TCP connection.
    Args:
        port (int): Port number.
        host (str): Host address.
        timeout (float): In seconds, how long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified
                      in `timeout`.
    '''

    while True:
        start_time = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as e:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(f'Wait too long for port {port} on host {host}'
                                'to start acepting connection') from e


wait_port(port=3306, host=HOST, timeout=5.0)

connection = pymysql.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DB,
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
