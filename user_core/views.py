from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import WalletAddress,Deposit,Profile,Notification,Withdraw,Transfer, Transaction, InvestmentPlan,Referral,Site, Kyc
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import timedelta,date
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
User = get_user_model()
# Create your views here.

def send_email(subject,body,recipient):
    site = Site.objects.get(pk=1)
    name = site.name
    address = site.address
    phone_number = site.phone_number
    context ={
        "title": subject,
        "content":body,
        "name": name,
        "address": address,
        "phone_number":phone_number
        }   
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER ,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


import datetime 
import pytz 




@login_required(login_url='/accounts/login')
def user_index(request):
    user = User.objects.get(username=request.user.username)
    try:
        site = Site.objects.get(pk=1)
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1)
        site.save()

    if not Profile.objects.filter(user=user.id).exists():
        return redirect('/user/profile')

    profile = Profile.objects.get(user=user)
    notifications_unread_count = Notification.objects.filter(
        profile=profile, read='False').count()
    notifications_unread = Notification.objects.filter(
        profile=profile, read='False').order_by('-time')[:3]
    transactions = Transaction.objects.filter(profile=profile).order_by('-time')[:3]
    # Convert plan_amount to a float
    plan_amount = profile.plan_amount 

    if profile.plan_name:
        plan = InvestmentPlan.objects.get(plan_name=profile.plan_name)
        today = datetime.datetime.today().astimezone(None)
        plan_end_date = profile.plan_end_date.astimezone(None)
        time_difference_days = plan_end_date - today
        time_difference = time_difference_days.days

        if time_difference > 0:
            live_profit = (
                plan_amount * plan.investment_profit_percent) / 100
            live_profit = live_profit / time_difference
            book_balance = profile.book_balance + live_profit
        else:
            live_profit = (plan_amount * plan.investment_profit_percent) / 100
            book_balance = profile.book_balance + live_profit
            profile.live_profit = live_profit
            profile.book_balance = book_balance
            profile.plan_name = None
            profile.plan_days = None
            profile.plan_end_date = None
            plan_amount = None
            profile.save()
    else:
        live_profit = profile.live_profit
        book_balance = profile.book_balance

    context = {
        'profile': profile,
        'live_profit': live_profit,
        'book_balance': book_balance,
        'notifications_unread_count': notifications_unread_count,
        'transactions': transactions,
        'notifications_unread': notifications_unread,
        'site': site,
    }
    return render(request, 'user/index.html', context)


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
def user_kyc(request):
    profile = Profile.objects.get(user=request.user)
    # instance = Kyc.objects.get(user=request.user)
    # verified = instance.verified
    try:
        instance = Kyc.objects.get(user=request.user)
        verified = instance.verified
    except Kyc.DoesNotExist:
        instance = None
        verified = False
    if request.method == 'POST':
        user = request.user
        country = request.POST['country']
        Id_type = request.FILES.get('Id_type')
        first_name = request.POST['f_name']
        last_name = request.POST['l_name']
        address = request.POST['address']
        proof_address = request.FILES.get('poa')


        if Kyc.objects.filter(user=user).exists():
            profile = Kyc.objects.get(user=user)
            profile.country = country
            profile.Id_type = Id_type
            profile.first_name = first_name
            profile.last_name = last_name
            profile.address = address
            profile.proof_address = proof_address
            profile.save()
            action_title = "Details submitted for kyc"
            action = "Pending Verification"
            notification = Notification.objects.create(profile=profile,action_title=action_title,action=action)
            notification.save()
        else:
            profile = Kyc.objects.create(user=user,country=country, Id_type=Id_type, first_name=first_name, last_name=last_name, address=address, proof_address=proof_address)
            profile.save()
        
        return redirect('/user/')

    else:
        user = request.user
    return render(request,'user/kyc.html', {'user': user, 'profile': profile, 'verified': verified})


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
    try:
        wallet = WalletAddress.objects.get(id=1)
    except WalletAddress.DoesNotExist:
        wallet = WalletAddress.objects.create(pk=1)
        wallet.save()
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
        action = f'You have deposited {amount} {wallet_type} into {wallet_address}'
        action_title = 'Deposit Pending'
        notification = Notification.objects.create(profile=profile,action_title=action_title,action=action)
        notification.save()
        transaction = Transaction.objects.create(profile=profile,category='deposit',action_title='Deposit Requested',action=action)
        transaction.save()
        body = f'{profile.user.username} has deposited {deposit.amount} {deposit.wallet_type} into {deposit.wallet_address}'
        body_two = f'You have deposited {deposit.amount} {deposit.wallet_type} into {deposit.wallet_address}'
        subject = 'Deposit Requested'
        # send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        # send_mail(subject=subject,message=body_two,from_email=settings.EMAIL_HOST_USER,recipient_list=[request.user.email])
        send_email(subject,body,settings.RECIPIENT_ADDRESS)
        
        send_email(subject,body_two,request.user.email)
        messages.info(request, 'You have applied for a deposit')
        return redirect('/user/deposit')
        
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
        profile.save
        if int(amount) > profile.available_balance:
            messages.info(request, 'You do not have enough funds')
            return render(request,'user/plans.html',context)
        if profile.live_profit:
            messages.info(request, 'You already have an existing plan')
            return render(request,'user/plans.html',context)
        plan = InvestmentPlan.objects.get(plan_name=plan_name)
        profile.plan_name = plan_name
        profile.plan_days = plan.number_of_days
        today = datetime.datetime.today().astimezone(None)
        profile.plan_end_date = today +timedelta(days=plan.number_of_days)
        profile.plan_amount = amount
        referred_user = profile.referred_by
        if referred_user:
            user_model = User.objects.get(username=referred_user)
            user_profile = Profile.objects.get(user=user_model)
            referralPrice = plan.referral_profit_percent * amount
            user_profile.referralPrice += referralPrice
            user_profile.available_balance += referralPrice
            user_profile.save()
            send_email("Referral Gain",f'Your referral gain is {referralPrice} from {request.user.username}',settings.RECIPIENT_ADDRESS)

        profile.save()
        messages.info(request, 'You have applied for the ' + plan_name + ' plan ')
        send_email('You have applied for the ' + plan_name + ' plan ',plan_name,request.user.email)
        return redirect('/user/plans')
    # profile.save()
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
        messages.info(request, 'Your email has been sent')
        #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        send_email(subject,body,settings.RECIPIENT_ADDRESS)
        return redirect('/user/support')
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
    on_development = True
    sender_user = User.objects.get(username=request.user.username)
    sender_profile = Profile.objects.get(user=sender_user)
    notifications_unread_count = Notification.objects.filter(
        profile=sender_profile, read=False).count()
    notifications_unread = Notification.objects.filter(
        profile=sender_profile, read=False).order_by("-time")[:3]
    transfers = Transfer.objects.filter(
        sender=sender_profile).order_by("-time")[:5]
    wallet, created = WalletAddress.objects.get_or_create(id=1)
    site, created = Site.objects.get_or_create(id=1)
    context = {
        "profile": sender_profile,
        "wallet": wallet,
        "transfers": transfers,
        "notifications_unread_count": notifications_unread_count,
        "notifications_unread": notifications_unread,
        "site": site,
        'on_development' : on_development
    }
    if request.method == "POST":
        receiver_username = request.POST.get("username", None)
        if not receiver_username:
            messages.info(request, "You did not include a receiver username")
            return redirect("/user/")

        try:
            receiver_user = User.objects.get(username=receiver_username)
            receiver_profile = Profile.objects.get(user=receiver_user)
            amount = request.POST.get("amount", None)
            username = request.POST.get("username", None)
            usdt_amount = float(request.POST.get("usdt_amount", 0))
            if usdt_amount > sender_profile.available_balance:
                messages.info(request, "You have insufficient funds")
                return redirect("/user/")
            
            transfer = Transfer.objects.create(
                sender=sender_profile,
                receiver=receiver_profile,
                amount=usdt_amount,
                usdt_amount=usdt_amount,
                username=username
            )
            action = f"You have transferred {usdt_amount} Units of USD to {receiver_username}"
            action_title = "Transfer Successful"
            notification = Notification.objects.create(
                profile=sender_profile,
                action_title=action_title,
                action=action
            )
            transaction = Transaction.objects.create(
                profile=sender_profile,
                category="transfer",
                action_title="Transfer Requested",
                action=action
            )
            body = f"{sender_profile.user.username} has transferred {transfer.amount}USD to {receiver_profile.user.username}"
            body_two = f"You have transferred {transfer.amount}USD to {receiver_profile.user.username}"
            body_three = f"{sender_profile.user.username} has transferred {transfer.amount} USD to you"
            subject = "Transfer Requested"
            send_email(subject, body, settings.RECIPIENT_ADDRESS)
            send_email(subject, body_two, request.user.email)
            send_email(subject, body_three, receiver_profile.user.email)
            messages.info(request, 'You have applied for a transfer')
            return redirect('/user/transfer')

        except User.DoesNotExist:
            messages.info(request, 'The user does not exist')
            return redirect('/user/transfer')
        
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
    try:
        wallet = WalletAddress.objects.get(id=1)
    except WalletAddress.DoesNotExist:
        wallet = WalletAddress.objects.create(pk=1)
        wallet.save()
    context = {
        'profile':profile,
        'wallet':wallet,
        'withdraws': withdraws,
        'notifications_unread_count':notifications_unread_count,
        'notifications_unread': notifications_unread,
        'site':site
    }
    if request.method == 'POST':
        # if profile.plan_name:
        #     messages.info(request, 'You have an existing plan')
        #     return render(request,'user/withdraw.html',context)
        wallet_address = request.POST['wallet_address']
        if wallet_address == None or wallet_address =='':
            messages.info(request, 'You did not add a withdrawal address')
            return redirect('/user/withdraw')
        amount = request.POST['amount']
        wallet_type = request.POST['wallet_type']
        usdt_amount = request.POST['usdt_amount']
        if float(usdt_amount) > profile.available_balance:
            messages.info(request, 'Your have insufficient funds')
            return redirect('/user/withdraw')
            
        withdraw = Withdraw.objects.create(profile=profile,amount=amount,wallet_type=wallet_type,wallet_address=wallet_address,usdt_amount=usdt_amount)
        withdraw.save()
        action = f'You has withdrawn {amount} {wallet_type} into {wallet_address}'
        action_title = 'Withdrawal Pending'
        notification = Notification.objects.create(profile=profile,action_title=action_title,action=action)
        notification.save()
        transaction = Transaction.objects.create(profile=profile,category='withdraw',action_title='Withdraw Requested',action=action)
        transaction.save()
        body = f'{profile.user.username} has withdrawn {withdraw.amount} {withdraw.wallet_type} into {withdraw.wallet_address}'
        body_two = f'You have withdrawn {withdraw.amount} {withdraw.wallet_type} into {withdraw.wallet_address}'
        subject = 'Withdrawal Requested'
        #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[settings.RECIPIENT_ADDRESS])
        #send_mail(subject=subject,message=body_two,from_email=settings.EMAIL_HOST_USER,recipient_list=[request.user.email])
        send_email(subject,body,settings.RECIPIENT_ADDRESS)
        send_email(subject,body_two,request.user.email)
        messages.info(request, 'You have applied for withdrawal')
        return redirect('/user/withdraw')
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