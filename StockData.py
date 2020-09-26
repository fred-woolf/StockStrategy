from indicators import *
from BackTest import *


class StockData:
    def __init__(self, list_of_stock_data_in_df):
        """ stock_data class maintains the collection of raw stock data as well as the calculated values for
            indicators

            :param list self.list_of_stock_data_in_df is a list of dataframes from the raw data in .csv files
            :param list self.list_stock_data_adjusted is the cleaned up set of data from the .csv files
            :param list self.list_candlestick_stock_data has all of the adjusted OHLC data plus candlestick
                data and indicator data
        """

        ''' top-level data format is arranged like this
            list_of_stock_data_in_df:
                - data for each csv file in the directory
                    - data is directly from the .csv file into a dateframe with unlabeled columns:
                    - date, OHLC, volume
                    - data will be cleaned up and put into labeled columns in the dataframe
                        - adjusted date, OHLC, volume, plus indicators
        '''
        self.list_of_stock_data_in_df = list_of_stock_data_in_df
        self.list_stock_data_adjusted = []
        self.list_candlestick_stock_data = []

        self.cleanup_data()
        self.calculate_candlesticks()
        self.calculate_indicators()
        self.execute_strategies()

    # clean up data
    def cleanup_data(self):
        """ Cleans up data by finding non-numeric values and setting them to Nan, adds the column names

            :param col_names list for data sets which don't already have column names
            :param data_columns_list list of column names to assign to df
         """

        for df_element in self.list_of_stock_data_in_df:
            # Date
            col_names = df_element.columns
            if "Date" not in col_names:
                # join columns with date and time into one
                df_element.iloc[:, 0] = df_element.iloc[:, 0].apply(lambda x: x+":")
                df_element.iloc[:, 0] = df_element.iloc[:, 0] + df_element.iloc[:, 1]
                # reformat
                df_element.iloc[:, 0] = pd.to_datetime(df_element.iloc[:, 0], format='%m/%d/%Y:%H:%M')
                df_element = df_element.drop(df_element.columns[1], axis=1)
                # set column names as this data doesn't have any
                df_element.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

            if df_element.Date.isnull().values.any():
                pass
            elif "#" in df_element.Date.values:
                pass

            # coerce to a numeric; errors will get NaN
            data_columns_list = ["Open", "High", "Low", "Close", "Volume"]
            df_element = (df_element.drop(data_columns_list, axis=1)
                          .join(df_element[data_columns_list].apply(pd.to_numeric, errors='coerce')))

            for col_name in data_columns_list:
                # return boolean index series of errors in stock values
                indices_of_errors = np.where(df_element[col_name].isna())[0]

                # fix errors by copying next or previous element
                for i in indices_of_errors:
                    if i == 0:
                        df_element.loc[i, col_name] = df_element.loc[(i+1), col_name]
                    elif i == len(df_element[col_name]):  # index is same as last element
                        df_element.loc[i, col_name] = df_element.loc[(i-1), col_name]
                    else:
                        df_element.loc[i, col_name] = df_element.loc[(i+1), col_name]

            self.list_stock_data_adjusted.append(df_element)

    def calculate_candlesticks(self):
        """ Take the OHLC data and create candlestick data for dislplay
            :param ohlc_data dictionary of Open, High, Low, Close data
            :param dict_candlestick_stock_data dictionary with data elements
            :param hi_day_bounds_above_bar int green candle upper wick length
            :param hi_day_bounds_below_bar int green candle below wick length
            :param lo_day_bounds_above_bar int green candle lower wick length
            :param lo_day_bounds_above_bar int red candle upper wick length
            :param lo_day_bounds_below_bar int red candle lower wick length

        """
        # list_of_candlestick_stock_data has all adjusted data plus indicators for each data file
        #   - each element in the list has data for a separate data file
        #       - each element has dictionary elements:
        #           - candlestick data: calculated data for display on the chart page - each candlestick plus wick data
        #           - OHLC data
        #           - candlestick data

        for stock_data in self.list_stock_data_adjusted:

            ohlc_data = {}
            ohlc_data['Close'] = stock_data['Close']
            ohlc_data['Low'] = stock_data['Low']
            ohlc_data['High'] = stock_data['High']
            ohlc_data['Open'] = stock_data['Open']

            # calculate candlestick plot data
            hi_day = stock_data[stock_data['Open'] < stock_data['Close']]
            lo_day = stock_data[stock_data['Open'] > stock_data['Close']]

            hi_day_bounds_above_bar = hi_day['High'] - hi_day['Close']
            hi_day_bounds_below_bar = hi_day['Open'] - hi_day['Low']

            lo_day_bounds_above_bar = lo_day['High'] - lo_day['Open']
            lo_day_bounds_below_bar = lo_day['Close'] - lo_day['Low']

            dict_candlestick_stock_data = {}
            dict_candlestick_stock_data['lo_day'] = lo_day
            dict_candlestick_stock_data['hi_day'] = hi_day
            dict_candlestick_stock_data['hi_day_bounds_above_bar'] = hi_day_bounds_above_bar
            dict_candlestick_stock_data['hi_day_bounds_below_bar'] = hi_day_bounds_below_bar
            dict_candlestick_stock_data['lo_day_bounds_above_bar'] = lo_day_bounds_above_bar
            dict_candlestick_stock_data['lo_day_bounds_below_bar'] = lo_day_bounds_below_bar

            self.list_candlestick_stock_data.append([ohlc_data, dict_candlestick_stock_data])

    def calculate_indicators(self):
        """ calculate the list of indicators which are of interest for backtesting; each day/minute will have the
            following set of indicators calculated and stored for analysis and plotting

            :param dict_moving_averages dictionary with moving average data for 21, 55, and 89-day averages
            :param dict_stochastics dictionary with stochastics calculated data
            :param dict_williams dictionary with williams %R calculated data
            :param dict_momentum dictionary with momentum calculated data
            :param dict_date_index dictionary with the date index for each set of data
            :param dict_macd dictionary with the MACD calculated data
            :param self.list_candlestick_stock_data will have the following dictionary elements:
                - OHLC data
                - candlestick data
                - moving average data: 21day, 55day, 89day
                - stochastics data: %k and %d
                - Williams %R data
                - momentum data
                - date index
                - MACD data

        """

        # list_of_candlestick_stock_data has all adjusted data plus indicators for each data file
        #   - each element in the list is data for a separate data file plus the indicators
        #       - each element is a dictionary with:
        #           - candlestick data: calculated data for display on the chart page - each candlestick plus wick data
        #           - moving average data: 21day, 55day, 89day
        #           - stochastics data: %k and %d
        #           - Williams %R data
        #           - momentum data
        #           - date index
        #           - OHLC data
        #           - MACD data

        for i in range(0, len(self.list_candlestick_stock_data)):
            dict_moving_averages = {}
            dict_moving_averages['pd_sma_21day'] = moving_average(pd.DataFrame(self.list_stock_data_adjusted[i]['Close']), 21)
            dict_moving_averages['pd_sma_55day'] = moving_average(pd.DataFrame(self.list_stock_data_adjusted[i]['Close']), 55)
            dict_moving_averages['pd_sma_89day'] = moving_average(pd.DataFrame(self.list_stock_data_adjusted[i]['Close']), 89)

            self.list_candlestick_stock_data[i].append(dict_moving_averages)

            # stochastics
            dict_stochastics = {}
            number_of_days_for_lookback = 21
            smoothing = 7
            dict_stochastics['%K'] = stochastic_oscillator_k(self.list_stock_data_adjusted[i], number_of_days_for_lookback)
            dict_stochastics['%D'] = stochastic_oscillator_d(self.list_stock_data_adjusted[i], number_of_days_for_lookback,smoothing)
            self.list_candlestick_stock_data[i].append(dict_stochastics)

            # williams %R
            dict_williams = {}
            number_of_days_for_lookback = 14
            dict_williams["%R"] = williams_R(self.list_stock_data_adjusted[i], number_of_days_for_lookback)
            self.list_candlestick_stock_data[i].append(dict_williams)

            # momentum
            dict_momentum = {}
            number_of_days_for_lookback = 9
            dict_momentum["momentum"] = momentum(self.list_stock_data_adjusted[i], number_of_days_for_lookback)
            self.list_candlestick_stock_data[i].append(dict_momentum)

            # date reference
            dict_date_index = {}
            dict_date_index["date_index"] = self.list_stock_data_adjusted[i]["Date"]
            self.list_candlestick_stock_data[i].append(dict_date_index)

            # MACD
            dict_macd = {}
            number_of_days_for_lookback_fast = 9
            number_of_days_for_lookback_slow = 12
            dict_macd["macd"] = macd(self.list_stock_data_adjusted[i], number_of_days_for_lookback_fast,
                                     number_of_days_for_lookback_slow)
            self.list_candlestick_stock_data[i].append(dict_macd)

        return self.list_candlestick_stock_data

    def execute_strategies(self):
        # for each strategy, see if the indicators initiate a purchase
        for i in range(0, len(self.list_candlestick_stock_data)):
            back_test_strategies = BackTest(self.list_candlestick_stock_data[i])

            back_test_strategies.backtest_strategy_1()

            back_test_strategies.backtest_strategy_2()
