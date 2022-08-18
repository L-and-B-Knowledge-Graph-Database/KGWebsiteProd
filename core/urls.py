"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.login_page),
    path('set/', views.set_neo4j_params),
    path('query/', views.query_engine),
    path('query/export/', views.get_file),
    path('manage/', views.database_manager),
    path('manage/test/', views.test_database),
    path('manage/update/', views.update_database),
    path('manage/clear/', views.clear_database),
    path('load/', views.load_donors_and_interests),
    path('manage/load/', views.load_donors_and_interests),
    path('docs/', views.docs_page),
    path('stats/', views.stats_page),
    path('interests/', views.get_Interests),
    path('create/cypher/', views.make_cypher_command),
    path('cypher/<str:command>/', views.run_command),
    path('admin/', admin.site.urls)
]
