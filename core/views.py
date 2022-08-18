from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from core.drivers.dbDriver import App
import core.drivers.localDriver as ld
import core.drivers.config as c
import json

app = App(c.uri, c.user, c.password)

def query_engine(request):
    return render(request, 'query.html')

def database_manager(request):
    return render(request, 'database.html')

def get_donor(request, donor_id):

    Donors = ld.load_Donors()

    if donor_id in Donors:
        return JsonResponse(Donors[donor_id])
    else:
        return HttpResponse(f'{donor_id} not found')

def get_Interests(request):

    Interests = ld.load_Interests()
    return JsonResponse(Interests)


def run_command(request, command):
    # This is a way for us to say - your command was invalid
    # and this is a way for us to create something exportable
    # based on the query
    result = app.run(command)
    return JsonResponse(json.dumps(result), safe=False)