#!/usr/bin/env python3
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


import _thread
import os
import sys
import time
from CreateTables import *
from GoldSaxMachine import *

class GoldSaxMarketsEngine:
        def EngineStart(entries):
                start1 = []

                sys.setrecursionlimit(100000)
                database = entries[0]
                with open(entries[1]) as f:
                    actionlist = f.read().splitlines()
                for listo in actionlist:
                        lis = listo.split('", "')
                        CreateTables.Create(lis[0].replace('"',''), database+lis[2].replace('"',''),lis[1])
                while("TRUE"):
                        with open(entries[1]) as openedfile:
                            fileaslist = openedfile.read().splitlines()
                        a_lock = _thread.allocate_lock()
                        thr = []
                        with a_lock:
                                print("locks placed and Market engine is running.....")
                                for lines in fileaslist:
                                        lisj = lines.split('", "')
                                        thr.append(_thread.start_new_thread(GoldSaxMachine.ActionKing, (start1, lisj[0].replace('"',''),database+lisj[2].replace('"',''),0,lisj[1]) ))
                                        time.sleep(0.001)
                        time.sleep(1800)
                        _thread.exit()
                        _thread.interrupt_main()
                        time.sleep(10)
                while 1:
                        pass
                for th in thr:
                        th._thread.exit()
                return 0
