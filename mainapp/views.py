from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .models import Portfolio, User, Profile, DailyWorth
from django.contrib.auth.decorators import login_required
from yahoo_fin import stock_info as si
import yfinance as yf
import json
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import Dropdown
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure, show, output_file, save
from bokeh.io import output_notebook

from bokeh.models import BooleanFilter, CDSView, Select, Range1d, HoverTool
from bokeh.palettes import Category20
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.embed import components, json_item

from eventregistry import *
from django.core.exceptions import ObjectDoesNotExist






# @csrf_protect
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('homepage')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Create your views here.
def landingpage(request):
    return render(request, "landing.html")

@login_required
def homepage(request):
    current_user = request.user
    user = Profile.objects.get(user = current_user)
    if request.user.is_authenticated:
        return render(request, "homepage.html", {'user': user})

def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user.profile.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
    user.save()


@login_required
def playground(request):
    current_user = request.user
    if request.user.is_authenticated:

        stock_list = ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI"]
        stock_and_prices = {}
        for stock in stock_list:
            price = si.get_live_price(stock)
                
            stock_and_prices[stock] = {'price': price}
        
        user = Profile.objects.get(user = current_user)
        if request.method == "GET":
            all_portfolios_of_current_users = Portfolio.objects.filter(user = user)
            return render(request,'playground.html',{'stock_and_prices': stock_and_prices, 'user': user, "all_portfolios_of_current_users": all_portfolios_of_current_users })
        if request.method == 'POST':    
            stock_purchased = request.POST.dict()
            total_sum = 0
            # individual_port= Portfolio.objects.get_or_create(user = user)
            user_portfolios = Portfolio.objects.get(user = user)
            for key, value in stock_purchased.items():
                if key == 'csrfmiddlewaretoken':
                    continue
                else:
                    if value != '':
                        try:
                            individual_port= Portfolio.objects.get(user = user, stock= key)
                        except ObjectDoesNotExist:
                            new_portfolio = Portfolio(user = user, stock = key, number = int(value))
                            new_portfolio.save()
                            continue
                        
                            
                        
                        individual_port.number += int(value)
                        individual_port.save()
                        price = stock_and_prices[key]['price']
                        total_sum += price*int(value)

                    else:
                        continue
            # individual_port.save()
            current_budget = float(user.current_budget) - total_sum
            # portfolio = Portfolio.objects.get(user= user)
            user.current_budget = current_budget
            
            all_portfolios_of_current_users = Portfolio.objects.filter(user = user)
            user.save()
            portfolio.save()
            message = 'you have spent $'+ str(total_sum)
            
            return render(request,'playground.html',{'stock_and_prices': stock_and_prices, 'user':user, 'message': message, "all_portfolios_of_current_users": all_portfolios_of_current_users })
    else:
        return redirect(landingpage)


def dashboard(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        # Get Stock DataFrame
        # msft = yf.Ticker("MSFT")
        msft = yf.Ticker(symbol)
        hist = msft.history(period='max')

        # Define constants
        W_PLOT = 1000
        H_PLOT = 400
        TOOLS = 'pan,wheel_zoom,hover,reset'

        VBAR_WIDTH = 0.2
        RED = Category20[7][6]
        GREEN = Category20[5][4]

        BLUE = Category20[3][0]
        BLUE_LIGHT = Category20[3][1]

        ORANGE = Category20[3][2]
        PURPLE = Category20[9][8]
        BROWN = Category20[11][10]

        def get_symbol_df(symbol=None):
            df = pd.DataFrame(hist)[-50:]
            df.reset_index(inplace=True)
            df["Date"] = pd.to_datetime(df["Date"])
            return df

        def plot_stock_price(stock):
        
            p = figure(plot_width=W_PLOT, plot_height=H_PLOT, tools=TOOLS,
                    title="Stock price", toolbar_location='above')

            inc = stock.data['Close'] > stock.data['Open']
            dec = stock.data['Open'] > stock.data['Close']
            view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
            view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

            # map dataframe indices to date strings and use as label overrides
            p.xaxis.major_label_overrides = {i+int(stock.data['index'][0]): date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(stock.data["Date"]))}
            p.xaxis.bounds = (stock.data['index'][0], stock.data['index'][-1])


            p.segment(x0='index', x1='index', y0='Low', y1='High', color=RED, source=stock, view=view_inc)
            p.segment(x0='index', x1='index', y0='Low', y1='High', color=GREEN, source=stock, view=view_dec)

            p.vbar(x='index', width=VBAR_WIDTH, top='Open', bottom='Close', fill_color=BLUE, line_color=BLUE,source=stock,view=view_inc, name="price")
            p.vbar(x='index', width=VBAR_WIDTH, top='Open', bottom='Close', fill_color=RED, line_color=RED,source=stock,view=view_dec, name="price")

            p.legend.location = "top_left"
            p.legend.border_line_alpha = 0
            p.legend.background_fill_alpha = 0
            p.legend.click_policy = "mute"

            p.yaxis.formatter = NumeralTickFormatter(format='$ 0,0[.]000')
            p.x_range.range_padding = 0.05
            p.xaxis.ticker.desired_num_ticks = 40
            p.xaxis.major_label_orientation = 3.14/4
            
            # Select specific tool for the plot
            price_hover = p.select(dict(type=HoverTool))

            # Choose, which glyphs are active by glyph name
            price_hover.names = ["price"]
            # Creating tooltips
            price_hover.tooltips = [("Datetime", "@Date{%Y-%m-%d}"),
                                    ("Open", "@Open{$0,0.00}"),
                                    ("Close", "@Close{$0,0.00}"),("Volume", "@Volume{($ 0.00 a)}")]
            price_hover.formatters={"Date": 'datetime'}

            return p

        
        stock = ColumnDataSource(data=dict(Date=[], Open=[], Close=[], High=[], Low=[],index=[]))
        df = get_symbol_df(symbol)
        stock.data = stock.from_df(df)
        elements = list()

        # update_plot()
        p_stock = plot_stock_price(stock)

        elements.append(p_stock)

        curdoc().add_root(column(elements))
        curdoc().title = 'Bokeh stocks historical prices'

        #show(p_stock)

        script, div = components(p_stock)
        kwargs = {'script': script, 'div': div}

        stock_list = ["MSFT", "AAPL"]
        er = EventRegistry(apiKey = '3a7a023b-6280-4476-bec0-5c9ff41770bd')
        q = QueryArticlesIter(
            keywords = QueryItems.OR(stock_list),
            dataType = ["news"],
            lang = 'eng'
        )
        news_list = q.execQuery(er, sortBy = ["rel","date","sourceImportance"], maxItems = 5, )

        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/get-detail"

        querystring = {"region":"US","lang":"en","symbol":symbol}

        headers = {
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
            'x-rapidapi-key': "ff4cff81d5msh596a92309f2f43ap13412cjsn002bc2a74b4d"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        json_dict  = json.loads(response.text)


        for key in json_dict.keys():
            if key == "summaryDetail":
                try:
                    stock_close = json_dict[key]['previousClose']['raw']
                except KeyError:
                    stock_close = ''
                    
                try:
                    stock_open = json_dict[key]['open']['raw']
                except KeyError:
                    stock_open = ''
                try:
                    stock_bid = json_dict[key]['bid']['raw']
                except KeyError:
                    stock_bid = ''
                try:
                    stock_ask = json_dict[key]['ask']['raw']
                except KeyError:
                    stock_ask = ''
                try:
                    stock_volume = json_dict[key]['volume']['fmt']
                except KeyError:
                    stock_volume = ''
                try:
                    stock_averageVolume = json_dict[key]['averageVolume']['fmt']
                except KeyError:
                    stock_averageVolume = ''
                try:
                    stock_marketCap = json_dict[key]['marketCap']['fmt']    
                except KeyError:  
                    stock_marketCap = ''
            if key == "defaultKeyStatistics":
                try:
                    stock_weekChange = json_dict[key]['52WeekChange']['fmt']
                except KeyError:
                    stock_weekChange = ''
                try:
                    stock_beta = json_dict[key]['beta']['fmt']
                except KeyError:
                    stock_beta = ''
                try:
                    stock_EPS = json_dict[key]['trailingEps']['raw']
                except KeyError:
                    stock_EPS = ''
                try:
                    stock_PE = json_dict[key]['forwardPE']['fmt']
                except KeyError:
                    stock_PE = ''

        return render(request, 'dashboard.html', {**kwargs, 'news_list' : news_list,'stock_close':stock_close,'stock_open':stock_open,'stock_bid':stock_bid,'stock_ask':stock_ask,'stock_volume':stock_volume,'stock_averageVolume':stock_averageVolume,'stock_marketCap':stock_marketCap,'stock_weekChange':stock_weekChange,'stock_beta':stock_beta,'stock_EPS':stock_EPS,'stock_PE':stock_PE,'stock_list':stock_list,'symbol':symbol}) 
    else:
        symbol = 'MSFT'
        stock_list = ["MSFT", "AAPL"]

        msft = yf.Ticker(symbol)
        hist = msft.history(period='max')

        # Define constants
        W_PLOT = 1000
        H_PLOT = 400
        TOOLS = 'pan,wheel_zoom,hover,reset'

        VBAR_WIDTH = 0.2
        RED = Category20[7][6]
        GREEN = Category20[5][4]

        BLUE = Category20[3][0]
        BLUE_LIGHT = Category20[3][1]

        ORANGE = Category20[3][2]
        PURPLE = Category20[9][8]
        BROWN = Category20[11][10]

        def get_symbol_df(symbol=None):
            df = pd.DataFrame(hist)[-50:]
            df.reset_index(inplace=True)
            df["Date"] = pd.to_datetime(df["Date"])
            return df

        def plot_stock_price(stock):
        
            p = figure(plot_width=W_PLOT, plot_height=H_PLOT, tools=TOOLS,
                    title="Stock price", toolbar_location='above')

            inc = stock.data['Close'] > stock.data['Open']
            dec = stock.data['Open'] > stock.data['Close']
            view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
            view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

            # map dataframe indices to date strings and use as label overrides
            p.xaxis.major_label_overrides = {i+int(stock.data['index'][0]): date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(stock.data["Date"]))}
            p.xaxis.bounds = (stock.data['index'][0], stock.data['index'][-1])


            p.segment(x0='index', x1='index', y0='Low', y1='High', color=RED, source=stock, view=view_inc)
            p.segment(x0='index', x1='index', y0='Low', y1='High', color=GREEN, source=stock, view=view_dec)

            p.vbar(x='index', width=VBAR_WIDTH, top='Open', bottom='Close', fill_color=BLUE, line_color=BLUE,source=stock,view=view_inc, name="price")
            p.vbar(x='index', width=VBAR_WIDTH, top='Open', bottom='Close', fill_color=RED, line_color=RED,source=stock,view=view_dec, name="price")

            p.legend.location = "top_left"
            p.legend.border_line_alpha = 0
            p.legend.background_fill_alpha = 0
            p.legend.click_policy = "mute"

            p.yaxis.formatter = NumeralTickFormatter(format='$ 0,0[.]000')
            p.x_range.range_padding = 0.05
            p.xaxis.ticker.desired_num_ticks = 40
            p.xaxis.major_label_orientation = 3.14/4
            
            # Select specific tool for the plot
            price_hover = p.select(dict(type=HoverTool))

            # Choose, which glyphs are active by glyph name
            price_hover.names = ["price"]
            # Creating tooltips
            price_hover.tooltips = [("Datetime", "@Date{%Y-%m-%d}"),
                                    ("Open", "@Open{$0,0.00}"),
                                    ("Close", "@Close{$0,0.00}"),("Volume", "@Volume{($ 0.00 a)}")]
            price_hover.formatters={"Date": 'datetime'}

            return p

        
        stock = ColumnDataSource(data=dict(Date=[], Open=[], Close=[], High=[], Low=[],index=[]))
        df = get_symbol_df(symbol)
        stock.data = stock.from_df(df)
        elements = list()

        # update_plot()
        p_stock = plot_stock_price(stock)

        elements.append(p_stock)

        curdoc().add_root(column(elements))
        curdoc().title = 'Bokeh stocks historical prices'

        #show(p_stock)

        script, div = components(p_stock)
        kwargs = {'script': script, 'div': div}

        stock_list = ["MSFT", "AAPL"]
        er = EventRegistry(apiKey = '3a7a023b-6280-4476-bec0-5c9ff41770bd')
        q = QueryArticlesIter(
            keywords = QueryItems.OR(stock_list),
            dataType = ["news"],
            lang = 'eng'
        )
        news_list = q.execQuery(er, sortBy = ["rel","date","sourceImportance"], maxItems = 5, )

        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/get-detail"

        querystring = {"region":"US","lang":"en","symbol":symbol}

        headers = {
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
            'x-rapidapi-key': "ff4cff81d5msh596a92309f2f43ap13412cjsn002bc2a74b4d"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        json_dict  = json.loads(response.text)


        for key in json_dict.keys():
            if key == "summaryDetail":
                try:
                    stock_close = json_dict[key]['previousClose']['raw']
                except KeyError:
                    stock_close = ''
                    
                try:
                    stock_open = json_dict[key]['open']['raw']
                except KeyError:
                    stock_open = ''
                try:
                    stock_bid = json_dict[key]['bid']['raw']
                except KeyError:
                    stock_bid = ''
                try:
                    stock_ask = json_dict[key]['ask']['raw']
                except KeyError:
                    stock_ask = ''
                try:
                    stock_volume = json_dict[key]['volume']['fmt']
                except KeyError:
                    stock_volume = ''
                try:
                    stock_averageVolume = json_dict[key]['averageVolume']['fmt']
                except KeyError:
                    stock_averageVolume = ''
                try:
                    stock_marketCap = json_dict[key]['marketCap']['fmt']    
                except KeyError:  
                    stock_marketCap = ''
            if key == "defaultKeyStatistics":
                try:
                    stock_weekChange = json_dict[key]['52WeekChange']['fmt']
                except KeyError:
                    stock_weekChange = ''
                try:
                    stock_beta = json_dict[key]['beta']['fmt']
                except KeyError:
                    stock_beta = ''
                try:
                    stock_EPS = json_dict[key]['trailingEps']['raw']
                except KeyError:
                    stock_EPS = ''
                try:
                    stock_PE = json_dict[key]['forwardPE']['fmt']
                except KeyError:
                    stock_PE = ''

        return render(request, 'dashboard.html', {**kwargs, 'news_list' : news_list,'stock_close':stock_close,'stock_open':stock_open,'stock_bid':stock_bid,'stock_ask':stock_ask,'stock_volume':stock_volume,'stock_averageVolume':stock_averageVolume,'stock_marketCap':stock_marketCap,'stock_weekChange':stock_weekChange,'stock_beta':stock_beta,'stock_EPS':stock_EPS,'stock_PE':stock_PE,'stock_list':stock_list,'symbol':symbol}) 

    #return render(request, 'dashboard.html',{'stock_list':stock_list})
       
@login_required
def register(request):
    return render(request, "register.html")
    
@login_required
def risk(request):
    if request.method == "POST":
        currentBudget = request.POST.get('monthlyIncome')
        riskTolerance = 0
        if 1000 <= int(currentBudget) and  int(currentBudget) <= 3000:
            riskTolerance = 0.5 
        elif 3000 < int(currentBudget) and  int(currentBudget) <= 6000:
            riskTolerance = 1.5
        elif 6000 < int(currentBudget) and  int(currentBudget) <= 10000:
            riskTolerance = 2.5
        elif int(currentBudget) > 10000:
            riskTolerance = 3.5
        current_user = request.user
        user = Profile.objects.get(user = current_user)
        user.current_budget = currentBudget
        user.save()
        
        return render(request, 'risk.html', {'riskTolerance': riskTolerance})
    else: 
        return render(request, 'register.html')