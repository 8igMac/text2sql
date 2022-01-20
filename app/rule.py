from enum import Enum
from app.CRF.predict import predict
from app.time_dealer import time_processor
import json
import re
import datetime

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
    Example data: ['B-time', 'I-time', 'E-time', 'O', 'B-amount', 'I-amount', 'E-amount', 'O', 'O', 'O']
    Example output:
    {
        'date': [Entity('1月份', 0)],
        'type': [],
        'item': [],
        'amount': [Entity('總開銷', 4)],
    }
    """
    result = {
        'time': [],
        'class': [],
        'item': [],
        'amount': [],
    }
    beg = -1
    end = -1
    flag = False
    column = ''
    for i, token in enumerate(data):
        if flag:
            if token[0] == 'E' or token[0] == 'O':
                end = i
                if column in result:
                    result[column].append(Entity(text[beg:end+1], beg))
                else:
                    result[column] = [Entity(text[beg:end+1], beg)]
                flag = False
        else:
            if token[0] == 'B':
                flag = True
                column = token[2:]
                beg = i
            else:
                continue

    # # The dictionay contain all the lexicon in type and item.
    # with open(f'{current_dir}/CRF/dataset/word_class.json') as f:
    #     accounting_dict = json.load(f)
    return result

def get_time_constrain(result):
    # for date in result['date']:
    #     fmt = time_processor(date.text)
    #     d_ob = datetime.date.fromisoformat(fmt)

    return 'YEAR(date)=2022 AND MONTH(date)=1'
    

def classify_intent(text):
    """ Classify user intent based on predefine keyword."""
    if re.search(r'[佔|%|趴|幾成|比例|佔比]', text):
        return Intent.GET_PERCENTAGE
    elif re.search(r'[最|前(+d)]', text):
        return Intent.GET_TOP_N
    elif re.search(r'[共|多少|總]', text):
        return Intent.GET_TOTAL_AMOUNT
    elif re.search(r'[內容|細項|開銷|詳細|資料|所有|什麼|甚麼|哪一類]', text):
        return Intent.LIST_DATA

    return Intent.NOT_SUPPORTED

def text2sql(text: str):
    '''Hand craft rule for handling text2sql.

    Arguments:
    text -- Natural language query text.

    Return:
    A valid SQL query.
    '''

    # Use CRF model to predict the text.
    # bug: 1月份在餐飲食品花費前3高的項目 無法印出任何東西
    _, prediction = predict(input_=text)

    result = preprocess(prediction, text)
    intent = classify_intent(text)

    sql = ''
    # TODO: process time with time_processor
    if intent == Intent.GET_PERCENTAGE:
        # 分子
        num_constrain = get_time_constrain(result) + ' AND type="餐飲食品"'

        # 分母
        dom_constrain = get_time_constrain(result) + ' AND type="餐飲食品"'

        sql = (
            f'SELECT SUM(amount) / '
            f'('
                f'SELECT SUM(amount) FROM accounting '
                f'WHERE {dom_constrain} '
            f') AS "percent" '
            f'FROM accounting '
            f'WHERE {num_constrain};'
        )
    elif intent == Intent.GET_TOP_N:
        time_constrain = get_time_constrain(result)

        if re.search(r'[在]', text) and 'class' in result:
            if result["class"][0].text == '食物':
                typ = '餐飲食品'
            elif result["class"][0].text == '交通':
                typ = '汽機車'
            elif result["class"][0].text == '服飾':
                typ = '服飾'
            else:
                raise Exception("get total amount: unrecognize type")
            other_constrain = f' AND type="{typ}"'
        else:
            other_constrain = ''

        # Get column
        if re.search(r'[項目]', text):
            column = 'item'
        elif re.search(r'[類別]', text): 
            column = 'type'
        elif re.search(r'[天]', text): 
            column = 'date'
        else:
            raise Exception("Try to get top N but column ambiguity.")

        # Ascending or descending.
        if re.search(r'[高|多]', text):
            order = 'DESC'
        else:
            order = 'ASC'

        # Get top N
        if re.search(r'[最]', text):
            n = 1
        else:
            nums = re.findall(r'前\d+', text) 
            if len(nums) == 0:
                raise Exception("Try to get top N but no number found.")
            n = nums[0][1:]

        sql = (
            f'SELECT {column}, SUM(amount) FROM accounting '
            f'WHERE {time_constrain} {other_constrain} '
            f'GROUP BY {column} '
            f'ORDER BY SUM(amount) {order} ' 
            f'LIMIT {n};'
        )
        print(sql)#debug
    elif intent == Intent.GET_TOTAL_AMOUNT:
        time_constrain = get_time_constrain(result)
        print(result) #debug
        if len(result['item']) != 0:
            '''今年1月的晚餐共花多少錢？'''
            print('hi')
            sql = f'SELECT SUM(amount) FROM accounting WHERE {time_constrain} AND item="{result["item"][0].text}";'
        elif len(result['class']) != 0:
            '''上個月花在吃的上總共有多少錢？'''
            if result["class"][0].text == '食物':
                typ = '餐飲食品'
            elif result["class"][0].text == '交通':
                typ = '汽機車'
            elif result["class"][0].text == '服飾':
                typ = '服飾'
            else:
                raise Exception("get total amount: unrecognize type")
            sql = f'SELECT SUM(amount) FROM accounting WHERE {time_constrain} AND type="{typ}";'
        elif len(result['amount']) != 0:
            '''1月份的總開銷是多少'''
            sql = f'SELECT SUM(amount) FROM accounting WHERE {time_constrain};'
        else:
            raise Exception("Operation not supported.")
    elif intent == Intent.LIST_DATA:
        time_constrain = get_time_constrain(result)
        # if len(result['item']) != 0 or len(result['detail']):
        if len(result['class']) != 0:
            """今年1月11號我的開銷有哪些類別(花多少錢)?"""
            sql = f'SELECT type, SUM(amount) FROM accounting WHERE {time_constrain} GROUP BY type;'
        elif 'item' in result or 'detail' in result:
            """今年1月1號我買了什麼(花多少錢)?"""
            sql = f'SELECT item, amount FROM accounting WHERE {time_constrain};'
        else:
            raise Exception("Operation not supported.")
    elif intent == Intent.NOT_SUPPORTED:
        raise Exception("Operation not supported.")

    return sql
