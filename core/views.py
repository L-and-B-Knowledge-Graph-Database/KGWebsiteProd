from django.http import JsonResponse, HttpResponse
from core.drivers.dbDriver import App
from django.shortcuts import render
from io import StringIO
import core.drivers.test_drivers as t
import core.drivers.localDriver as ld
import core.drivers.helper as h
import core.drivers.config as c
import pandas as pd
import requests
import json
import os

def clear_database(request):
    app = App(os.environ["URI"].replace(' ', '+'), os.environ["USER"], os.environ["PASSWORD"])
    app.clear()
    return JsonResponse({'result':'done'})

def update_database(request):
    result, l_count, d_count = t.check_count(request)
    if result:
        print('no need to update, everything is equal')
        return JsonResponse({'result':'done'})
    else:
        app = App(os.environ["URI"].replace(' ', '+'), os.environ["USER"], os.environ["PASSWORD"])
        app.update_neo4j(request.session['Donors'], request.session['Interests'])
        app.close()
        return JsonResponse({'result':'done'})

def test_database(request):
    result, l_count, d_count = t.check_count(request)
    return JsonResponse({'result' : result, 'l_count' : l_count, 'd_count' : d_count})

def load_donors_and_interests(request):

    Donors, Interests, Links = ld.fetch_donors_and_interests_from_drive()

    request.session['Donors'] = Donors
    request.session['Interests'] = Interests
    request.session['Links'] = Links

    return JsonResponse({'loaded' : 'done'})


def set_neo4j_params(request):

    params = {}

    if request.method == 'GET':
        params = eval(request.GET.dict()['params'])
    else:
        params = eval(request.POST.dict()['params'])

    os.environ["URI"] = params['uri']
    os.environ["USER"] = params['username']
    os.environ["PASSWORD"] = params['password']

    return JsonResponse({'set' : 'done'})

def make_cypher_command(request):

    params = {}

    if request.method == 'GET':
        params = eval(request.GET.dict()['params'])
    else:
        print('ERROR : Request should have been a GET')
        return JsonResponse({'ERROR' : 'Request should have been a GET'})
    
    filters = []
    
    if params['donor_ids']:
        IDs = [int(x) for x in params['donor_ids'].replace(' ', '').split(',')]
        filters.append(f'a.ID IN {IDs} ')
    
    if params['donor_versions'] != 'Both':
        filters.append(f"a.Version = '{params['donor_versions']} Giving' ")

    if params['click_count']:
        filters.append(f"c.count {params['click_compare']} {int(params['click_count'])} ")

    if '' in params['interests']:
        params['interests'].remove('')

    if params['interests']:
        filters.append(f"b.Name IN {params['interests']} ")

    cypherCommand = 'MATCH (a:Donor)-[c:CLICKED]-(b:Interest) '
    if filters:
        cypherCommand += 'WHERE '
        for i in range(len(filters)):
            cypherCommand += filters[i]
            if i < (len(filters) - 1):
                cypherCommand += 'AND '
    cypherCommand += 'RETURN a, b, c'

    return JsonResponse({'command' : cypherCommand})

def get_file(request):

    command = ''

    if request.method == 'GET':
        command = eval(request.GET.dict()['command'])
    else:
        print('ERROR : Request should have been a GET')
        return JsonResponse({'ERROR' : 'Request should have been a GET'})

    result = run_command_here(command)
    pdOutput = h.get_click_data(result)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=filename.csv'

    pdOutput.to_csv(path_or_buf=response, sep=',', index=False)

    return response

def query_engine(request):
    rightURI = os.environ["URI"].replace(' s', '')
    model = {'uri' : rightURI, 'user' : os.environ["USER"], 'password' : os.environ["PASSWORD"]}
    return render(request, 'query.html', model)

def database_manager(request):
    return render(request, 'database.html')

def docs_page(request):
    return render(request, 'docs.html')

def login_page(request):
    return render(request, 'login.html')

def stats_page(request):
    context = {}
    interestCount = h.get_Interest_Count(request.session['Donors'], request.session['Interests'], request.session['Links'])
    context['graph1'] = h.show_AVP_graph(interestCount)
    return render(request, 'stats.html', context)

def get_Interests(request):
    return JsonResponse(request.session['Interests'])

def run_command(request, command):
    result = run_command_here(command)
    return JsonResponse(json.dumps(result), safe=False)

def run_command_here(command) :
    app = App(os.environ["URI"].replace(' ', '+'), os.environ["USER"], os.environ["PASSWORD"])
    return app.run(command)