from django.urls import path
from . import views


urlpatterns = [                   
                    path('about',views.about, name='about'),
                    path('contact',views.contact, name='contact'),
                    path('faqs',views.faqs, name='faqs'),
                    path('index_2',views.index_2, name='index_2'),
                    path('',views.index, name='index'),
                    path('plans',views.plans, name='plans'),
                    path('terms',views.terms, name='terms'),
                    
]
    #urls created                   
                        