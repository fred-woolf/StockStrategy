""" Stock Strategy Backtest
    Given stock ticker data for minute or daily, use the follwing indicators to test strategies:
           Moving averages, Momentum, Stochastics, MACD, and Williams &R
"""
#
#   Fred W. Woolf
#   version 0.1
#   Initial version
#   09.25.20
#   Required external libraries: tkinter, matplotlib, pandas, os, scipy, math
#
#   TBD:
#       Add labels for plots
#       Add High and Low extensions for candlesticks
#       Verify macd data is correct
#       Add window for results reporting; also write to file
#       Add directory selector
#       Add stock ticker selector
#       Add stock ticker data request from quandl site and notification
#       adapt williams to stochastic init set of data
#
#   version 0.2  09.28.20
#       - Update Strategy 1 and 2
#       - add overall profit for each Strategy after all analysis is run
#   version 0.3  09.28.20
#       - Increase plot size slightly
#   version 0.4  09.28.20
#       - change plot dpi 

import os
import tkinter as tk
from StockData import StockData
import tkinter.font as tkFont
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
from Common import *
import pandas as pd
style.use('ggplot')


LOCATION_OF_DATA_FILES = "./StockMarketData/"  # initially data files are read from local storage


def get_stock_data_files(data_interval):
    """ Get all stock data files (.csv format) in the directory of interest
        - data in csv format
        - initially only IBM

        Parameters:
        -----------
        LOCATION_OF_DATA_FILES: string of current base directory
        data_interval: string: daily or Intraday (minute)
        path_to_data_files:

        Returns:
        --------
        list of files in directory of interest with .csv extension
    """
    path_to_data_files = LOCATION_OF_DATA_FILES
    # choice of daily or minute data
    if data_interval == "daily":
        path_to_data_files = LOCATION_OF_DATA_FILES + "daily/OneYear"

    elif data_interval == "minute":
        path_to_data_files = LOCATION_OF_DATA_FILES + "Intraday/eachDay"

    # find all csv filenames
    location = path_to_data_files
    files_in_dir = []

    # r=>root, d=>directories, f=>files
    for r, d, f in os.walk(location):
        for item in f:
            if '.csv' in item[-4:]:
                files_in_dir.append(os.path.join(r, item))

    for item in files_in_dir:
        print("file in dir: ", item)

    return files_in_dir


class BaseWindow:
    """ This is the class for the Base Window. The Base window will include the data plots for stock market indicators
        and the Stock Ticker textbox.  nitially, data will be read from files; later on, data will be requested from
        stock market data site"""
    def __init__(self, main_window, all_calculated_stock_data: StockData):
        """ init function params:
            :param main_window tk.TK() base window param for display
            :param all_calculated_stock_data list of data which was read from .csv files

            :param self.number_of_plots int  defines the number of plots to be displayed on the main chart page
            :param self.plot_layout int defines the grid pattern for plots
            :param self.topFigure Figure  for the main window
            :param self.canvas1 FigureCanvasTkAgg  the drawing canvas
            The following integers define the locations of plots on the main chart page:
                :param self.candlesticks_plot_number int
                :param self.williams_plot_number int
                :param self.momentum_plot_number int
                :param self.stochastics_plot_number int
                :param self.macd_plot_number int
            The following tkFont types define the helvetica fonts available for the display:
                :param self.helv12_boldtkFont
                :param self.helv12 tkFont
                :param self.helv10_bold tkFont
                :param self.helv10 tkFont
            :param self.width_of_candlestick_bar int defines the width of the candlestick bar on the chart
            :param self.main_frame tk.Frame  frame which holds the main frame which encompasses the main wincdow
            :param self.top_frame tk.Frame  frame which is at the top fo the window and holds the Stock Ticker name
                and buttons
            :param self.chart_frame tk.Frame  frame which holds the data plots
            :param self.textbox_stock_tTicker tk.Entry  textbox which holds the stock ticker symbol
            :param self.button_get_all_stock_data tk.Button  button which initiates drawing of the stock ticker data plots;
                not implemented currently
        """

        self.all_stock_data = all_calculated_stock_data

        # Figure and layout params
        self.topFigure = Figure(figsize=(15, 8), dpi=85)
        self.number_of_plots = 5 * 100
        self.plot_layout = 1 * 10
        self.candlesticks_plot_number = 1
        self.williams_plot_number = 2
        self.momentum_plot_number = 3
        self.stochastics_plot_number = 4
        self.macd_plot_number = 5
        self.width_of_candlestick_bar = 0.88

        # Subplots for each indicator type
        # Use layout designations to add chart subplots
        self.stock_chart_subplot = self.topFigure.add_subplot(
            self.number_of_plots + self.plot_layout + self.candlesticks_plot_number)
        self.williams_ChartSubplot = self.topFigure.add_subplot(
            self.number_of_plots + self.plot_layout + self.williams_plot_number)
        self.macd_ChartSubplot = self.topFigure.add_subplot(
            self.number_of_plots + self.plot_layout + self.macd_plot_number)
        self.momentum_ChartSubplot = self.topFigure.add_subplot(
            self.number_of_plots + self.plot_layout + self.momentum_plot_number)
        self.stochastics_ChartSubplot = self.topFigure.add_subplot(
            self.number_of_plots + self.plot_layout + self.stochastics_plot_number)

        self.helv12_bold = tkFont.Font(family='Helvetica', size=12, weight='bold')
        self.helv12 = tkFont.Font(family='Helvetica', size=12)
        self.helv10_bold = tkFont.Font(family='Helvetica', size=10, weight='bold')
        self.helv10 = tkFont.Font(family='Helvetica', size=10)
        self.main_frame = tk.Frame(main_window, width=1100, height=500, bg='white')
        self.main_frame.grid(column=0, row=0, sticky="nsew")

        # add top frame into main frame
        self.top_frame = tk.Frame(self.main_frame, width=1550, height=20, bg="gainsboro", borderwidth=5, relief=RIDGE)
        self.top_frame.grid(column=0, row=0, sticky=W + E)

        # add stock ticker entry box into top frame
        self.var_stock_ticker = tk.StringVar(self.top_frame, "IBM")
        self.textbox_stock_tTicker = tk.Entry(self.top_frame, width=15, textvariable=self.var_stock_ticker,
                                              font=self.helv12)
        self.textbox_stock_tTicker.grid(column=0, row=0, sticky="NW", padx=(20, 0), pady=(10, 5))

        # add button to initiate stock data retrieval and display to the top frame; not currently implemented
        self.button_get_stock_data = tk.Button(self.top_frame,
                                               text="Get Stock Data",
                                               fg="black",
                                               command=self.submit_contact_draw_stock_data_plots,
                                               font=self.helv12_bold)
        self.button_get_stock_data.grid(column=1, row=0, sticky="NW", padx=(20, 0), pady=(10, 0))
        self.button_get_stock_data.state = "disabled"   # disabled for now

        # add the chart frame to the main frame
        self.chart_frame = tk.Frame(self.main_frame, width=1200, height=720, bg="gainsboro", borderwidth=5, relief=RIDGE)
        self.chart_frame.grid_propagate(False)
        self.chart_frame.grid(column=0, row=2, columnspan=2, sticky=E+W+N+S, padx=(0, 0), pady=(0, 0))

        # set column and row figure params
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        self.chart_frame.rowconfigure(0, weight=1)
        self.chart_frame.columnconfigure(0, weight=1)

        # set up drawing canvas and toolbar
        self.canvas1 = FigureCanvasTkAgg(self.topFigure, master=self.chart_frame)
        self.canvas1.get_tk_widget().grid(column=0, row=1, sticky=E+W+N+S)
        toolbar1 = NavigationToolbar2Tk(self.canvas1, self.chart_frame)
        toolbar1.grid(column=0, row=0)

        # since button is not implemented, automatically draw chart
        self.submit_contact_draw_stock_data_plots()

    def submit_contact_draw_stock_data_plots(self):
        """ process the drawing of the stock indicator charts """
        ax1, ax2, ax3, ax4, ax5 = self.topFigure.get_axes()
        ax1.get_shared_x_axes().join(ax1, ax2, ax3, ax4, ax5)

        self.plot_candlesticks()
        self.plot_williams_r()
        self.plot_momentum()
        self.plot_stochastics()
        self.plot_macd()

    def plot_candlesticks(self):
        """ For the candlestick charts, draw each candlestick in the appropriate color, given the calculated bar size
            and the color - green for positive day/minute, red for negative day/minute

        :param index_offset list holds length of each data set from the .csv files
        :param this_offset list holds offset for each successive set of data
        :param hi_day pd.Dataframe  holds the set of OHLC data for candlestick bars which are positive
        :param lo_day pd.Dataframe  holds the set of OHLC data for candlestick bars which are negative

        :return: None
        """
        # Concatenate the data from all files in the directory to create a single plot which covers the date range
        index_offset = []
        this_offset = 0
        candles_data = self.all_stock_data.list_candlestick_stock_data
        for i in range(0, len(candles_data)):
            hi_day = candles_data[i][CommonDefs.INDEX_OF_CANDLESTICK_PLOT_DATA]["hi_day"]
            lo_day = candles_data[i][CommonDefs.INDEX_OF_CANDLESTICK_PLOT_DATA]["lo_day"]

            # make the indices sequential by incrementing by previous number of data points
            if i == 0:
                index_offset.append(len(candles_data[i][CommonDefs.INDEX_OF_OHLC_DATA]['Close'].index))
                index = [x for x in candles_data[i]
                         [CommonDefs.INDEX_OF_OHLC_DATA]['Close'].index]
            else:
                this_offset = this_offset + len(candles_data[i-1][CommonDefs.INDEX_OF_OHLC_DATA]['Close'].index)
                index = [x + this_offset for x in candles_data[i]
                            [CommonDefs.INDEX_OF_OHLC_DATA]['Close'].index]

            # add MA plots; use sequential index
            ma_21d_data = candles_data[i][CommonDefs.INDEX_OF_OHLC_DATA] \
                            ['Close'].rolling(window=21, min_periods=21).mean()
            ma_55_data = candles_data[i][CommonDefs.INDEX_OF_OHLC_DATA] \
                            ['Close'].rolling(window=55, min_periods=55).mean()
            ma_89_data = candles_data[i][CommonDefs.INDEX_OF_OHLC_DATA] \
                                            ['Close'].rolling(window=89, min_periods=89).mean()
            self.stock_chart_subplot.plot(index, ma_21d_data, color='red')
            self.stock_chart_subplot.plot(index, ma_55_data, color='yellow')
            self.stock_chart_subplot.plot(index, ma_89_data, color='green')

            # add Candlestick bars
            # up day/minute
            index = [x + this_offset for x in hi_day['Close'].index]
            self.stock_chart_subplot.bar(index, hi_day['Close'] - hi_day['Open'],
                                         bottom=hi_day['Open'], width=self.width_of_candlestick_bar, color='green')
            # down day/minute
            index = [x + this_offset for x in lo_day['Close'].index]
            self.stock_chart_subplot.bar(index, lo_day['Open'] - lo_day['Close'],
                                         bottom=lo_day['Close'], width=self.width_of_candlestick_bar, color='red')

    def plot_williams_r(self):
        """ plot the Williams %R as a series, with a sequential index which covers the entire data range

            :param index_len int which has the number of stock ticker data sets - one per file
            :param williams_data list of all williams_data for the data sets
        """
        index_len = 0
        for i in range(len(self.all_stock_data.list_candlestick_stock_data)):
            williams_data = self.all_stock_data.list_candlestick_stock_data[i][CommonDefs.INDEX_OF_WILLIAMS_DATA]['%R']

            # make sequential index across all data sets
            index = [x + index_len for x in williams_data.index]
            self.williams_ChartSubplot.plot(index, williams_data, color='green')
            index_len = index_len + len(index)

    def plot_momentum(self):
        """ plot the Momentum as a series, with a sequential index which covers the entire data range

            :param index_len int which has the number of stock ticker data sets - one per file
            :param momentum_data list of all momentum_data for the data sets
        """
        index_len = 0
        for i in range(len(self.all_stock_data.list_candlestick_stock_data)):
            momentum_data = self.all_stock_data.list_candlestick_stock_data[i][CommonDefs.INDEX_OF_MOMENTUM_DATA]['momentum']

            # make sequential index across all data sets
            index = [x + index_len for x in momentum_data.index]
            self.momentum_ChartSubplot.plot(index, momentum_data, color='blue')
            index_len = index_len + len(index)

    def plot_stochastics(self):
        """ plot the stochastics %K and %D as series, with a sequential index which covers the entire data range

            :param index_len int which has the number of stock ticker data sets - one per file
            :param stoch_k_data list of all stoch_k_data for the data sets
            :param stoch_d_data list of all stoch_d_data for the data sets
        """
        index_len = 0
        for i in range(len(self.all_stock_data.list_candlestick_stock_data)):
            stoch_k_data = self.all_stock_data.list_candlestick_stock_data[i][CommonDefs.INDEX_OF_STOCHASTICS_DATA]['%K']
            stoch_d_data = self.all_stock_data.list_candlestick_stock_data[i][CommonDefs.INDEX_OF_STOCHASTICS_DATA]['%D']

            # make sequential index across all data sets
            index = [x + index_len for x in stoch_k_data.index]
            self.stochastics_ChartSubplot.plot(index, stoch_k_data, color='gray')
            index = [x + index_len for x in stoch_d_data.index]
            self.stochastics_ChartSubplot.plot(index, stoch_d_data, color='orange')
            index_len = index_len + len(index)

    def plot_macd(self):
        """ plot the MACD and MACD signal as a series, with a sequential index which covers the entire data range

            :param index_len int which has the number of stock ticker data sets - one per file
            :param macd_data list of all macd data for the data sets
            :param macd_data_signal list of all macd_signal_data for the data sets
        """
        index_len = 0
        for i in range(len(self.all_stock_data.list_candlestick_stock_data)):
            macd_data = self.all_stock_data.list_candlestick_stock_data[i] \
                                [CommonDefs.INDEX_OF_MACD_DATA]["macd"]['MACD_12_26']
            macd_data_signal = self.all_stock_data.list_candlestick_stock_data[i] \
                                [CommonDefs.INDEX_OF_MACD_DATA]["macd"]["MACDsign_12_26"]

            # make sequential index across all data sets
            index = [x + index_len for x in macd_data_signal.index]
            self.macd_ChartSubplot.plot(index, macd_data_signal, color='blue')
            index = [x + index_len for x in macd_data_signal.index]
            self.macd_ChartSubplot.plot(index, macd_data, color='red')
            index_len = index_len + len(index)


if __name__ == "__main__":
    #get filenames for all.csv files in the directory of interest
    stock_data_files = get_stock_data_files("minute")  # minute or daily data

    # put data in list in pandas frame
    list_all_stock_data_in_df = []
    for filename in stock_data_files:
        df_all_data = pd.read_csv(filename)  # one day of data
        list_all_stock_data_in_df.append(df_all_data)

    # for the list of all stock data for each file, calculate all indicators and run the backtest strategies
    # in preparation for display of the data
    # AllStockData has the list of all raw and and calculated stock market data and indicators
    AllStockData = StockData(list_all_stock_data_in_df)

    # main window
    win = tk.Tk()
    win.title("Stock Data BackTest Analysis")
    win.resizable(False, False)

    app = BaseWindow(win, AllStockData)
    win.mainloop()
