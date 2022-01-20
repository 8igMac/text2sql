

def time_processor(time) -> str:
    """Process natural language time into YYYY-MM-DD format.
    Arguments
        time - Natural language time.
    Return: 
        time in YYYY-MM-DD format.

    e.g. (assume today is '2022-01-20')
        上個月       ->  '2021-12'
        前兩個禮拜    -> '2022-01-06'
        去年         -> '2021'
        上禮拜六      -> '2021-01-15'
        去年十月十九號    -> '2021-10-19'

    """
    print("input: ", time)
    import datetime
    import re
    # time_zone = datetime.timezone(datetime.timedelta(hours=+8))
    word2num = {"一": "1", "兩":"2", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "1"}
    

    today = datetime.date.today()
    token = time[0]

    if time == "今年":
        return str(today.year)

    if token == "上":
        time = time[1:]
        if time.find("週") != -1 or time.find("禮拜") != -1:
            weekday = today.weekday()
            start_delta = datetime.timedelta(days=weekday, weeks=1)
            start_of_week = today - start_delta

            if word2num.get(time[-1], None):
                temp = word2num.get(time[-1], None)
                result = start_of_week + datetime.timedelta(days=int(temp))
                return result.strftime('%Y-%m-%d')
            else:
                print("unknown format")
        
        elif time.find("月") != -1:
            first = today.replace(day=1)
            lastMonth = first - datetime.timedelta(days=1)
            result = str(lastMonth.year) + "-" + str(lastMonth.month)
            return result
                

    if token == "前":
        time = time[1:]
        num = word2num.get(time[0], None)
        if time.find("週") != -1 or time.find("禮拜") != -1:
            if num:
                weekday = today.weekday()
                start_delta = datetime.timedelta(days=weekday, weeks=int(num))
                result = today - start_delta
                return result.strftime('%Y-%m-%d')

            else:
                print("unknown format")     
        
        elif time.find("月") != -1:
            if num:
                num = int(num)
                temp = today.replace(day=1)

                for i in range(num):
                    lastMonth = temp - datetime.timedelta(days=1)
                    temp = lastMonth.replace(day=1)

                result = str(temp.year) + "-" + str(temp.month)
                return result

            else:
                print("unknown format")          


    if re.match(r'今年\d+月', time):
        result = str(today.year) + "-" + time[2:-1]
        return result


    if re.match(r'今年\d+月\d+日', time):
        result = str(today.year) + "-"
        search = re.search(r'今年(\d+)月(\d+)日', time)

        result = time.replace("今年", str(today.year)+"-")
        result = result.replace("月", "-")
        result = result.replace("日","")
        return result




    if re.match(r'[0-9]+年[0-9]+月[0-9]+日', time):
        search = re.search(r'(\d+)年(\d+)月(\d+)日', time)
        result = search[1] + "-" + search[2] + "-" + search[3]
        return result


    if re.match(r'去年\S+月\S+日', time):
        result = str(today.year - 1) + "-"
        search = re.search(r'去年(\S+)月(\S+)日', time)

        month = search[1]
        date = search[2]
        if month == "十":
            result += "10-"
        elif len(month) == 2:
            result += word2num.get(month[0]) + word2num.get(month[1]) + "-"
        else:
            result += word2num.get(month[0]) + "-"
        
        if date == "十":
            result += "10"
        elif len(date) == 2:
            result += word2num.get(date[0]) + word2num.get(date[1])
        else:
            result += word2num.get(date[0])


        return result


if __name__ == '__main__':
    print(time_processor("今年1月"))
    print(time_processor("上禮拜一"))
    print(time_processor("101年1月1日"))

