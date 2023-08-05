MarketsEngine. Version 0.1.
	To retrieve Capital Market quotes directly into an sqlite Database. This can be used by any Trader, Market
Maker, a Retail Investor, Instituitional Investor, Hedge Fund Managers, and Asset Managers.

Copyright (c) <2014> Author Vance King Saxbe. A, and contributors Power Dominion Enterprise, Precieux Consulting and other contributors.

To install the package, you should be using Python 3.3 and above.(It also works with 2.7).

pip install GoldSaxGFinanceQuote.

pip install GoldSaxYFinanceQuote.

pip install GoldSaxMarketsEngine.

This will install the package for you.

Decide upon a database location in your file system.
and a location to place urls.conf file.

please refer documentation for using the urls.conf file.

from GoldSaxMarketsEngine import *

data = ["database location", "urls.conf location"]

GoldSaxMarketsEngine.EngineStart(data)


The engine starts and the tables are created in the database and checked and the database is inserted with data.


Please refer to documentation for further use of this package.

For further support email Vance King Saxbe. A to vsaxbe@yahoo.com.