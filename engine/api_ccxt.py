import logging
import time
from functools import wraps
import ccxt.async_support
from engine.api_functions import FtxExceptions
from ftx_lib.websocket_api import client as ws_client

# key, secret, market, subaccount_name = load_config()


class FtxDisconnectError(Exception):
    """
    Generic disconnect
    """
    pass



"""
{'id': 'ftx', 'name': 'FTX', 'countries': ['HK'], 'rateLimit': 50, 'certified': True, 'pro': True, 
'hostname': 'ftx.com', 'urls': {'logo': 'https://user-images.githubusercontent.com/1294454/67149189-df896480-f2b0-11e9-8816-41593e17f9ec.jpg', 
'www': 'https://ftx.com', 'api': {'public': 'https://{hostname}', 'private': 'https://{hostname}'}, 'doc': 'https://github.com/ftexchange/ftx',
 'fees': 'https://ftexchange.zendesk.com/hc/en-us/articles/360024479432-Fees', 'referral': 'https://ftx.com/#a=darkerego'}, 
 'has': {'cancelAllOrders': True, 'cancelOrder': True, 'createOrder': True, 'editOrder': True, 'fetchBalance': True, 
 'fetchClosedOrders': False, 'fetchCurrencies': True, 'fetchDepositAddress': True, 'fetchDeposits': True, 
 'fetchFundingFees': False, 'fetchMarkets': True, 'fetchMyTrades': True, 'fetchOHLCV': True, 'fetchOpenOrders': True, 
 'fetchOrder': True, 'fetchOrderBook': True, 'fetchOrders': True, 'fetchTicker': True, 'fetchTickers': True, 
 'fetchTrades': True, 'fetchTradingFees': True, 'fetchWithdrawals': True, 'withdraw': True}, 
 'timeframes': {'15s': '15', '1m': '60', '5m': '300', '15m': '900', '1h': '3600', '4h': '14400', '1d': '86400'}, 
 'api': {'public': {'get': ['coins', 'markets', 'markets/{market_name}', 'markets/{market_name}/orderbook', 
 'markets/{market_name}/trades', 'markets/{market_name}/candles', 'futures', 'futures/{future_name}', 
 'futures/{future_name}/stats', 'funding_rates', 'indexes/{index_name}/weights', 'expired_futures', 
 'indexes/{market_name}/candles', 'lt/tokens', 'lt/{token_name}', 'options/requests', 'options/trades', 
 'stats/24h_options_volume', 'options/historical_volumes/BTC', 'options/open_interest/BTC', 
 'options/historical_open_interest/BTC']}, 'private': {'get': ['account', 'positions', 'wallet/coins', 
 'wallet/balances', 'wallet/all_balances', 'wallet/deposit_address/{coin}', 'wallet/deposits', 
 'wallet/withdrawals', 'wallet/withdrawal_fee', 'wallet/airdrops', 'wallet/saved_addresses', 'orders', 
 'orders/history', 'orders/{order_id}', 'orders/by_client_id/{client_order_id}', 'conditional_orders', 
 'conditional_orders/{conditional_order_id}/triggers', 'conditional_orders/history', 'spot_margin/borrow_rates', 
 'spot_margin/lending_rates', 'spot_margin/borrow_summary', 'spot_margin/market_info', 'spot_margin/borrow_history', 
 'spot_margin/lending_history', 'spot_margin/offers', 'spot_margin/lending_info', 'fills', 'funding_payments', '
 lt/balances', 'lt/creations', 'lt/redemptions', 'subaccounts', 'subaccounts/{nickname}/balances', 'otc/quotes/{quoteId}', 
 'options/my_requests', 'options/requests/{request_id}/quotes', 'options/my_quotes', 'options/account_info', 
 'options/positions', 'options/fills', 'staking/stakes', 'staking/unstake_requests', 'staking/balances', 
 'staking/staking_rewards'], 'post': ['account/leverage', 'wallet/withdrawals', 'wallet/saved_addresses', 
 'orders', 'conditional_orders', 'orders/{order_id}/modify', 'orders/by_client_id/{client_order_id}/modify', 
 'conditional_orders/{order_id}/modify', 'spot_margin/offers', 'lt/{token_name}/create', 'lt/{token_name}/redeem', 
 'subaccounts', 'subaccounts/update_name', 'subaccounts/transfer', 'otc/quotes/{quote_id}/accept', 'otc/quotes', 
 'options/requests', 'options/requests/{request_id}/quotes', 'options/quotes/{quote_id}/accept', 
 'staking/unstake_requests', 'srm_stakes/stakes'], 'delete': ['wallet/saved_addresses/{saved_address_id}', 
 'orders/{order_id}', 'orders/by_client_id/{client_order_id}', 'orders', 'conditional_orders/{order_id}', 
 'subaccounts', 'options/requests/{request_id}', 'options/quotes/{quote_id}', 'staking/unstake_requests/{request_id}']}}, 
 'fees': {'trading': {'tierBased': True, 'percentage': True, 'maker': 0.0002, 'taker': 0.0007000000000000001, 
 'tiers': {'taker': [[0, 0.0007000000000000001], [1000000, 0.0006], [5000000, 0.00055], [10000000, 0.0005], [15000000, 0.00045], [35000000, 0.0004]], 
 'maker': [[0, 0.0002], [1000000, 0.0002], [5000000, 0.00015], [10000000, 0.00015], [15000000, 0.0001], [35000000, 0.0001]]}}, 
 'funding': {'withdraw': {}}}, 'exceptions': {'exact': {'Please slow down': <class 'ccxt.base.errors.RateLimitExceeded'>, 
 'Size too small for provide': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Not logged in': <class 'ccxt.base.errors.AuthenticationError'>, 
 'Not enough balances': <class 'ccxt.base.errors.InsufficientFunds'>, 
 'InvalidPrice': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Size too small': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Missing parameter price': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Order not found': <class 'ccxt.base.errors.OrderNotFound'>, 
 'Order already closed': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Trigger price too high': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Trigger price too low': <class 'ccxt.base.errors.InvalidOrder'>, 
 'Order already queued for cancellation': <class 'ccxt.base.errors.CancelPending'>}, 
 'broad': {'Account does not have enough margin for order': <class 'ccxt.base.errors.InsufficientFunds'>, '
 Invalid parameter': <class 'ccxt.base.errors.BadRequest'>, 
 'The requested URL was not found on the server': <class 'ccxt.base.errors.BadRequest'>, 
 'No such coin': <class 'ccxt.base.errors.BadRequest'>, 
 'No such market': <class 'ccxt.base.errors.BadRequest'>, 
 'Do not send more than': <class 'ccxt.base.errors.RateLimitExceeded'>, 
 'An unexpected error occurred': <class 'ccxt.base.errors.ExchangeNotAvailable'>, 
 'Please retry request': <class 'ccxt.base.errors.ExchangeNotAvailable'>, 
 'Please try again': <class 'ccxt.base.errors.ExchangeNotAvailable'>, 
 'Only have permissions for subaccount': <class 'ccxt.base.errors.PermissionDenied'>}}, 
 'precisionMode': 4, 'options': {'cancelOrder': {'method': 'privateDeleteOrdersOrderId'}, 
 'fetchOpenOrders': {'method': 'privateGetOrders'}, 
 'fetchOrders': {'method': 'privateGetOrdersHistory'}, 'sign': {'ftx.com': 'FTX', 'ftx.us': 'FTXUS'}}}
"""


@wraps
def call(func, *args, **kwargs):
    func(args, kwargs)


class ApiFunctions:
    """ API Wrapper
    """

    def __init__(self, key, secret, subaccount_name):
      """
      Initialize the websocket and connect ccxt rest api
      @param key: api key
      @param secret: api secret
      @param subaccount_name: connect to this subaccount
      """
        self.ws = ws_client.FtxWebsocketClient(api_key=key, api_secret=secret, subaccount_name=subaccount_name)
        self.logger = logging.getLogger(__name__)
        self.logger.level = 20
        self.ftx = ccxt.ftx({'verbose': True})
        self.exchange_id = 'ftx'
        self.exchange_class = getattr(ccxt, self.exchange_id)
        self.ftx_api = exchange = self.exchange_class({
            'enableRateLimit': True,
            'apiKey': key,
            'secret': secret,
            'timeout': 30000,
            'subaccount': subaccount_name
        })

    def info(self, attribute=None):
        info = self.ftx_api.private_get_account()['result']
        if attribute is None:
            return info
        else:
            try:
                info[attribute]
            except IndexError:
                return False
            else:
                return info[attribute]

    def ticker(self, market):
        return self.ws.get_ticker(market=market)

    def futures(self, f=None):
        fut = []
        for i in self.ftx_api.fetchMarkets():

            if i['type'] == 'future':
                fut.append(i)
        return fut

    def markets(self):
        # return self.rest.list_markets()
        markets = []
        for i in self.ftx_api.fetchMarkets():
            if i['type'] == 'spot':
                markets.append(i)
        return markets

    def fills(self):
        return self.ws.get_fills()

    def trades(self, market):
        return self.ws.get_trades(market=market)

    def orderbook(self, market):
        return self.ws.get_orderbook(market=market)

    def position(self):
        return self.ftx_api.fetch_positions()

    def open_orders(self, market):
        return self.ftx_api.fetchOpenOrders(market=market)

    def open_conditional_orders(self, market):
        return self.ftx_api.get_conditional_orders(market=market)

    def order_history(self, market, side=None):
        return self.ftx_api.get_order_history(market=market, side=side)

    def conditional_order_history(self, market, side=None):
        return self.ftx_api.get_conditional_order_history(market=market, side=side)

    def balances(self):
        return self.ftx_api.fetchBalance().get('info').get('result')

    def new_order(self, market: str, side: str, price: float = None, size: float = None, _type: str = 'limit',
                  reduce: bool = False, ioc: bool = False, post_only: bool = False, client_id: str = None):
        # self.log_trade(f'Market: {market}, Side: {side}, Price: {price}, Type: {_type}, Reduce: {reduce,} IOC: {ioc},'
        #               f'Post: {post_only}, CID: {client_id}')

        """
        Create an order
        api.createOrder(symbol='TRX-PERP', type='limit', side='sell', amount=1.0, price='0.1249650', params={"reduceOnly":False, "ioc": False, "postOnly":True, "clientId":None})
        """

        for i in range(1, 30):
            try:
                """order = self.rest.place_order(market=market,
                                              side=side,
                                              price=price,
                                              size=size,
                                              type=_type,
                                              reduce_only=reduce,
                                              ioc=ioc,
                                              post_only=post_only)"""
                order = self.ftx_api.createOrder(symbol=market, type=_type, side=side, amount=size, price=price,
                                                 params={"reduceOnly": reduce, "ioc": ioc, "postOnly": post_only,
                                                         "clientId": client_id})
            except Exception as err:
                self.logger.error(err)
            except FtxExceptions.catchall as err:
                print(err)
            else:
                self.logger.info('Order Placed!')
                print(order)
                return True
            time.sleep(0.125)
        self.logger.error(f'Could not place order!')
        return False

    def trailing_stop(self, market: str, side: str, size: float, price: float = None, trail_value: float = None,
                      trigger_price: float = None, reduce_only: bool = True):
        """def place_conditional_order(
        self, market: str, side: str, size: float, type: str = 'stop',
        limit_price: float = None, reduce_only: bool = False, cancel: bool = True,
        trigger_price: float = None, trail_value: float = None
    ) -> dict:
        To send a Stop Market order, set type='stop' and supply a trigger_price
        To send a Stop Limit order, also supply a limit_price
        To send a Take Profit Market order, set type='trailing_stop' and supply a trigger_price
        To send a Trailing Stop order, set type='trailing_stop' and supply a trail_value
        """
        # self.rest.place_order()
        order = self.ftx_api.create_order(symbol=market,  # market
                                          type='trailingStop',  # type
                                          side='sell',  # side
                                          amount=size,  # amount
                                          price=price,
                                          params={
                                              "trailValue": trail_value,
                                              "retryUntilFilled": True,
                                              "reduceOnly": reduce_only}
                                          )

    def cancel_order(self, order_id):
        """
        Cancel an order
        """
        for i in range(1, 3):
            try:
                self.ftx_api.cancelOrder(id=order_id)
            except Exception as err:
                self.logger.error(err)
            else:
                self.logger.info('Order canceled')
                return
            time.sleep(0.125)
        self.logger.error(f'Could not cancel order!')
        return False

    def cancel_all_limit(self, market):
        self.ftx_api.cancelAllOrders(symbol=market)

    def modify_order(self, order_id, price, size, market, side, type='limit'):
        for i in range(1, 3):
            try:
                # ret = self.rest.modify_order(existing_order_id=order_id, price=price, size=size)
                ret = self.ftx_api.edit_order(id=order_id, price=price, symbol=market, type=type, side=side,
                                              amount=size)
            except Exception as err:
                self.logger.error(err)
            else:
                return ret
        self.logger.error('Could not modify order!')

    def create_sub_account(self, name):
        self.ftx_api.subaccounts()
