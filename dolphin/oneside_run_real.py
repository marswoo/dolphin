#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from CTPHBAccount import CTPHBAccount
from Account import LocalWebServiceAccount
from StockDataFeeder import LocalWebServiceDataFeeder
from OnesideDolphin import OnesideDolphin
from Util import *

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print "usage: ./Dolphin.py pairid"
        sys.exit(-1)

    reconnect_database(settings.DATABASES["default"])
    init_logging( sys.argv[1] )

    data_feeder = LocalWebServiceDataFeeder()
    account = LocalWebServiceAccount()
#   account = CTPHBAccount()

    m = OnesideDolphin(sys.argv[1], data_feeder, account)
    m.run()


