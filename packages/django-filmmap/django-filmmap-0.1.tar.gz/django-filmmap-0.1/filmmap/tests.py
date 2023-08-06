from django.core.management import call_command
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from filmmap.models import Film, FilmLocation
import urllib
import json
import os


_ROOT = os.path.abspath(os.path.dirname(__file__))
_URL_FILE = 'url.txt'
_LOG_FILE = 'update_films.log'
_LOG_SUCCESS_MSG = 'Insertion finished'
_LOG_CLEAR_MSG = 'Old entries cleared'
_API_URL = 'filmmap:api_v1'


class UpdateFilmsTests(TestCase):
    def setUp(self):
        with open(os.path.join(_ROOT, _URL_FILE), 'r') as f:
            self.url = f.readline()
        if self.url:
            self.log_file = os.path.join(_ROOT, _LOG_FILE)
            args = [self.url, self.log_file]
        call_command('update_films', *args)

    def test_database_not_empty(self):
        '''Test if the database was populated with entries'''
        films = Film.objects.count()
        film_locations = FilmLocation.objects.count()

        self.assertGreater(films, 0)
        self.assertGreater(film_locations, 0)

    def test_log_file_success(self):
        '''Test if the log file gave success messages'''
        with open(self.log_file, 'r') as f:
            self.assertIn(_LOG_SUCCESS_MSG.lower(), f.readline().lower())
            self.assertIn(_LOG_CLEAR_MSG.lower(), f.readline().lower())

    def test_all_entries_added(self):
        '''Test if the database was populated with *every* entry'''
        with urllib.request.urlopen(self.url) as f:
            source_data = json.loads(f.read().decode('utf-8'))

        no_location_count = 0
        for item in source_data:
            if not item.get('locations'):
                no_location_count += 1

        duplicate_locations_count = 0
        film_locations = {}
        for item in source_data:
            if item.get('title') and not film_locations.get(item['title']):
                film_locations[item['title']] = {item.get('locations')}
            elif item.get('title'):
                if item.get('locations') and item['locations'] in film_locations[item['title']]:
                    duplicate_locations_count += 1
                elif item.get('locations'):
                    film_locations[item['title']].add(item.get('locations'))

        total_locations = len(source_data) - no_location_count - duplicate_locations_count
        self.assertEqual(total_locations, FilmLocation.objects.count())

    def tearDown(self):
        if os.path.isfile(self.log_file):
            os.remove(self.log_file)


class ApiTests(TestCase):
    def setUp(self):
        self.global_limit_count = 25

        with open(os.path.join(_ROOT, _URL_FILE), 'r') as f:
            self.url = f.readline()
        if self.url:
            self.log_file = os.path.join(_ROOT, _LOG_FILE)
            args = [self.url, self.log_file]
        call_command('update_films', *args)

    def test_limit_query(self):
        '''Test if a query with a limit parameter matches the database'''
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_query = {film['title'] for film in Film.objects.all()[:limit_count].values('title')}

        response = self.client.get(reverse(_API_URL), {'limit': limit_count})
        json_response = json.loads(response.content.decode('utf-8'))
        api_query = {film['title'] for film in json_response}

        self.assertEqual(film_query, api_query)

    def test_select_title_query(self):
        '''Test if a query with a select=title parameter matches the database'''
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_query = list(Film.objects.all()[:limit_count].values('title'))

        response = self.client.get(reverse(_API_URL), {'select': 'title', 'limit': limit_count})
        api_query = json.loads(response.content.decode('utf-8'))

        self.assertEqual(film_query, api_query)

    def test_select_release_year_query(self):
        '''Test if a query with a select=release_year (integer) parameter matches the database'''
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_query = list(Film.objects.all()[:limit_count].values('title', 'release_year'))

        response = self.client.get(reverse(_API_URL), {'select': 'release_year', 'limit': limit_count})
        api_query = json.loads(response.content.decode('utf-8'))

        self.assertEqual(film_query, api_query)

    def test_select_actors_query(self):
        '''Test if a query with a select=actors parameter matches the database'''
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_query = list(Film.objects.all()[:limit_count].values('title', 'actors'))

        response = self.client.get(reverse(_API_URL), {'select': 'actors', 'limit': limit_count})
        json_response = json.loads(response.content.decode('utf-8'))
        api_query = [{'title':film['title'],'actors':", ".join(film['actors'])} for film in json_response]

        self.assertEqual(film_query, api_query)

    def test_order_by_asc_query(self):
        '''Test if a query with a order=title parameter (ascending) matches the database''' 
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_query = list(Film.objects.all().order_by('title')[:limit_count].values('title'))

        response = self.client.get(reverse(_API_URL), 
                {'select': 'title', 'order': 'title', 'limit': limit_count})
        api_query = json.loads(response.content.decode('utf-8'))

        self.assertEqual(film_query, api_query)

    def test_order_by_desc_query(self):
        '''Test if a query with a order=title parameter (descending) matches the database''' 
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_query = list(Film.objects.all().order_by('-title')[:limit_count].values('title'))

        response = self.client.get(reverse(_API_URL), 
                {'select': 'title', 'order': '-title', 'limit': limit_count})
        api_query = json.loads(response.content.decode('utf-8'))

        self.assertEqual(film_query, api_query)

    def test_select_location_query(self):
        '''Test if a query with a select=location parameter matches the database'''
        if self.global_limit_count:
            limit_count = self.global_limit_count
        else:
            limit_count = 25

        film_titles = FilmLocation.objects.all().order_by('-location').values('film__title')[:limit_count]
        film_query = []
        for title in film_titles:
            film_locations = list(FilmLocation.objects.filter(film__title=title['film__title']).values())
            for film_location in film_locations:
                film_location.pop('id')
                film_location.pop('film_id')
                film_location.pop('fun_facts')
            film_query.append({'title': title['film__title'], 'locations': film_locations})

        response = self.client.get(reverse(_API_URL), 
                {'select': 'location', 'order': '-location', 'limit': limit_count})
        api_query = json.loads(response.content.decode('utf-8'))

        self.assertEqual(film_query, api_query)

    def test_where_integer_query(self):
        '''Test if a query with a where=title=[specific_film_name] (integer) parameter matches the database'''
        film_name = '180'  # Target a specific film with an integer as all of the name

        film_query = list(Film.objects.filter(title=film_name).values())
        film_locations = list(FilmLocation.objects.filter(film__id=film_query[0]['id']).values())
        for film_location in film_locations:
            film_location.pop('id')
            film_location.pop('film_id')
        film_query[0].pop('modified_date')
        film_query[0].pop('id')
        film_query[0]['locations'] = film_locations

        response = self.client.get(reverse(_API_URL), {'where': 'title=%s' % film_name})
        api_query = json.loads(response.content.decode('utf-8'))
        api_query[0]['actors']  = ", ".join(api_query[0]['actors'])
        api_query[0]['writers'] = ", ".join(api_query[0]['writers'])

        self.assertEqual(film_query, api_query)

    def test_where_spaces_query(self):
        '''Test if a query with a where=title=[film_name_with_spaces] parameter matches the database'''
        film_name = '50 First Dates'  # Target a film with spaces, and an integer as all or part of the name

        film_query = list(Film.objects.filter(title=film_name).values())
        film_locations = list(FilmLocation.objects.filter(film__id=film_query[0]['id']).values())
        for film_location in film_locations:
            film_location.pop('id')
            film_location.pop('film_id')
        film_query[0].pop('modified_date')
        film_query[0].pop('id')
        film_query[0]['locations'] = film_locations

        response = self.client.get(reverse(_API_URL), {'where': 'title=%s' % film_name})
        api_query = json.loads(response.content.decode('utf-8'))
        api_query[0]['actors']  = ", ".join(api_query[0]['actors'])
        api_query[0]['writers'] = ", ".join(api_query[0]['writers'])

        self.assertEqual(film_query, api_query)

    def test_where_general_query(self):
        '''Test if a query with a where=title=[general_film_term] parameter matches the database'''
        film_name = 'Night'  # Target a generic film term that will return >1 result

        film_query = list(Film.objects.filter(title__contains=film_name).values())
        for film_item in film_query:
            film_locations = list(FilmLocation.objects.filter(film__id=film_item['id']).values())
            for film_location in film_locations:
                film_location.pop('id')
                film_location.pop('film_id')
            film_item.pop('modified_date')
            film_item.pop('id')
            film_item['locations'] = film_locations

        response = self.client.get(reverse(_API_URL), {'where': 'title=%s' % film_name})
        api_query = json.loads(response.content.decode('utf-8'))
        for film_item in api_query:
            film_item['actors']  = ", ".join(film_item['actors'])
            film_item['writers'] = ", ".join(film_item['writers'])

        self.assertEqual(film_query, api_query)

    def tearDown(self):
        if os.path.isfile(self.log_file):
            os.remove(self.log_file)
