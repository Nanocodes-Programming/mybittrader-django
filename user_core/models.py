from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
User = get_user_model()

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

# Create your models here.
class Kyc(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    country = models.CharField(max_length=50,null=True,blank=True)
    Id_type = models.FileField(upload_to='kyc_documents', default='kyc.pdf')
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    proof_address = models.FileField(upload_to='kyc_documents' )
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} has submitted documents for kyc'
# date import


import datetime 
import pytz 


from decimal import *
from datetime import timedelta
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images', default=' ')
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    live_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    book_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    plan_name = models.CharField(max_length=50, null=True, blank=True)
    plan_days = models.IntegerField(default=0, null=True, blank=True)
    plan_end_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    plan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    referral_people = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    referred_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def calculate_live_profit_and_book_balance(self):
        if self.plan_name:
            plan = InvestmentPlan.objects.get(plan_name=self.plan_name)
            today = datetime.datetime.today().astimezone(None)
            plan_end_date = today + timedelta(days=plan.number_of_days)
            self.available_balance = self.available_balance
            self.plan_amount = Decimal(self.plan_amount)

            time_difference_days = plan_end_date - today
            time_difference = time_difference_days.days
            self.available_balance -= self.plan_amount

            if time_difference > 0:
                self.live_profit = (self.plan_amount * plan.investment_profit_percent) / 100
                self.live_profit = self.live_profit / time_difference
                self.book_balance = self.live_profit + self.available_balance + self.plan_amount
                self.plan_name = plan.plan_name
                self.plan_days = plan.number_of_days
                self.plan_end_date = today + timedelta(days=plan.number_of_days)
                self.plan_amount = Decimal(self.plan_amount)
            else:
                self.live_profit = (self.plan_amount * plan.investment_profit_percent) / 100
                self.book_balance = self.live_profit + self.available_balance + self.plan_amount
                self.plan_name = None
                self.plan_days = None
                self.plan_end_date = None
                self.plan_amount = None
                self.save()
        else:
            self.live_profit = self.live_profit
            self.book_balance = self.book_balance
            self.available_balance = self.available_balance



    def save(self, *args, **kwargs):
        self.calculate_live_profit_and_book_balance()
        super().save(*args, **kwargs)

   
# class PendingDeposit(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     time = models.DateTimeField(auto_now_add=True)
#     amount = models.IntegerField(default=0)
#     wallet_address = models.CharField(max_length=100)
#     wallet_type  = models.CharField(max_length=50)
    
#     def __str__(self):
#         return f'{self.user.username} has deposited this {self.amount}'
    
class Notification(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    action = models.TextField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    action_title = models.CharField(max_length=100,blank=True,null=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.profile.user.username} - {self.action}'  
    
class Deposit(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20,decimal_places=5,blank=True,null=True)
    wallet_type  = models.CharField(max_length=50,blank=True,null=True)
    wallet_address = models.CharField(max_length=100,blank=True,null=True)
    usdt_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.profile.user.username} has deposited this {self.amount}-{self.verified}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            self.profile.available_balance += self.usdt_amount
            self.profile.save()
            if self.wallet_type == 'bitcoin':
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your deposit of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
                
            elif self.wallet_type == 'litecoin':
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your deposit of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
            
            elif self.wallet_type == 'USDT':
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your deposit of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
            elif self.wallet_type == 'xrp':
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your deposit of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
            
            else:
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your deposit of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
        return super().save(*args, **kwargs)

    
class WalletAddress(models.Model):
    bitcoin_address  = models.CharField(max_length=200,blank=True,null=True)
    litecoin_address  = models.CharField(max_length=200,blank=True,null=True)
    xrp_address  = models.CharField(max_length=200,blank=True,null=True)
    etherum_address  = models.CharField(max_length=200,blank=True,null=True)
    usdt_address  = models.CharField(max_length=200,blank=True,null=True)
    address = models.CharField(max_length=100,default='Wallet Address')
    
    def __str__(self):
        return str(self.id)
    
    
class Withdraw(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wallet_type  = models.CharField(max_length=50,blank=True,null=True)
    wallet_address = models.CharField(max_length=100,blank=True,null=True)
    usdt_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.profile.user.username} has withdrawn this {self.amount}-{self.verified}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            self.profile.available_balance -= self.usdt_amount
            self.profile.save()
            if self.wallet_type == 'bitcoin':
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your withdrawal of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
            elif self.wallet_type == 'litecoin':
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your withdrawal of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
            elif self.wallet_type == 'USDT':
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your withdrawal of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                    
            elif self.wallet_type == 'xrp':
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your withdrawal of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
            
            else:
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your withdrawal of {self.amount} {self.wallet_type} to {self.wallet_address} has been verfied'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
        return super().save(*args, **kwargs)

class Transfer(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender', null=True)
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver', null=True)
    time = models.DateTimeField(auto_now_add=True)
    amount =  models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    # wallet_type  = models.CharField(max_length=50,blank=True,null=True)
    # email_address = models.EmailField(blank=True,null=True)
    # username = models.CharField(max_length=100,blank=True,null=True)
    usdt_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified = models.BooleanField(default=True)
    
    def __str__(self):
         return f"{self.sender} transferred {self.amount} to {self.receiver} on {self.time}"
    
    def save(self, *args, **kwargs):
        if self.verified:
            self.sender.available_balance -= self.usdt_amount
            self.receiver.available_balance += self.usdt_amount
            self.save()

            # Add the transferred amount to the receiver wallet
            # receiver_profile = Profile.objects.get(user=self.username)
            # receiver_profile.available_balance -= float(self.usdt_amount)
            # receiver_profile.save()

            if self.wallet_type == 'bitcoin':
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} to {self.email_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your transfer of {self.amount} {self.wallet_type} to {self.profile.email} has been verified'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
            elif self.wallet_type == 'litecoin':
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} to {self.email_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your transfer of {self.amount} {self.wallet_type} to {self.email_address} has been verified'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
                
            elif self.wallet_type == 'xrp':
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} to {self.email_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your transfer of {self.amount} {self.wallet_type} to {self.email_address} has been verified'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
            
            else:
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} to {self.email_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                subject = action_title
                body = f'Your transfer of {self.amount} {self.wallet_type} to {self.email_address} has been verified'
                #send_mail(subject=subject,message=body,from_email=settings.EMAIL_HOST_USER,recipient_list=[self.profile.user.email])
                send_email(subject,body,self.profile.user.email)
                
        return super().save(*args, **kwargs)

# class Transfer(models.Model):
#     profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
#     time = models.DateTimeField(auto_now_add=True)
#     amount = models.IntegerField(default=0)
#     wallet_type  = models.CharField(max_length=50)
#     wallet_address = models.CharField(max_length=100)
#     usdt_amount = models.FloatField(default=0)
#     verified = models.BooleanField(default=False)
    
#     def __str__(self):
#         return f'{self.profile.user.username} has transferred this {self.amount}-{self.verified}'
    
#     def save(self, *args, **kwargs):
#         if self.verified:
#             self.profile.available_balance -= self.usdt_amount
#             self.profile.save()
#             if self.wallet_type == 'bitcoin':
#                 action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
#                 action_title = 'Transfer Verified'
#                 self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
                
#             elif self.wallet_type == 'litecoin':
#                 action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
#                 action_title = 'Transfer Verified'
#                 self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
                
#             elif self.wallet_type == 'xrp':
#                 action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
#                 action_title = 'Transfer Verified'
#                 self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
            
#             else:
#                 action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
#                 action_title = 'Transfer Verified'
#                 self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
#         return super().save(*args, **kwargs)
    
    
    
class Transaction(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    action = models.TextField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    action_title = models.CharField(max_length=100,blank=True,null=True)
    category = models.CharField(max_length=50,blank=True,null=True)
    
    def __str__(self):
        return f'{self.profile.user.username} - {self.action}'


class InvestmentPlan (models.Model):
    plan_name = models.CharField(max_length=50,null=True,blank=True)
    investment_amount_highest = models.IntegerField(default=0)
    investment_amount_lowest = models.IntegerField(default=0)
    number_of_days = models.IntegerField(default=0)
    investment_profit_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    referral_profit_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # type = models.ForeignKey(PlanType, on_delete=models.CASCADE)

    def __str__(self):
        return self.plan_name
    


class Investment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    investment = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)


class Referral(models.Model):
    profile = models.ForeignKey(Profile, related_name="referrals", on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.profile.user.username} referred {self.username}'
    
class Site(models.Model):
    name = models.CharField(max_length=50,null=True,blank=True,default='Blank Name')
    email = models.EmailField(null=True,blank=True,default='Blank Email')
    address = models.CharField(max_length=300,null=True,blank=True,default='Blank Address')
    second_address = models.CharField(max_length=300,null=True,blank=True,default='Blank Address')
    logo = models.ImageField(upload_to='site_images', default='logo.png')
    phone_number = models.CharField(max_length=100, blank=True)
    owned_by = models.CharField(max_length=50,null=True,blank=True,default='Admin')
    
    def __str__(self):
        return f'{self.name}'

class SendEmail(models.Model):
    email = models.EmailField(null=True,blank=True)
    username = models.CharField(max_length=200,null=True,blank=True)
    subject = models.CharField(max_length=300,null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    
    def __str__(self):
        return f'{self.email}'
    
    def save(self, *args, **kwargs):
        send_email(self.subject,self.content,self.email)
        self.subject = ""
        self.content = ""
        return super().save(*args, **kwargs)
    
    