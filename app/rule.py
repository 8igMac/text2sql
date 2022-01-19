from enum import Enum
from app.CRF.predict import predict

# NOTE: Solve pickle reference issue. See [here](https://stackoverflow.com/questions/2121874/python-pickling-after-changing-a-modules-directory/2121918#2121918)
import os
import sys
current_dir = os.path.dirname(__file__)
sys.path.append(f'{current_dir}/CRF/')

class Intent(Enum):
    GET_PERCENTAGE = 1
    GET_TOP_N = 2
    GET_TOTAL_AMOUNT = 3
    LIST_DATA = 4
    NOT_SUPPORTED = 5

class Entity():
    def __init__(self, text: str, idx: int):
        self.text = text
        self.idx = idx

def preprocess(data, text):
    """
    Example text: 1月份的總開銷是多少
    Example output:
    {
        'date': [Entity('1月份', 0)],
        'type': [],
        'item': [],
        'amount': [Entity('總開銷', 4)],
    }
    """
    # TODO: preprocess
    result = {
        'date': [Entity('1月份', 0)],
        'type': [],
        'item': [1],
        'amount': [Entity('總開銷', 4)],
    }
    return result

def time_processor(time) -> str:
    """Process natural language time into YYYY-MM-DD format.
    Arguments
    time - Natural language time.

    Return: time in YYYY-MM-DD format.
    """
    return '2022-01-01'

def classify_intent(text):
    """ Classify user intent based on predefine keyword."""
    # TODO: implement this
    return Intent.GET_PERCENTAGE

def text2sql(text: str):
    '''Hand craft rule for handling text2sql.

    Arguments:
    text -- Natural language query text.

    Return:
    A valid SQL query.
    '''

    # TODO: Load CRF model

    # TODO: Use CRF model to predict the text.
    text = '1月份的總開銷是多少'
    data = ['B-time', 'I-time', 'E-time', 'O', 'B-amount', 'I-amount', 'E-amount', 'O', 'O', 'O']

    result = preprocess(data, text)
    intent = classify_intent(text)

    sql = ''
    # TODO: how to process time?
    if intent == Intent.GET_PERCENTAGE:
        time_constrain_num = 'YEAR(date)=2022 AND MONTH(date)=1'
        time_constrain_dom = 'YEAR(date)=2022 AND MONTH(date)=1'

        sql = (
            f'SELECT SUM(amount) / '
            f'('
                f'SELECT SUM(amount) FROM accounting '
                f'WHERE {time_constrain_dom} '
            f') AS "percent" '
            f'FROM accounting '
            f'WHERE {time_constrain_num} AND type="餐飲食品";'
        )
    elif intent == Intent.GET_TOP_N:
        # TODO: HERE
        # if len(result['type']) == 0 or len(result['item']) == 0 or len(result['amount']) == 0:
        #     raise Exception("Operation not supported.")

        time_constrain = 'YEAR(date)=2022 AND MONTH(date)=1'
        other_constrain = 'AND type="餐飲食品"'
        column = 'item'
        order = 'DESC'
        n = 2

        sql = (
            f'SELECT {column}, SUM(amount) FROM accounting '
            f'WHERE {time_constrain} {other_constrain} '
            f'GROUP BY {column} '
            f'ORDER BY SUM(amount) {order} ' 
            f'LIMIT {n};'
        )
    elif intent == Intent.GET_TOTAL_AMOUNT:
        if len(result['item']) != 0:
            '''今年1月的晚餐共花多少錢？'''
            sql = f'SELECT SUM(amount) FROM accounting WHERE date="{time_processor("d")} AND item="{result["item"][0]}";'
        elif len(result['type']) != 0:
            '''上個月花再吃的上總共有多少錢？'''
            sql = f'SELECT SUM(amount) FROM accounting WHERE date="{time_processor("d")} AND type="{result["type"][0]}";'
        elif len(result['amount']) != 0:
            '''1月份的總開銷是多少'''
            sql = f'SELECT SUM(amount) FROM accounting WHERE date="{time_processor("d")};'
        else:
            raise Exception("Operation not supported.")
    elif intent == Intent.LIST_DATA:
        if len(result['item']) != 0:
            """今年1月1號我買了什麼(花多少錢)?"""
            sql = f'SELECT item, amount FROM accounting WHERE date="{time_processor("d")}";'
        elif len(result['type']) != 0:
            """今年1月11號我的開銷有哪些類別(花多少錢)?"""
            sql = f'SELECT type, SUM(amount) FROM accounting WHERE date="{time_processor("g")}" GROUP BY type;'
        else:
            raise Exception("Operation not supported.")
    elif intent == Intent.NOT_SUPPORTED:
        raise Exception("Operation not supported.")

    return sql
