from django.db import models

# Create your models here.
class StockMetaData(models.Model):
    stockid = models.CharField(max_length=20, db_index=True)
    date = models.DateField(db_index=True)
    time = models.TimeField()
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    yesterday_close_price = models.DecimalField(max_digits=8, decimal_places=2)
    today_open_price = models.DecimalField(max_digits=8, decimal_places=2)
    today_highest_price = models.DecimalField(max_digits=8, decimal_places=2)
    today_lowest_price = models.DecimalField(max_digits=8, decimal_places=2)
    deal_stock_amount = models.IntegerField()
    deal_stock_money = models.DecimalField(max_digits=15, decimal_places=2)
    buy1_price = models.DecimalField(max_digits=8, decimal_places=2)
    buy1_amount = models.IntegerField()
    buy2_price = models.DecimalField(max_digits=8, decimal_places=2)
    buy2_amount = models.IntegerField()
    buy3_price = models.DecimalField(max_digits=8, decimal_places=2)
    buy3_amount = models.IntegerField()
    sell1_price = models.DecimalField(max_digits=8, decimal_places=2)
    sell1_amount = models.IntegerField()
    sell2_price = models.DecimalField(max_digits=8, decimal_places=2)
    sell2_amount = models.IntegerField()
    sell3_price = models.DecimalField(max_digits=8, decimal_places=2)
    sell3_amount = models.IntegerField()

    def __unicode__(self):
        return '\t'.join([ str(self.stockid), str(self.timestamp), str(self.current_price) ])

class PairDelta(models.Model):
    pairid = models.CharField(max_length=40)
    timestamp = models.DateTimeField()
    minutes_to_closemarket = models.IntegerField()
    delta1 = models.DecimalField(max_digits=8, decimal_places=6)
    delta2 = models.DecimalField(max_digits=8, decimal_places=6)

    def __unicode__(self):
        return '\t'.join([ str(self.pairid), str(self.timestamp), str(self.minutes_to_closemarket), str(self.delta1), str(self.delta2) ])

class Deal(models.Model):
    timestamp = models.DateTimeField()
    is_buy = models.BooleanField()
    stockid = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=4)
    amount = models.IntegerField()
    is_real = models.BooleanField()

    def __unicode__(self):
        return '\t'.join([ str(self.timestamp), str(self.is_buy), str(self.stockid), str(self.price), str(self.amount) ])

class Asset(models.Model):
    pairid = models.CharField(max_length=40)
    date = models.DateField()
    cash = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    is_real = models.BooleanField()

    def __unicode__(self):
        return '\t'.join([ str(self.pairid), str(self.date), str(self.cash), str(self.total) ])

class MarketCloseDate(models.Model):
    date = models.DateField(primary_key=True)

    def __unicode__(self):
        return str(self.date)

class NotificationNews(models.Model):
    pairid = models.CharField(max_length=40)
    date = models.DateField()
    news = models.TextField()
    label = models.BooleanField()




