import os, datetime
import numpy, matplotlib
from PIL import Image

from matplotlib import pyplot as plot
from matplotlib.figure import Figure
from matplotlib import dates as matdates

import util.formatter as formatter
import util.helper as helper

APP_ENV=os.environ.setdefault('APP_ENV', 'local')

if APP_ENV == 'local':
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    matplotlib.use("Qt5Agg")
elif APP_ENV == 'container':
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    matplotlib.use("agg")

def plot_frontier(portfolio, frontier, show=True, savefile=None):
    title = " ("
    for i in range(len(portfolio.tickers)):
        if i != (len(portfolio.tickers) - 1):
            title += portfolio.tickers[i] + ", "
        else:
            title += portfolio.tickers[i] + ") Efficient Frontier"
    
    return_profile, risk_profile = [], []
    for allocation in frontier:
        return_profile.append(portfolio.return_function(allocation))
        risk_profile.append(portfolio.volatility_function(allocation))
    
        # don't think numpy arrays are needed...
    # return_profile = numpy.array(return_profile)
    # risk_profile = numpy.array(risk_profile)
    
    canvas = FigureCanvas(Figure())
    axes = canvas.figure.subplots()

    axes.plot(risk_profile, return_profile, linestyle='dashed')
    axes.set_xlabel('Volatility')
    axes.set_ylabel('Return')
    axes.set_title(title)

    if savefile is not None:
        canvas.print_jpeg(filename_or_obj=savefile)

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        canvas.draw()
        return canvas

def plot_profiles(symbols, profiles, show=True, savefile=None, subtitle=None):
    canvas = FigureCanvas(Figure())

    no_symbols = len(symbols)
    axes = canvas.figure.subplots()

    title ="("
    for symbol in symbols:
        if symbols.index(symbol) != (len(symbols)-1):
            title += symbol +", "
        else:
            title += symbol +') Risk-Return Profile'
            if subtitle is not None:
                title += "\n" + subtitle

    return_profile, risk_profile = [], []
    for profile in profiles:
        return_profile.append(profile['annual_return'])
        risk_profile.append(profile['annual_volatility'])

    axes.plot(risk_profile, return_profile, linestyle='None', marker= ".", markersize=10.0)
    axes.set_xlabel('Volatility')
    axes.set_ylabel('Return')
    axes.set_title(title)

    for i in range(no_symbols):
        axes.annotate(symbols[i], (risk_profile[i], return_profile[i]))

    if savefile is not None:
        canvas.print_jpeg(filename_or_obj=savefile)

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        canvas.draw()
        return canvas


    # TODO: figure out date formatting for x-axis

def plot_moving_averages(symbols, averages_output, periods, show=True, savefile=None):
    averages, dates = averages_output
    canvas = FigureCanvas(Figure())
    axes = canvas.figure.subplots()
    ma1_label, ma2_label, ma3_label = f'MA({periods[0]})', f'MA({periods[1]})', f'MA({periods[2]})'

    if dates is None:
        ma1s, ma2s, ma3s = [], [], []
        for i in range(len(symbols)):
            ma1s.append(averages[i][0])
            ma2s.append(averages[i][1])
            ma3s.append(averages[i][2])
    
        # Bar Chart Variables
        width = formatter.BAR_WIDTH
        x = numpy.arange(len(symbols))

        axes.bar(x + width, ma1s, width, label=ma1_label)
        axes.bar(x, ma2s, width, label=ma2_label)
        axes.bar(x - width, ma3s, width, label=ma3_label)

        axes.set_ylabel('Annual Logarithmic Return')
        axes.set_title('Moving Averages of Annualized Daily Return Grouped By Equity')
        axes.set_xticks(x)
        axes.set_xticklabels(symbols)
        axes.legend()

    else:
 
        for i in range(len(symbols)):
            ma1s, ma2s, ma3s = [], [], []
            ma1_label, ma2_label, ma3_label = f'{symbols[i]}_{ma1_label}', f'{symbols[i]}_{ma2_label}', f'{symbols[i]}_{ma3_label}'
            for j in range(len(dates)):
                MA_1 = averages[i][0][j]
                ma1s.append(MA_1)
                                  
                MA_2 = averages[i][1][j]
                ma2s.append(MA_2)
         
                MA_3 = averages[i][2][j]
                ma3s.append(MA_3)
            
            # TODO: this can probably be integrated into the inner loop above.
            x = [datetime.datetime.strptime(date, '%Y/%M/%d').toordinal() for date in dates]

            start_date, end_date = dates[0], dates[len(dates)-1] 
            title_str = f'Moving Averages of Annualized Return From {start_date} to {end_date}'

            axes.plot(x, ma1s, linestyle="solid", color="darkgreen", label=ma1_label)
            axes.plot(x, ma2s, linestyle="dotted", color="gold", label=ma2_label)
            axes.plot(x, ma3s, linestyle="dashdot", color="orangered", label=ma3_label)

            axes.set_title(title_str)
            axes.set_ylabel('Annualized Logarthmic Return')
            axes.set_xlabel('Dates')
            # instruct matplotlib on how to convert the numbers back into dates for the x-axis
            l = matplotlib.dates.AutoDateLocator()
            f = matplotlib.dates.AutoDateFormatter(l)
            axes.xaxis.set_major_locator(l)
            axes.xaxis.set_major_formatter(f)
        
            axes.legend()

    if savefile is not None:
        canvas.print_jpeg(filename_or_obj=savefile)

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        canvas.draw()
        return canvas

# TODO: figure out date formatting for x-axis
def plot_cashflow(ticker, cashflow, show=True, savefile=None):
    # TODO: print net_present_value somewhere on the graph.
    if not cashflow.beta or not cashflow.alpha or len(cashflow.sample) < 3:
        return False
    else:
        canvas = FigureCanvas(Figure())
        axes = canvas.figure.subplots()

        title_str = f'{ticker} Dividend History Linear Regression Model'

        dividend_history = []
        for date in cashflow.sample:
            # dates.append(date)
            dividend_history.append(cashflow.sample[date])

        linear_model = lambda x: cashflow.alpha + cashflow.beta*x

        # x = [datetime.datetime.strptime(date, '%Y-%m-%d').toordinal() for date in dates]
        # model_map = list(map(linear_model, x))
        model_map = list(map(linear_model, cashflow.time_series))

        axes.scatter(cashflow.time_series, dividend_history, marker=".")
        axes.plot(cashflow.time_series, model_map)

        # instruct matplotlib on how to convert the numbers back into dates for the x-axis
        l = matplotlib.dates.AutoDateLocator()
        f = matplotlib.dates.AutoDateFormatter(l)
        axes.xaxis.set_major_locator(l)
        axes.xaxis.set_major_formatter(f)
        axes.set_title(title_str)
        axes.set_ylabel('Dividend Payment')
        axes.set_xlabel('Dates')

        if savefile is not None:
            canvas.print_jpeg(filename_or_obj=savefile)

        if show:
            s, (width, height) = canvas.print_to_buffer()
            im = Image.frombytes("RGBA", (width, height), s)
            im.show()
        else:
            canvas.draw()
            return canvas