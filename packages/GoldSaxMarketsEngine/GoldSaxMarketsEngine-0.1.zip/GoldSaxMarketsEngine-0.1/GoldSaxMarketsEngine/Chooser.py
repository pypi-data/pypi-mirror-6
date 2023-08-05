"""
MarketsEngine. Version 0.1.
	To retrieve Capital Market quotes directly into an sqlite Database. This can be used by any Trader, Market
Maker, a Retail Investor, Instituitional Investor, Hedge Fund Managers, and Asset Managers.

Copyright (c) <2014> Author Vance King Saxbe. A, and contributors Power Dominion Enterprise, Precieux Consulting and other contributors.

To install the package, you should be using Python 3.3 and above.(It also works with 2.7).

pip install GoldSaxGFinanceQuote.

pip install GoldSaxYFinanceQuote.

pip install GoldSaxMarketsEngine.

This will install the package for you.


Please refer to documentation for further use of this package.

For further support email Vance King Saxbe. A to vsaxbe@yahoo.com.

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

import GoldSaxGFinanceQuote
import GoldSaxYFinanceQuote

class Chooser:
    def GetIt(url, choice):
            if choice=="g":
                    return GoldSaxGFinanceQuote.GetQuote(url)
            elif choice == "y":
                    return GoldSaxYFinanceQuote.GetQuote(url)
