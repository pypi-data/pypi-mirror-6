GoldSax GFinance Quote. Version 0.1.
	To retrieve Capital Market quotes directly into your Python Applications. This can be used by any Trader, Market
Maker, a Retail Investor, Instituitional Investor, Hedge Fund Managers, and Asset Managers.

Copyright (c) <2014> Author Vance King Saxbe. A, and contributors Power Dominion Enterprise, Precieux Consulting and other contributors.

To install the package, you should be using Python 3.3 and above.(It also works with 2.7).

pip install GoldSaxGFinanceQuote.

This will install the package for you.

In your Application,

import GoldSaxGFinanceQuote

Values = GoldSaxGFinanceQuote.GetQuote(url, needcsv, location)

"url" is the data source.
"needcsv" is a boolean(TRUE or FALSE), whether the values are to be stored in a csv file or not.
"location" is the absolute file path to the csv files.

In the above code, "values "This should return a list of tuples with asset name and last traded value.
