__author__ = 'kmadac'

import os
import bitstamp.client
import time

bc = bitstamp.client.Trading(username=os.environ['bs_user'],
                             key=os.environ['bs_key'],

                             secret=os.environ['bs_secret'])
print(bc.account_balance())
print(bc.unconfirmed_bitcoin_deposits())
