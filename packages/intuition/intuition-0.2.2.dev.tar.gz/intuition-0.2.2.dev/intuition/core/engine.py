#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytz
import pandas as pd
import logbook

from intuition.data.utils import Exchanges
from intuition.modules.sources.loader import LiveBenchmark
from intuition.core.analyzes import Analyze

from zipline.finance.trading import TradingEnvironment
from zipline.utils.factory import create_simulation_parameters

import intuition.modules.library as library


BASE_CONFIG = {'algorithm': {}, 'manager': {}}
DEFAULT_PORTFOLIO_NAME = 'ChuckNorris'
log = logbook.Logger('intuition.core.engine')


class TradingEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo
    ready for use '''

    def __new__(self, algo, manager=None, source=None,
                strategy_configuration=BASE_CONFIG):
        '''
        Reads the user configuration and returns
        '''
        library.check_availability(algo, manager, source)

        #NOTE Other params: annualizer (default is cool), capital_base,
        #     data_frequency, sim_params (both are set in run function)
        trading_algorithm = library.algorithms[algo](
            properties=strategy_configuration['algorithm'])

        portfolio_name = strategy_configuration['manager'].get(
            'name', DEFAULT_PORTFOLIO_NAME)
        trading_algorithm.set_logger(logbook.Logger('algo.' + portfolio_name))

        if source:
            trading_algorithm.set_data_generator(library.data_sources[source])

        # Use of a portfolio manager
        if manager:
            log.info('initializing Manager')
            # Linking to the algorithm the configured portfolio manager
            trading_algorithm.manager = library.portfolio_managers[manager](
                strategy_configuration['manager'])

            # If requested and possible, loads the named portfolio to start
            # trading with it
            #FIXME Works, but every new event resets the portfolio

            if strategy_configuration['manager'].get('load_backup', False) \
                    and portfolio_name:

                log.info('Re-loading last {} portfolio from database'
                         .format(portfolio_name))
                # Retrieving a zipline portfolio object. str() is needed as the
                # parameter is of type unicode
                backup_portfolio = trading_algorithm.manager.load_portfolio(
                    str(portfolio_name))

                if backup_portfolio is None:
                    log.warning('! Unable to set {} portfolio: not found'
                                .format(portfolio_name))
                else:
                    trading_algorithm.set_portfolio(backup_portfolio)
                    log.info('Portfolio setup successful')
        else:
            trading_algorithm.manager = None
            log.info('no portfolio manager used')

        return trading_algorithm


#NOTE engine.feed_data(universe, start, end, freq) ? using set_source()
class Simulation(object):
    ''' Take a trading strategy and evalute its results '''

    def __init__(self, configuration):
        #self.server        = ZMQ_Dealer(id=self.__class__.__name__)
        self.configuration = configuration
        self.context = None

    #TODO For both, timezone configuration
    def configure(self):
        '''
        Prepare dates, data, trading environment for simulation
        '''
        last_trade = self.configuration['index'][-1]
        if last_trade > pd.datetime.now(pytz.utc):
            # This is live trading
            self.set_benchmark_loader(LiveBenchmark(
                last_trade, frequency='minute').surcharge_market_data)
        else:
            self.set_benchmark_loader(None)

        self.context = self._configure_context(self.configuration['exchange'])

    def set_benchmark_loader(self, load_function):
        self.load_market_data = load_function

    #TODO Use of futur localisation database criteria
    def _configure_context(self, exchange=''):
        '''
        Setup from exchange traded on benchmarks used, location
        and method to load data market while simulating
        _______________________________________________
        Parameters
            exchange: str
                Trading exchange market
        '''
        # Environment configuration
        if exchange in Exchanges:
            trading_context = TradingEnvironment(
                bm_symbol=Exchanges[exchange]['symbol'],
                exchange_tz=Exchanges[exchange]['timezone'],
                load=self.load_market_data)
        else:
            raise NotImplementedError('Because of computation limitation, \
                trading worldwide not permitted currently')

        return trading_context

    def run(self, data, strategy):
        engine = TradingEngine(self.configuration['modules']['algorithm'],
                               self.configuration['modules']['manager'],
                               self.configuration['modules']['data'],
                               strategy)

        #NOTE This method does not change anything
        #engine.set_sources([DataLiveSource(data_tmp)])
        #TODO A new command line parameter ? only minutely and daily
        #     (and hourly normaly) Use filter parameter of datasource ?
        #engine.set_data_frequency(self.configuration['frequency'])
        engine.is_live = self.configuration['live']

        # Running simulation with it
        #FIXME crash if trading one day that is not a trading day
        with self.context:
            sim_params = create_simulation_parameters(
                capital_base=strategy['manager']['cash'],
                start=self.configuration['index'][0],
                end=self.configuration['index'][-1])

            daily_stats = engine.go(data, sim_params=sim_params)

        return Analyze(
            results=daily_stats,
            metrics=engine.risk_report,
            datafeed=None,
            configuration=self.configuration)
