"""
GoldSax YFinance Quote. Version 0.1.
	To retrieve Capital Market quotes directly into your Python Applications. This can be used by any Trader, Market
Maker, a Retail Investor, Instituitional Investor, Hedge Fund Managers, and Asset Managers.

Copyright (c) <2014> Author Vance King Saxbe. A, and contributors Power Dominion Enterprise, Precieux Consulting and other contributors.

To install the package, you should be using Python 3.3 and above.(It also works with 2.7).

pip install GoldSaxYFinanceQuote.

This will install the package for you.

In your Application,

import GoldSaxYFinanceQuote

Values = GoldSaxYFinanceQuote.GetQuote(url)

"url" is the data source.
"

In the above code, "values "This should return a list of tuples with asset name and last traded value.


This Package is released under Contributor Agreement between Python Software Foundation (“PSF”) and Vance King Saxbe. A. and MIT License.

The MIT License (MIT)

Copyright (c) 2014 Author Vance King Saxbe. A, and contributors GoldSax Group, GoldSax Foundation, GoldSax Technologies, Power Dominion Enterprise, Precieux Consulting and other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


#!/usr/bin/env python33

import urllib3
import string
from time import localtime, strftime

class GoldSaxYFinanceQuote:    
    def GetQuote(url):
            http = urllib3.PoolManager()
            g_connector = http.request('GET', url)
            g_connector.release_conn()
            datadecoder = g_connector.data.decode("latin-1")
            first_splitter = datadecoder.split('\r\n')
            tstamp = strftime("%H:%M:%S", localtime())
            contents = []
            count = 0
            biz = len(a)
            for splits in first_splitter:
                if len(splits) > 0:
                    try:
                        second_splitter = splits.split(',')
                        contents.append([second_splitter[0].replace('"','').replace('.',''),strftime("%Y-%m-%d"),tstamp,second_splitter[1]])
                    except IndexError:
                        print("index out of range...")
                count = count+1
            return contents

