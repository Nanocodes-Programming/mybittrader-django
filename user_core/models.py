from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import date
User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    country = models.CharField(max_length=50,null=True,blank=True)
    image = models.ImageField(upload_to='profile_images', default='r.jpg')
    available_balance = models.FloatField(default=0)
    live_profit = models.FloatField(default=0)
    book_balance = models.FloatField(default=0)
    plan_name = models.CharField(max_length=50,null=True,blank=True)
    plan_days = models.IntegerField(default=0,null=True,blank=True)
    plan_end_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    plan_amount  = models.IntegerField(default=0,null=True,blank=True)
    # profit_list = models.TextField(null=True,blank=True)
    referral_price  = models.FloatField(default=0)
    referral_people  = models.FloatField(default=0)
    referred_by  = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return self.user.username 

class PendingDeposit(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    wallet_address = models.CharField(max_length=100)
    wallet_type  = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.user.username} has deposited this {self.amount}'
    
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
    amount = models.IntegerField(default=0)
    wallet_type  = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=100)
    usdt_amount = models.FloatField(default=0)
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
                
                
            elif self.wallet_type == 'litecoin':
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
                
            elif self.wallet_type == 'xrp':
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
            
            else:
                action = f'{self.profile.user.username} has deposited {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Deposit Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
        return super().save(*args, **kwargs)

    
class WalletAddress(models.Model):
    bitcoin_address  = models.CharField(max_length=100)
    litecoin_address  = models.CharField(max_length=100)
    xrp_address  = models.CharField(max_length=100)
    etherum_address  = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.id)
    
    
class Withdraw(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    wallet_type  = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=100)
    usdt_amount = models.FloatField(default=0)
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
                
                
            elif self.wallet_type == 'litecoin':
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
                
            elif self.wallet_type == 'xrp':
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
            
            else:
                action = f'{self.profile.user.username} has withdrawn {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Withdrawal Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
        return super().save(*args, **kwargs)

class Transfer(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    wallet_type  = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=100)
    usdt_amount = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.profile.user.username} has transferred this {self.amount}-{self.verified}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            self.profile.available_balance -= self.usdt_amount
            self.profile.save()
            if self.wallet_type == 'bitcoin':
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
                
            elif self.wallet_type == 'litecoin':
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
                
            elif self.wallet_type == 'xrp':
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
            
            else:
                action = f'{self.profile.user.username} has transferred {self.amount} {self.wallet_type} into {self.wallet_address}'
                action_title = 'Transfer Verified'
                self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
                
        return super().save(*args, **kwargs)
    
    
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
    investment_profit_percent = models.FloatField(default=0)
    referral_profit_percent = models.FloatField(default=0)
    def __str__(self):
        return self.plan_name
    
class Referral(models.Model):
    profile = models.ForeignKey(Profile,related_name="referrals", on_delete=models.CASCADE)
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
    phone_number = models.IntegerField(null=True,blank=True,default=0)
    owned_by = models.CharField(max_length=50,null=True,blank=True,default='Admin')
    
    def __str__(self):
        return f'{self.name}'