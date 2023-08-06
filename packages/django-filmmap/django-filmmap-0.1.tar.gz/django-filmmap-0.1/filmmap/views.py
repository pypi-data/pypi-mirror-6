from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from filmmap.models import Film, FilmLocation
import json

def index(request):
    return render(request, 'filmmap/index.html', {'hello':'world'})

def api_v1(request):
    context = {}
    films = Film.objects.all()

    if request.GET.get('where'):
        where_parameters = request.GET.get('where').split(' and ')
        parameters = dict(where_parameter.split("=") for where_parameter in where_parameters)
        if parameters.get('title'):
            films = films.filter(title__contains=parameters.get('title'))
        if parameters.get('production_company'):
            films = films.filter(production_company__contains=parameters.get('production_company'))
        if parameters.get('distributor'):
            films = films.filter(distributor__contains=parameters.get('distributor'))
        if parameters.get('release_year'):
            films = films.filter(release_year__contains=parameters.get('release_year'))
        if parameters.get('director'):
            films = films.filter(director__contains=parameters.get('director'))
        if parameters.get('actors'):
            actors = [actor.strip() for actor in parameters.get('actors').split(',')]
            for actor in actors:
                films = films.filter(actors__contains=actor)
        if parameters.get('writers'):
            writers = [writer.strip() for writer in parameters.get('writers').split(',')]
            for writer in writers:
                films = films.filter(writers__contains=writer)

        if parameters.get('location'):
            films = films.filter(filmlocation__location=parameters.get('location'))
        if parameters.get('fun_facts'):
            films = films.filter(filmlocation__fun_facts=parameters.get('fun_facts'))

    if request.GET.get('order'):
        parameters = [parameter.replace('location', 'filmlocation__location').strip() 
                      if parameter.strip(' -').startswith('location') or parameter.strip(' -').startswith('fun_facts') 
                      else parameter.strip() for parameter in request.GET.get('order').split(',')]
        try:
            films = films.order_by(*parameters)
        except FieldError:
            pass

    if request.GET.get('limit') and request.GET.get('limit').isdigit():
        limit = int(request.GET.get('limit'))
        if 0 < limit < films.count():
            films = films[0:limit]

    select_parameters = location_parameters = None
    if request.GET.get('select'):
        select_parameters = [parameter.strip() for parameter in request.GET.get('select').split(',')
                      if not parameter.strip().startswith('location') and 
                      not parameter.strip().startswith('fun_facts')]
        if 'title' not in select_parameters:
            select_parameters.append('title')
        location_parameters = [parameter.strip() for parameter in request.GET.get('select').split(',')
                               if parameter.strip().startswith('location') or
                               parameter.strip().startswith('fun_facts')]
        if select_parameters:
            try:
                films = films.values(*select_parameters)
            except FieldError:
                films = films.values()
        else:
            films = films.values()
    else:
        films = films.values()

    '''
    *Final formatting*
    Parse select statement, remove id and date fields, and 
    create writers, actors, and locations lists where appropriate.
    '''
    query = []
    for film in films:
        locations = {}
        if not select_parameters or (select_parameters and location_parameters):
            try:
                locations = FilmLocation.objects.filter(film__title=film['title']).values()
                for location in locations:
                    location.pop('id')
                    location.pop('film_id')

                    if location_parameters and not 'location' in location_parameters:
                        location.pop('location')
                    if location_parameters and not 'fun_facts' in location_parameters:
                        location.pop('fun_facts')
            except KeyError:
                pass

            film['locations'] = list(locations)

        if not select_parameters or (select_parameters and 'writers' in select_parameters):
            film['writers'] = [writer for writer in film['writers'].split(', ')]
        if not select_parameters or (select_parameters and 'actors' in select_parameters):
            film['actors'] = [actor for actor in film['actors'].split(', ')]

        if film.get('id'):
            film.pop('id')
        if film.get('modified_date'):
            film.pop('modified_date')

        query.append(film)

    return HttpResponse(json.dumps(query), content_type="application/json")
