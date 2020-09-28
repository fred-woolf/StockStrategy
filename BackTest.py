from Common import *
from scipy import stats
import math

class BackTest:
    def __init__(self, df):
        """ For the set of candlestick data which has indicators already calculated,
            prepare data points to run Backtest scenarios as requested

            :param self.candlestick:_dataframe of data to run backtest on
            :param self.data_points: dictionary of items which are available for backtest analylsis
            :param self.days_to_skip: int the number of days to skip - longest set of minimum days across the indicators

         """
        self.candlestick_data = df
        self.data_points = {}
        self.days_to_skip = 89  # 89d MA
        number_of_data_points = 0

        self.get_data_points()

    def backtest_strategy_1(self):
        """ backtest strategy 2
                :param own_short: boolean:
                :param trailing_stop_init: int initial value of trailing stop
                :param trailing_stop: int:
                :param sell_position: boolean
                :param purchase_price: int
                :param slope_macd: int
                :param min_data_points_for_macd: int
                :param winners: int total number of winning trades
                :param losers: int: total number losing trades
                :param pd_close_data: series self.candlestick_data[CommonDefs.INDEX_OF_OHLC_DATA]["Close"]
                :param profit: int
                :param williams_entry_point: int
                :param momentum_entry_point: int
                :param slope_momentum_entry_point: int
                :param stochastics_d_entry_point: int
        """

        # short strategy:
        # when Williams %R below -75
        # and momentum is crossing, or has just crossed below 0.05
        # and stochastics signal is below 60
        # and macd < macd_signal
        # and slope < 0.0025
        print(" \n\n************************************** BackTest Strategy 1 **************************************")
        own_short = False
        lowest_price_after_purchase = 0
        trailing_stop_init = 0.55
        trailing_stop = 0
        sell_position = False
        purchase_price = 0
        slope_macd = 0
        min_data_points_for_calculations = 26 + 5 + 1# 18 for macd min span
        min_data_points_for_macd = 5
        williams_entry_point = -75
        momentum_entry_point = 0.05
        stochastics_d_entry_point = 60
        slope_macd_entry_point = 0.0025
        slope_macd_exit_point = 0.0011
        convert_to_dollars = 100
        winners = 0
        losers = 0
        pd_close_data = self.data_points['Close_Data']
        number_of_data_points = len(self.data_points["momentum_data"])
        profit = 0
        for i in range(min_data_points_for_calculations + min_data_points_for_macd, number_of_data_points):
            slope_macd = self.calculate_slope_of_line(self.data_points["macd"], i - min_data_points_for_macd , i)

            if own_short is False and i > min_data_points_for_macd:
                if self.data_points["williams_data"][i] <= williams_entry_point and \
                    self.data_points["momentum_data"][i] <= momentum_entry_point and \
                    self.data_points["stochastics_data_d"][i] <= stochastics_d_entry_point and \
                    self.data_points["macd"][i]  < self.data_points["macd_signal"][i] and \
                    slope_macd < slope_macd_entry_point:
                        own_short = True
                        purchase_price = pd_close_data[i]
                        print("date: " + str(self.data_points["date_index"][i]) + " purchase at " +
                              str(purchase_price))
                        trailing_stop = purchase_price + trailing_stop_init
                        lowest_price_after_purchase = purchase_price
            else:
                if own_short is True:
                    slope_macd = self.calculate_slope_of_line(self.data_points["macd"], i - min_data_points_for_macd, i)

                    if slope_macd > slope_macd_exit_point:
                        # get slope of MACD signal; when it changes polarity, tighten the trailing stop position
                        sell_position = True

                    # reset trailing stop
                    if pd_close_data[i] < lowest_price_after_purchase:
                        lowest_price_after_purchase = pd_close_data[i-1]
                        trailing_stop = lowest_price_after_purchase + trailing_stop_init

                    if pd_close_data[i] > trailing_stop:
                        sell_position = True

                    if sell_position:
                        print("   sell position: ", self.data_points["date_index"][i], " i = ", i,
                              "price above trailing stop: ", pd_close_data[i], " > ", trailing_stop)
                        own_short = False
                        profit = profit + (purchase_price - pd_close_data[i]) * convert_to_dollars
                        if (purchase_price - pd_close_data[i]) > 0:
                            winners = winners + 1
                        else:
                            losers = losers + 1

                        trailing_stop = 0
                        sell_position = False
                        lowest_price_after_purchase = 0

                        print("   date: " + str(self.data_points["date_index"][i]) + "  sell at " +
                              str(pd_close_data[i]) + " profit = " + str((purchase_price - pd_close_data[i]) *
                                                                         convert_to_dollars))
        print(" total profit = " + str(profit) + " winners: " + str(winners) + "  losers: " + str(losers))

        return profit

    def backtest_strategy_2(self):
        """ backtest strategy 2
                :param own_short boolean: boolean
                :param trailing_stop_init: int initial value of trailing stop
                :param trailing_stop: int
                :param sell_position: boolean
                :param purchase_price: int
                :param slope_macd: int
                :param min_data_points_for_line: int
                :param winners: int total number of winning trades
                :param losers: int total number losing trades
                :param pd_close_data: series self.candlestick_data[CommonDefs.INDEX_OF_OHLC_DATA]["Close"]
                :param profit: int
                :param williams_entry_point: int
                :param momentum_entry_point: int
                :param slope_momentum_entry_point: int
                :param stochastics_d_entry_point: int
        """
        print("\n************************************** BackTest Strategy 2 ************************************")
        # short strategy:
        # when Williams %R below -75
        # and momentum is crossing, or has crossed below 0.05
        # and stochastics signal is <= 60
        # and macd < macd_signal
        own_short = False
        purchase_price = 0
        trailing_stop_init = 0.45
        lowest_price_after_purchase = 0
        trailing_stop = 0
        sell_position = False
        min_data_points_for_line = 9
        min_data_points_for_calculations = 26 + min_data_points_for_line #  26 for macd min span + min points for line
        williams_entry_point = -75
        momentum_entry_point = 0.05
        stochastics_d_entry_point = 60
        slope_macd_entry_point = -0.005
        slope_macd_exit_point = 0.0015
        slope_momentum_entry_point = 0.0
        convert_to_dollars = 100
        winners = 0
        losers = 0
        pd_close_data = self.data_points['Close_Data']
        number_of_data_points = len(self.data_points["momentum_data"])
        profit = 0
        for i in range(min_data_points_for_calculations + min_data_points_for_line, number_of_data_points):
            slope_macd = self.calculate_slope_of_line(self.data_points["macd"], i - min_data_points_for_line , i)
            slope_macd_signal = self.calculate_slope_of_line(self.data_points["macd_signal"],
                                                             i - min_data_points_for_line, i)
            slope_momentum = self.calculate_slope_of_line(self.data_points["macd_signal"],
                                                          i - min_data_points_for_line + 1, i)

            if own_short is False and i > min_data_points_for_calculations and \
                    not math.isnan(self.data_points["ma_data_55d"][i]):
                if self.data_points["williams_data"][i] <= williams_entry_point and \
                        self.data_points["momentum_data"][i] <= momentum_entry_point and \
                        self.data_points["stochastics_data_d"][i] <= stochastics_d_entry_point and \
                        self.data_points["macd"][i] < self.data_points["macd_signal"][i] and \
                        slope_macd < slope_macd_entry_point and \
                        slope_momentum < slope_momentum_entry_point:

                    own_short = True
                    purchase_price = pd_close_data[i]
                    print("**date: " + str(self.data_points["date_index"][i]) + " purchase at " +
                          str(purchase_price))
                    print("     open position slope_MACD_signal = ", slope_macd_signal, "slope_MACD = ",
                          slope_macd, " close price = ", pd_close_data[i])
                    lowest_price_after_purchase = purchase_price
                    trailing_stop = purchase_price + trailing_stop_init
            else:
                if own_short is True:  #check for exit
                    ma_data_21d = self.data_points["ma_data_21d"]
                    ma_data_55d = self.data_points["ma_data_55d"]

                    if not math.isnan(ma_data_21d[i]) and not math.isnan(ma_data_55d[i]):
                        if ma_data_21d[i] >= ma_data_55d[i] or pd_close_data[i] > self.data_points["ma_data_21d"][i]:
                            print(" close position 21dMA = ", ma_data_21d[i], "55dMA = ", ma_data_55d[i],
                                  "  close price = ", pd_close_data[i])
                            sell_position = True
                        if slope_macd_signal > slope_macd_exit_point:
                            print (" close position slope_MACD_signal = ", slope_macd_signal, "slope_MACD = ",
                                  slope_macd, " close price = ", pd_close_data[i])
                            sell_position = True

                    if pd_close_data[i] > trailing_stop:
                        print(" close position on trailing stop: close ", pd_close_data[i], " > ", trailing_stop)
                        print(    "slope_MACD_signal = ", slope_macd_signal, " slope_MACD = ", slope_macd)
                        sell_position = True

                    # reset trailing stop
                    if pd_close_data[i] < lowest_price_after_purchase:
                        lowest_price_after_purchase = pd_close_data[i]
                        trailing_stop = lowest_price_after_purchase + trailing_stop_init

                    if sell_position:
                        print("   sell position: ", self.data_points["date_index"][i], " i =", i,
                              " price: ", pd_close_data[i], " trailing stop: ", trailing_stop)
                        own_short = False
                        profit = profit + (purchase_price - pd_close_data[i]) * convert_to_dollars
                        if (purchase_price - pd_close_data[i]) > 0:
                            winners = winners + 1
                        else:
                            losers = losers + 1

                        lowest_price_after_purchase = 0
                        trailing_stop = 0
                        sell_position = False

                        print("   date: " + str(
                            self.data_points["date_index"][i]) + "  sell at " + str(
                            pd_close_data[i]) + " profit = " + str((purchase_price - pd_close_data[i]) *
                                                                   convert_to_dollars))

        print(" total profit = " + str(profit) + " winners: " + str(winners) + "  losers: " + str(losers))
        return profit

    def get_data_points(self):
        self.data_points["date_index"] = self.candlestick_data[CommonDefs.INDEX_OF_DATE_INDEX]["date_index"]
        number_of_data_points = 0
        if len(self.candlestick_data) > 0:
            number_of_data_points = len(self.candlestick_data[CommonDefs.INDEX_OF_MOMENTUM_DATA]["momentum"])

        # for each set of data, arrange the indicators for easy retrieval and comparison of data points
        # skip the frst 89 because that's the 89dayMA
        for j in range(89, number_of_data_points):
            self.data_points['Close_Data'] = self.candlestick_data[CommonDefs.INDEX_OF_OHLC_DATA]["Close"]
            self.data_points["williams_data"] = self.candlestick_data[CommonDefs.INDEX_OF_WILLIAMS_DATA]["%R"]
            self.data_points["ma_data_21d"] = self.candlestick_data[CommonDefs.INDEX_OF_MA_DATA]["pd_sma_21day"]["MA_21"]
            self.data_points["ma_data_55d"] = self.candlestick_data[CommonDefs.INDEX_OF_MA_DATA]["pd_sma_55day"]["MA_55"]
            self.data_points["ma_data_89d"] = self.candlestick_data[CommonDefs.INDEX_OF_MA_DATA]["pd_sma_89day"]["MA_89"]
            self.data_points["stochastics_data_k"] = self.candlestick_data[CommonDefs.INDEX_OF_STOCHASTICS_DATA]["%K"]
            self.data_points["stochastics_data_d"] = self.candlestick_data[CommonDefs.INDEX_OF_STOCHASTICS_DATA]["%D"]
            self.data_points["momentum_data"] = self.candlestick_data[CommonDefs.INDEX_OF_MOMENTUM_DATA]["momentum"]
            self.data_points["macd"] = self.candlestick_data[CommonDefs.INDEX_OF_MACD_DATA]["macd"]["MACD_12_26"]
            self.data_points["macd_signal"] = self.candlestick_data[CommonDefs.INDEX_OF_MACD_DATA]["macd"] \
                ["MACDsign_12_26"]

    def calculate_slope_of_line(self, series, beginning, end):
        # calculate slope of MACD signal line using linear regression
        slope = 0
        if (end - beginning) > 1:
            x_values = list(range(beginning, end))
            y_values = series[beginning: end]
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, list(y_values))

        return slope
