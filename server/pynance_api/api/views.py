# Python Imports
import sys, datetime

# Django Imports
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Server Imports
from core import settings
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, Economy

# Application Imports
from app.portfolio import Portfolio
import app.statistics as statistics
import app.optimizer as optimizer
import app.settings as app_settings
import app.markets as markets

# Utility Imports
import util.helper as helper
import util.plotter as plotter
import util.logger as logger

output = logger.Logger("server.pynance_api.api.views", settings.LOG_LEVEL)

def verify_method(request, allowed_methods):
    if request.method not in allowed_methods: 
        return False
    else:
        return True

def log_secondary_args(parsed_args):
    if parsed_args['start_date'] is not None:
        output.comment(f'> Start : {parsed_args["start_date"]}')

    if parsed_args['end_date'] is not None:
        output.comment(f'> End: {parsed_args["end_date"]}')
    
    if parsed_args['target_return'] is not None:
        output.comment(f'> Target: {parsed_args["target_return"]}')
    
    if parsed_args['jpeg'] is not None:
        output.comment(f'> JPEG: {parsed_args["jpeg"]}')

def parse_secondary_args(request):
    if settings.REQUEST_PARAMS['start_date'] in request.GET:
        start_date = str(request.GET.get(settings.REQUEST_PARAMS['start_date']))
        start_date = helper.parse_date_string(start_date)
    else:
        start_date = None

    if settings.REQUEST_PARAMS['end_date'] in request.GET:
        end_date = str(request.GET.get(settings.REQUEST_PARAMS['end_date']))
        end_date = helper.parse_date_string(end_date)
    else:
        end_date = None

    if settings.REQUEST_PARAMS['target_return'] in request.GET:
        target_return = request.GET.get(settings.REQUEST_PARAMS['target_return'])
    else:
        target_return = None

    if settings.REQUEST_PARAMS['jpeg'] in request.GET:
        jpeg = str(request.GET.get(settings.REQUEST_PARAMS['jpeg']))
        jpeg = True if jpeg.lower() == 'true' else False
    else:
        jpeg = None

    parsed_args = {
        'start_date': start_date,
        'end_date': end_date,
        'target_return': target_return,
        'jpeg': jpeg
    }
    log_secondary_args(parsed_args)

    return parsed_args

def parse_tickers(request):
    if settings.REQUEST_PARAMS['tickers'] in request.GET:
        tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])
        for ticker in tickers:
            ticker = ticker.upper()
        return tickers
    else:
        return False

# If end_date and start_date are not provided, defaults to last 100 prices.
# If either end_date and start_date are provided, will return ALL records
# that match the criteria, i.e. less than or equal to end_date and greater_than
# or equal to start_date. Note, if only one is specified, the result will 
# contain all left-hand or right-hand records that match the criteria, i.e.
# if only start date is specified in, then it will return ALL records greater
# than or equal to the start_date
def parse_args_into_queryset(ticker, parsed_args):
    asset_type = markets.get_asset_type(ticker)

    if parsed_args['start_date'] is None and parsed_args['end_date'] is None:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker).order_by('-date')[:100]
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker).order_by('-date')[:100]
        else:
            return False

    elif parsed_args['start_date'] is None and parsed_args['end_date'] is not None:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker,
                                                date__lte=parsed_args['end_date']).order_by('-date')
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker,
                                                date__lte=parsed_args['end_date']).order_by('-date')
        else:
            return False
        
    elif parsed_args['start_date'] is not None and parsed_args['end_date'] is not None:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'], 
                                                date__lte=parsed_args['end_date']).order_by('-date')

        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'],
                                                date_lte=parsed_args['end_date']).order_by('-date')
        else:
            return False

    # start_date is not None and end_date is None
    else:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker,
                                                date__gte=parsed_args['start_date']).order_by('-date')
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker,
                                                date_gte=parsed_args['start_date']).order_by('-date')
        else:
            return False

# Note: model must implement to_date() and to_list() methods and have
#       ticker attribute
def queryset_to_list(price_set):
    set_list, price_list = {}, {}
    for price in price_set:
        price_list[price.to_date()] = price.to_list() 
    set_list[price_models.ticker] = price_list
    return set_list

def validate_request(request, allowed_methods=["GET"]):
    output.debug('Verifying request method...')
    if verify_method(request, allowed_methods):
        output.debug('Request method verified!')

        arg_err_or_tickers = parse_tickers(request)
        if arg_err_or_tickers:
            tickers = arg_err_or_tickers
            parsed_args = parse_secondary_args(request)

            return 200, { 'tickers': tickers, 'parsed_args': parsed_args }

        else:
            output.debug('No ticker query parameters provided')    
            return 400, { 'message': 'Input error' }

    else:
        output.debug('Request method rejected')
        return 405, { 'message' : "Request method not allowed" }

def risk_return(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])
    today = datetime.date.today()

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        response = {}
        profiles = []
        for i in range(len(tickers)):
            ticker_str = f'{tickers[i]}'
            output.debug(f'Calculating risk-return profile for {tickers[i]}')

            prices = parse_args_into_queryset(ticker=tickers[i], parsed_args=parsed_args)

            if prices.count() == 0:
                output.debug(f'No prices found in database, passing query to service.')
                profile = statistics.calculate_risk_return(ticker=tickers[i], start_date=parsed_args['start_date'], 
                                                            end_date=parsed_args['end_date'])
            else:
                output.debug(f'Prices found in database, passing result to statistics.')
                sample_prices = queryset_to_list(price_models=prices)
                profile = statistics.calculate_risk_return(ticker=tickers[i], sample_prices=sample_prices)

            response[ticker_str] = profile

            if parsed_args['jpeg']:
                profiles.append(profile)

        if parsed_args['jpeg']:
            graph = plotter.plot_profiles(symbols=tickers, profiles=profiles, show=False)
            response = HttpResponse(content_type="image/png")
            graph.print_png(response)
            return response

        else:
            return JsonResponse(data=response, status=status, safe=False)

def optimize(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])
    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']
        prices, sample_prices = {}, {}
        null_result = False

        # TODO: what is querysets.count() != each other?
        for ticker in tickers:
            prices[ticker] = parse_args_into_queryset(ticker, parsed_args)
            if prices[ticker].count() == 0:
                null_result=True
                break
        
        if null_result:
            output.debug(f'No prices found in database, passing query to service.')
            portfolio = Portfolio(tickers=tickers, start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
        else:
            output.debug(f'Prices found in database, passing result to statistics.')
            for ticker in tickers:
                sample_prices[ticker] = queryset_to_list(price_model=prices[ticker])[ticker]
            portfolio = Portfolio(tickers=tickers, sample_prices=sample_prices)  

        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=parsed_args['target_return'])
        allocation = helper.round_array(array=allocation, decimals=4)

        response = {
            'portfolio_return' : portfolio.return_function(allocation),
            'portfolio_volatility': portfolio.volatility_function(allocation)
        }
        subresponse = {}

        for i in range(len(tickers)):
            allocation_string = f'{tickers[i]}_allocation'
            subresponse[allocation_string] = allocation[i]

        response['allocations'] = subresponse
        return JsonResponse(data=response, status=status, safe=False)

def efficient_frontier(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)
    
    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        prices, sample_prices = {}, {}
        null_result = False

        # TODO: what is querysets.count() != each other?
        for ticker in tickers:
            prices[ticker] = parse_args_into_queryset(ticker, parsed_args)
            if prices[ticker].count() == 0:
                null_result=True
                break

        if null_result:
            output.debug(f'No prices found in database, passing query to service.')
            portfolio = Portfolio(tickers=tickers, start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
        else:
            output.debug(f'Prices found in database, passing result to statistics.')
            for ticker in tickers:
                sample_prices[ticker] = queryset_to_list(price_model=prices[ticker])[ticker]
            portfolio = Portfolio(tickers=tickers, sample_prices=sample_prices)  
            
        frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
    
        response = {}
        for i in range(len(frontier)):
            subresponse, subsubresponse = {}, {}
            port_string =  f'portfolio_{i}'

            allocation = helper.round_array(array=frontier[i], decimals=4)
            subresponse['portfolio_return'] = helper.truncate(portfolio.return_function(allocation),4)
            subresponse['portfolio_volatility'] = helper.truncate(portfolio.volatility_function(allocation), 4)

            for j in range(len(tickers)):
                allocation_string = f'{tickers[j]}_allocation'
                subsubresponse[allocation_string] = allocation[j]

            subresponse['allocation']=subsubresponse
            response[port_string] = subresponse
        
        if parsed_args['jpeg']:
            graph = plotter.plot_frontier(portfolio=portfolio, frontier=frontier, show=False)
            response = HttpResponse(content_type="image/png")
            graph.print_png(response)
            return response
        else:
            return JsonResponse(data=response, status=status, safe=False) 

# TODO: in future allow user to specify moving average periods through query parameters! 
def moving_averages(request, jpeg=False):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        prices, sample_prices = {}, {}
        null_result = False

        # TODO: what is querysets.count() != each other?
        for ticker in tickers:
            prices[ticker] = parse_args_into_queryset(ticker, parsed_args)
            if prices[ticker].count() == 0:
                null_result=True
                break

        if null_result:
            output.debug(f'No prices found in database, passing query to service.')
            averages_output = statistics.calculate_moving_averages(tickers=tickers, start_date=parsed_args['start_date'],
                                                                    end_date=parsed_args['end_date'])
        else: 
            output.debug(f'Prices found in database, passing result to statistics.')
            for ticker in tickers:
                sample_prices[ticker] = queryset_to_list(price_model=prices[ticker])[ticker]
            averages_output = statistics.calculate_moving_averages(tickers=tickers, sample_prices=sample_prices)

        moving_averages, dates = averages_output

        response = {}
        for i in range(len(tickers)):
            ticker_str=f'{tickers[i]}'
            MA_1_str, MA_2_str, MA_3_str = f'{ticker_str}_MA_1', f'{ticker_str}_MA_2', f'{ticker_str}_MA_3'    

            subresponse = {}
            if parsed_args['start_date'] is None and parsed_args['end_date'] is None:
                subresponse[MA_1_str] = moving_averages[i][0]
                subresponse[MA_2_str] = moving_averages[i][1]
                subresponse[MA_3_str] = moving_averages[i][2]

            else:
                subsubresponse_1, subsubresponse_2, subsubresponse_3 = {}, {}, {}
        
                for j in range(len(dates)):
                    date_str=helper.date_to_string(dates[j])
                    subsubresponse_1[date_str] = moving_averages[i][0][j]
                    subsubresponse_2[date_str] = moving_averages[i][1][j]
                    subsubresponse_3[date_str] = moving_averages[i][2][j]
 
                subresponse[MA_1_str] = subsubresponse_1
                subresponse[MA_2_str] = subsubresponse_2
                subresponse[MA_3_str] = subsubresponse_3

            response[ticker_str] = subresponse

        if parsed_args['jpeg']:
            periods = [app_settings.MA_1_PERIOD, app_settings.MA_2_PERIOD, app_settings.MA_3_PERIOD]
            graph = plotter.plot_moving_averages(symbols=tickers, averages_output=averages_output, periods=periods,
                                                    show=False)
            response = HttpResponse(content_type="image/png")
            graph.print_png(response)
            return response
        else:
            return JsonResponse(data = response, status=status, safe=False)

