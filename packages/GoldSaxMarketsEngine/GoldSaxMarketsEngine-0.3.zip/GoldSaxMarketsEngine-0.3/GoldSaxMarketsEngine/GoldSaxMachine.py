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

from Chooser import *
import sqlite3 as lite
import string
import gc
import time
import math
class GoldSaxMachine:
  def ActionKing(tempf, stocklist, dbase, attmt, choice):
    filler = Chooser.GetIt(stocklist, choice)
    sorter = []
    con = lite.connect(dbase)
    for filled in filler:
            for temporary in tempf:
                    if (filled[0] == temporary[0]):
                            Jack = float(filled[3].replace(",",""))
                            Jill = float(temporary[3].replace(",",""))
                            
                            if (abs(Jack-Jill)> 0.01):
                                    sorter.append([filled[0],Jack, abs((Jack-Jill)/Jill)])
                                    stmt = "INSERT INTO "+filled[0]+"table(ONNN, ATTT, PRIC) VALUES ('"+filled[1]+"', '"+filled[2]+"', "+filled[3].replace(",","")+");"
                                    cur = con.cursor()
                                    try:
                                        cur.execute(stmt)
                                    except lite.OperationalError:
                                        print("database locked for ", fuck[0])
                                        time.sleep(0.25)
                                        try:
                                            cur.execute(stmt)
                                            print("tried once & executed for ", fuck[0])
                                        except lite.OperationalError:
                                            print("database still locked for", fuck[0])
                                            time.sleep(0.25)
                                            try:
                                                cur.execute(stmt)
                                                print("tried twice & executed for ", fuck[0])
                                            except lite.OperationalError:
                                                print("database still still locked.... fuckkk offff...", fuck[0]," is being pissing into...")
    con.commit()
    con.close()
    if sorter != []:
        attmt = 0
        sor = sorted(sorter, key=itemgetter(2),reverse=True)
        for so in sorter:
            print(so[0], so[1], "\r")
    if tempf != [] and sorter == [] and attmt == 4:
        gc.collect()
        print("all... attmts fnishd...")
        return 0
    if tempf != [] and sorter == [] and attmt == 3:
        time.sleep(220)
        gc.collect()
        attmt = 4
        print("attmt s ...", attmt)
    if tempf != [] and sorter == [] and attmt == 2:
        time.sleep(195)
        gc.collect()
        attmt = 3
        print("attmt s ...", attmt)
    if tempf != [] and sorter == [] and attmt == 1:
        time.sleep(120)
        gc.collect()
        attmt = 2
        print("attmt s ...", attmt)
    if tempf != [] and sorter == []:
        time.sleep(60)
        attmt = 1
        print("attmt s ...", attmt)
        gc.collect()
    time.sleep(30)
    gc.collect()
    return ActionKing(filler, stocklist,dbase, attmt,choice)
