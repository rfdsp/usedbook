from django.db import models

class WantedBook(models.Model):
    isbn=models.CharField(max_length=10,null=False)
    name=models.CharField(max_length=256)
    retailPrice=models.IntegerField()
    price=models.IntegerField()
    millage=models.IntegerField()
    realPrice=models.IntegerField()
    def __unicode__(self):
        return self.isbn

