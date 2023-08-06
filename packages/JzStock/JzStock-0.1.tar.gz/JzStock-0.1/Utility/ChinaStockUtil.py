# -*- coding=utf-8 -*-
'''
The utility for HongKong stock markets.
@author: eric<eric.ni@ijinzhuan.com> 
@version:1.0 2014-4-10
'''

class ChinaStockUtil(object):
    
    @staticmethod
    def getMarketPrefix(stock_code):
        '''Get the market code prefix from stock code.'''
        assert(type(stock_code)==str)
        if stock_code.startswith('000'): return 'sz'    # Shenzhen Main-Board Market - A Share
        if stock_code.startswith('200'): return 'sz'    # Shenzhen Main-Board Market - B Share
        if stock_code.startswith('002'): return 'sz'    # Shenzhen Second-Board Market
        if stock_code.startswith('300'): return 'sz'    # Shenzhen Growth Enterprise Market
        if stock_code.startswith('600'): return 'sh'    # Shanghai Main-Board Market - A Share
        if stock_code.startswith('601'): return 'sh'    # Shanghai Main-Board Market - A Share
        if stock_code.startswith('603'): return 'sh'    # Shanghai Main-Board Market - A Share
        if stock_code.startswith('900'): return 'sh'    # Shanghai Main-Board Market - B Share
        return 'unknown'
    
    
    
    