from django.db import models
from filmmap.utils.fields import SetField

class Film(models.Model):
    title = models.CharField(max_length=512, unique=True, null=False)
    production_company = models.CharField(max_length=512)
    distributor = models.CharField(max_length=512)
    release_year = models.IntegerField()
    director = models.CharField(max_length=512)
    writers = SetField()
    actors = SetField()
    modified_date = models.DateTimeField('date modified', auto_now=True)

    def __str__(self):
        return self.title

class FilmLocation(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    location = models.CharField(max_length=1024)
    fun_facts = models.CharField(max_length=2048)

    def __str__(self):
        return self.location
