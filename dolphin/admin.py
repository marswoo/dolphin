#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from dolphin.models import StockMetaData, PairDelta, Deal, Asset, MarketCloseDate

admin.site.register(StockMetaData)
admin.site.register(PairDelta)
admin.site.register(Deal)
admin.site.register(Asset)
admin.site.register(MarketCloseDate)

