from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.

class Movies(models.Model):
    title = models.CharField(max_length=30)
    genres = models.CharField(max_length=50)
    photo=models.ImageField(upload_to='%Y/%m/%d',blank=True)
    description = models.TextField(blank=True)
    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def __str__(self):
        return self.title
    
    def __unicode__(self):
        return self.title

class Ratings(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    movieid = models.ForeignKey(Movies, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment=models.TextField(max_length=1000,blank=True,null=True)
    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
    
    def __str__(self):
        return self.userId.username

