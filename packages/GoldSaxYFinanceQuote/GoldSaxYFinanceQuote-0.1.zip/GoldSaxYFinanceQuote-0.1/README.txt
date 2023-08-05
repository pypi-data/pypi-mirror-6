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
