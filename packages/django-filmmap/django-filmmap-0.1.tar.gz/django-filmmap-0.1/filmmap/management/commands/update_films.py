from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.timezone import utc
from filmmap.models import Film, FilmLocation
import urllib.request
import datetime
import json
import os


class Command(BaseCommand):
    args = "<url>"
    help = "Update the film database with new films."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "update_films.log") 
        self._KEEP_DAYS = 1  # Number of days to keep old entries
        self.log_file = open(self._LOG_FILE, 'a')
        self.has_errors = False

    def clear_old_entries(self):
        ''' Clear old entries created before yesterday '''
        window = datetime.datetime.now(utc) - datetime.timedelta(days=self._KEEP_DAYS)
        Film.objects.filter(modified_date__lt=window).delete()

    def create_entry(self, film_entry):
        _MAX_ACTORS = 4  # Maximum actors in the film source
        actors = None
        if film_entry.get('actor_1'):
            actors = film_entry['actor_1']
            for i in range(1, _MAX_ACTORS + 1):
                if film_entry.get('actor_'+str(i)):
                    actors += ", " + film_entry['actor_'+str(i)]

        try:
            film = Film(title=film_entry['title'])
            if film_entry.get('production_company'):
                film.production_company = film_entry['production_company']
            if film_entry.get('distributor'):
                film.distributor = film_entry['distributor']
            if film_entry.get('release_year'):
                film.release_year = int(film_entry['release_year'])
            if film_entry.get('director'):
                film.director = film_entry['director']
            if film_entry.get('writer'):
                film.writers=film_entry['writer']
            if actors:
                film.actors = actors
            film.save()
            self.update_entry(film, film_entry)
        except KeyError:
            self.log_file.write("[%s] Error: Film entry is missing a required key.\n" % datetime.datetime.now() +
                                "Film entry: %s\n" % film_entry)
            self.has_errors = True

    def update_entry(self, film, film_entry):
        if film_entry.get('locations'):
            entry_location = FilmLocation.objects.filter(film=film, location=film_entry['locations'])
            if not entry_location:
                try:
                    entry_location = FilmLocation(film=film, location=film_entry['locations'])
                    if film_entry.get('fun_facts'):
                        entry_location.fun_facts = film_entry['fun_facts']
                    entry_location.save()
                    film.save()
                except IntegrityError:
                    self.log_file.write("[%s] Error: Entry location insertion failed.\n" % datetime.datetime.now() +
                                        "Film: %s\n" % film +
                                        "Film entry: %s\n" % film_entry)
                    self.has_errors = True

    def update_database(self, film_entry):
        film = Film.objects.filter(title=film_entry['title'])
        if film:
            self.update_entry(film[0], film_entry)
        else:
            self.create_entry(film_entry)

    def insert(self, url):
        try:
            with urllib.request.urlopen(url) as f:
                for film_entry in json.loads(f.read().decode('utf-8')):
                    self.update_database(film_entry)
        except urllib.error.HTTPError as err:
            self.log_file.write("[%s] Error: %s" % (datetime.datetime.now(), err)) 
            self.has_errors = True
            raise

    def handle(self, *args, **options):
        if 1 <= len(args) <= 2:
            url = args[0]
            if len(args) == 2:
                self.log_file = open(args[1], 'a')

            has_errors = ''
            if self.has_errors:
                has_errors = " Finished with errors."
            self.insert(url)
            self.log_file.write("[%s] Insertion finished. %s\n" % (datetime.datetime.now(), has_errors))
            self.clear_old_entries()
            self.log_file.write("[%s] Old entries cleared.\n\n\n" % datetime.datetime.now())

            self.stdout.write("Completed. %s\nSee log file '%s' for more details." % (has_errors, self.log_file.name))
        else:
            print("Usage: %s url [log_file]" % __file__)

    def __del__(self):
        self.log_file.close()
        del self.log_file
