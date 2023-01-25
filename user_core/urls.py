from django.urls import path
from . import views


urlpatterns = [
    path('',views.user_index, name='user_index'),
    path('deposit',views.user_deposit, name='user_deposit'),
    path('notification',views.user_notification, name='user_notification'),
    path('plans',views.user_plans, name='user_plans'),
    path('profile',views.user_profile, name='user_profile'),
    path('ref',views.user_ref, name='user_ref'),
    path('support',views.user_support, name='user_support'),
    path('transaction',views.user_transaction, name='user_transaction'),
    path('transfer',views.user_transfer, name='user_transfer'),
    path('referral',views.user_referral, name='user_referral'),
    path('withdraw',views.user_withdraw, name='user_withdraw'),
   
    
]
