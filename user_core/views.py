from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import WalletAddress,Deposit,Profile,Notification,Withdraw,Transfer, Transaction, InvestmentPlan,Referral,Site
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import timedelta,date
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()
# Create your views here.

@login_required(login_url='/accounts/login')
def user_index(request):
    
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    live_profit = 0.00
    book_balance = 0.00
    transactions = Transaction.objects.filter(profile=profile).order_by('-time')[:3]
    if profile.plan_name != None:
        plan = InvestmentPlan.objects.get(plan_name=profile.plan_name)
        plan_end_date = profile.plan_end_date
        time_difference_days = plan_end_date - date.today()
        time_difference = time_difference_days.days
        
        if time_difference > 0:
            live_profit = (profile.plan_amount * plan.investment_profit_percent) / 100
            live_profit = live_profit / time_difference
            book_balance = live_profit + profile.available_balance
            
        else:
            profile.live_profit = (profile.plan_amount * plan.investment_profit_percent) / 100
            profile.book_balance = profile.live_profit + profile.available_balance
            profile.available_balance = profile.book_balance
            profile.plan_name = None
            profile.plan_days = None
            profile.plan_end_date = None
            profile.plan_amount = None
            profile.save()
            

    context = {
        'profile':profile,
        'live_profit': live_profit,
        'book_balance': book_balance,
        'notifications_unread_count':notifications_unread_count,
        'transactions':transactions,
        'notifications_unread': notifications_unread,
        'site':site
    }
    return render(request,'user/index.html',context)


@login_required(login_url='/accounts/login')
def user_profile(request):
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    user = User.objects.get(username = request.user.username)
    profile = None
    try:
        referred_by = request.session['referred_by']
    except:
        referred_by = None
    if referred_by:        
        try:
            referred_user = User.objects.get(username=referred_by)
        except User.DoesNotExist:
            referred_user = None
        
        if referred_user:
            profile = Profile.objects.get(user=referred_user)
            referral = Referral.objects.create(profile=profile,username=request.user.username)
            
            profile.referral_people += 1
            
            profile.save()
            referral.save()
        request.session['referred_by'] = None
    notifications_unread_count = 0
    if not Profile.objects.filter(user= user.id):
        notifications_unread_count = 0
        notifications_unread = None
    else:
        profile = Profile.objects.get(user=user)
        notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
        notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    
    context = {
        'notifications_unread_count':notifications_unread_count,
        'profile':profile,
        'notifications_unread': notifications_unread,
        'site':site
    }
    
    if request.method == 'POST':
        country = request.POST['country']
        image = request.FILES.get('image')
        user = User.objects.get(username = request.user.username)
        
        if Profile.objects.filter(user= user.id):
            profile = Profile.objects.get(user=user)
            profile.country = country
            profile.image = image
            profile.save()
        else:
            profile = Profile.objects.create(user=user,country=country,image=image)
            profile.save()
        
        return redirect('/user/')
        
    return render(request,'user/profile.html')


@login_required(login_url='/accounts/login')
def user_deposit(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    deposits = Deposit.objects.filter(profile=profile).order_by('-time')[:5]
    wallet = WalletAddress.objects.get(id=1)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    context = {
        'wallet':wallet,
        'deposits': deposits,
        'profile':profile,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    if request.method == 'POST':
        wallet_address = request.POST['wallet_address']
        amount = request.POST['amount']
        wallet_type = request.POST['wallet_type']
        usdt_amount = request.POST['usdt_amount']
        deposit = Deposit.objects.create(profile=profile,amount=amount,wallet_type=wallet_type,wallet_address=wallet_address,usdt_amount=usdt_amount)
        deposit.save()
        action = f'{request.user.username} has deposited {amount} {wallet_type} into {wallet_address}'
        action_title = 'Deposit Pending'
        notification = Notification.objects.create(profile=profile,action_title=action_title,action=action)
        notification.save()
        transaction = Transaction.objects.create(profile=profile,category='deposit',action_title='Deposit Requested',action=action)
        transaction.save()
        body = f'{profile.user.username} has deposited {deposit.amount} {deposit.wallet_type} into {deposit.wallet_address}'
        subject = 'Deposit Requested'
        send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        
        return redirect('/user/')
        
    return render(request,'user/deposit.html',context)


@login_required(login_url='/accounts/login')
def user_notification(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unreads = Notification.objects.filter(profile=profile,read='False').order_by('-time')
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    notifications = Notification.objects.filter(profile=profile).order_by('-time')
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    #idea on read new, add the read = false to a variable and exclude it from the remaining array
    for notification in notifications_unreads:
        notification.read = 'True'
        notification.save()
    context = {
        'notifications':notifications,
        'profile':profile,
        'notifications_unreads': notifications_unreads,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
        
    }
    return render(request,'user/notification.html',context)


@login_required(login_url='/accounts/login')
def user_plans(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    plans = InvestmentPlan.objects.all()
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    context = {
        'plans':plans,
        'profile':profile,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    if request.method == 'POST':
        amount = request.POST['amount']
        plan_name = request.POST['plan_name']
        profile = Profile.objects.get(user=user)
        if int(amount) > profile.available_balance:
            messages.info(request, 'You do not have enough funds')
            return render(request,'user/plans.html',context)
        if profile.plan_name:
            messages.info(request, 'You already have an existing plan')
            return render(request,'user/plans.html',context)
        plan = InvestmentPlan.objects.get(plan_name=plan_name)
        profile.plan_name = plan_name
        profile.plan_days = plan.number_of_days
        profile.plan_end_date = date.today()+timedelta(days=plan.number_of_days)
        profile.plan_amount = amount
        referred_user = profile.referred_by
        if referred_user:
            profile = Profile.objects.get(user=referred_user)
            referralPrice = plan.referral_profit_percent * amount
            profile.referralPrice += referralPrice
            profile.available_balance += referralPrice
            profile.save()
        profile.save()
        return redirect('/user/')
        
    return render(request,'user/plans.html',context)


@login_required(login_url='/accounts/login')
def user_ref(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    referrals = Referral.objects.filter(profile=profile)
    
    context = {
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'referrals':referrals,
        'profile':profile,
        'site':site
    }
    return render(request,'user/ref.html',context)


@login_required(login_url='/accounts/login')
def user_support(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    
    context = {
        'profile':profile,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    if request.method == 'POST':
        body = request.POST['body']
        subject = request.POST['subject']
        send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        return redirect('/user/')
    return render(request,'user/support.html',context)


@login_required(login_url='/accounts/login')
def user_transaction(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
           
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    transactions = Transaction.objects.filter(profile=profile).order_by('-time')
    category = request.GET.get('category')
    if category:
        transactions = Transaction.objects.filter(profile=profile,category=category).order_by('-time')
    
    context = {
        'profile':profile,
        'transactions':transactions,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    return render(request,'user/transaction.html',context)


@login_required(login_url='/accounts/login')
def user_transfer(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    transfers = Transfer.objects.filter(profile=profile).order_by('-time')[:5]
    wallet = WalletAddress.objects.get(id=1)
    context = {
        'profile':profile,
        'wallet':wallet,
        'transfers': transfers,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    if request.method == 'POST':
        if profile.plan_name:
            messages.info(request, 'You have an existing plan')
            return render(request,'user/transfer.html',context)
        wallet_address = request.POST['wallet_address']
        amount = request.POST['amount']
        wallet_type = request.POST['wallet_type']
        usdt_amount = request.POST['usdt_amount']
        transfer = Transfer.objects.create(profile=profile,amount=amount,wallet_type=wallet_type,wallet_address=wallet_address,usdt_amount=usdt_amount)
        transfer.save()
        action = f'{request.user.username} has transferred {amount} {wallet_type} into {wallet_address}'
        action_title = 'Transfer Pending'
        notification = Notification.objects.create(profile=profile,action_title=action_title,action=action)
        notification.save()
        transaction = Transaction.objects.create(profile=profile,category='transfer',action_title='Transfer Requested',action=action)
        transaction.save()
        body = f'{profile.user.username} has transferred {transfer.amount} {transfer.wallet_type} into {transfer.wallet_address}'
        subject = 'Transfer Requested'
        send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        
        return redirect('/user/')
    return render(request,'user/transfer.html',context)


@login_required(login_url='/accounts/login')
def user_withdraw(request):
    user = User.objects.get(username = request.user.username)
    
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if not Profile.objects.filter(user= user.id):
        return redirect('/user/profile')
    
    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(profile=profile,read='False').count()
    notifications_unread = Notification.objects.filter(profile=profile,read='False').order_by('-time')[:3]
    withdraws = Withdraw.objects.filter(profile=profile).order_by('-time')[:5]
    wallet = WalletAddress.objects.get(id=1)
    context = {
        'profile':profile,
        'wallet':wallet,
        'withdraws': withdraws,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    if request.method == 'POST':
        if profile.plan_name:
            messages.info(request, 'You have an existing plan')
            return render(request,'user/withdraw.html',context)
        wallet_address = request.POST['wallet_address']
        amount = request.POST['amount']
        wallet_type = request.POST['wallet_type']
        usdt_amount = request.POST['usdt_amount']
        withdraw = Withdraw.objects.create(profile=profile,amount=amount,wallet_type=wallet_type,wallet_address=wallet_address,usdt_amount=usdt_amount)
        withdraw.save()
        action = f'{request.user.username} has withdrawn {amount} {wallet_type} into {wallet_address}'
        action_title = 'Withdrawal Pending'
        notification = Notification.objects.create(profile=profile,action_title=action_title,action=action)
        notification.save()
        transaction = Transaction.objects.create(profile=profile,category='withdraw',action_title='Withdraw Requested',action=action)
        transaction.save()
        body = f'{profile.user.username} has withdrawn {withdraw.amount} {withdraw.wallet_type} into {withdraw.wallet_address}'
        subject = 'Withdrawal Requested'
        send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        
        return redirect('/user/')
    return render(request,'user/withdraw.html',context)


# send the referal to another then redirect to main registration link


def user_referral(request):
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()
        
    if request.user.username:
        return redirect('/user/ref')
    referred_by = request.GET.get('referred_by')
    if referred_by:
        request.session['referred_by'] = referred_by
        return redirect('/accounts/signup')
    if request.method == 'POST':
        referred_by = request.POST['referred_by']
        if referred_by:
            request.session['referred_by'] = referred_by
            return redirect('/accounts/signup')   
    context = {
        'site':site
    } 
    return render(request,'user/referral.html',context)

def my_custom_error_view(request):
    return render(request,'error.html')

def my_custom_page_not_found_view(request,exception):
    return render(request,'error.html')


def my_custom_bad_request_view(request,exception):
    return render(request,'error.html')


def my_custom_permission_denied_view(request,exception):
    return render(request,'error.html')

       

