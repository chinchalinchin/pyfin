import datetime, os, io, json, csv, zipfile
import holidays
import requests
import app.settings as settings

def get_number_input(msg_prompt):
    while True:
        user_input = input(msg_prompt)
        if user_input.isnumeric():
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')

def strip_string_array(array):
    new_array = []
    for string in array:
        new_array.append(string.strip())
    return new_array
    
def format_allocation_profile(allocation, portfolio):
    port_return, port_volatility = portfolio.return_function(allocation), portfolio.volatility_function(allocation)
    formatted_result = "( "+str(100*port_return)[:5]+"%, " + str(100*port_volatility)[:5]+"%)"
    formatted_result_title = "("
    for symbol in portfolio.tickers:
        if portfolio.tickers.index(symbol) != (len(portfolio.tickers) - 1):
            formatted_result_title += symbol+", "
        else:
            formatted_result_title += symbol + ") Portfolio Return-Risk Profile"
    whole_thing = formatted_result_title +" = "+formatted_result
    return whole_thing

# YYYY-MM-DD
def is_date_string_weekend(date_string):
    dates=str(date_string).split('-')
    weekday = datetime.datetime(year=int(dates[0]), month=int(dates[1]), day=int(dates[2])).weekday()
    if weekday in [5,6]:
        return True
    else:
        return False

# YYYY-MM-DD
def is_holiday(date_string):
    us_holidays = holidays.UnitedStates()
    return (date_string in us_holidays)

# YYYY-MM-DD
def get_holidays_between(start_date_string, end_date_string):
    us_holidays = holidays.UnitedStates()
    return len(us_holidays[start_date_string: end_date_string])

# YYYY-MM-DD
def consecutive_trading_days(start_date_string, end_date_string):
    # if weekends, return false
    if is_date_string_weekend(start_date_string) or is_date_string_weekend(end_date_string):
        return False

    start_parsed = str(start_date_string).split('-')
    end_parsed = str(end_date_string).split('-')
    start_date = datetime.date(year=int(start_parsed[0]), month=int(start_parsed[1]), day=int(start_parsed[2]))
    end_date = datetime.date(year=int(end_parsed[0]), month=int(end_parsed[1]), day=int(end_parsed[2]))
    delta = end_date - start_date

    if delta.days < 0:
        buffer = start_date
        start_date = end_date
        end_date = buffer
        delta = end_date - start_date

    holiday_count = get_holidays_between(start_date_string=start_date_string, end_date_string=end_date_string)

    if (delta.days - holiday_count) == 0:
        return False

    elif (delta.days - holiday_count) == 1:
        return True

    elif ((delta.days - holiday_count) > 1 and (delta.days - holiday_count) < 4):
        start_week, end_week = start_date.isocalendar()[1], end_date.isocalendar()[1]

        if start_week == end_week:
            return False

        else:
            return True

    else:
        return False

def get_first_json_key(this_json):
    return list(this_json.keys())[0]

def parse_price_from_date(prices, date, asset_type):
    try:
        if asset_type == settings.ASSET_EQUITY:
            return prices[date][settings.AV_RES_EQUITY_CLOSE_PRICE]
        elif asset_type == settings.ASSET_CRYPTO:
            return prices[date][settings.AV_RES_CRYPTO_CLOSE_PRICE]
    except:
        return False

def replace_troublesome_chars(msg):
    return msg.replace('\u2265','').replace('\u0142', '')

def parse_csv_response_column(column, url, firstRowHeader=None, savefile=None, zipped=None):
    col, big_mother = [], []

    with requests.Session() as s:
        download = s.get(url)
        
        if zipped is not None:
            zipdata = io.BytesIO(download.content)
            unzipped = zipfile.ZipFile(zipdata)
            with unzipped.open(zipped, 'r') as f:
                for line in f:
                    big_mother.append(replace_troublesome_chars(line.decode("utf-8")))
                cr = csv.reader(big_mother, delimiter=',')
        
        else:
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')

        s.close()
    
    for row in cr:
        if row[column] != firstRowHeader:
            col.append(row[column])

    if savefile is not None:    
        with open(savefile, 'w') as outfile:
            json.dump(col, outfile)
            
def clear_dir(directory, retain=True):
    filelist = [ f for f in os.listdir(directory)]
    if retain:
        for f in filelist:
            filename = os.path.basename(f)
            if filename != ".gitkeep":
                os.remove(os.path.join(directory, f))

    else:
        for f in filelist:
            os.remove(os.path.join(directory, f))

def clear_cache(outdated_only=False):
    filelist = [ f for f in os.listdir(settings.CACHE_DIR)]

    if outdated_only:
        now = datetime.datetime.now()
        timestamp = '{}{}{}'.format(now.month, now.day, now.year)
        for f in filelist:
            filename = os.path.basename(f)
            if filename != ".gitkeep" and timestamp not in filename:
                os.remove(os.path.join(settings.CACHE_DIR, f))

    else:
        for f in filelist:
            filename = os.path.basename(f)
            if filename != ".gitkeep":
                os.remove(os.path.join(settings.CACHE_DIR, f))