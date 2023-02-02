from django.contrib import admin
from user_core.models import Profile,Referral,Notification,Deposit,WalletAddress,Withdraw,Transfer,InvestmentPlan,Site,SendEmail, Kyc
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
#from django.shortcuts import render,redirect
#
# class EmailForm(forms.Form):
#     subject = forms.CharField(max_length=100)
#     message = forms.CharField(widget=forms.Textarea)

# def send_email(modeladmin, request, queryset):
#     array = []
#     for user in queryset:
#         array.append(user.email)
#         redirect('/user/withdraw')
#     # form = None
#     # if 'apply' in request.POST:
#     #     form = EmailForm(request.POST)
#     #     if form.is_valid():
#     #         subject = form.cleaned_data['subject']
#     #         message = form.cleaned_data['message']
#     #         for user in queryset:
#     #             user.email_user(
#     #                 subject=subject,
#     #                 message=message,
#     #                 from_email=settings.EMAIL_HOST_USER,
#     #             )
#     # if not form:
#     #     form = EmailForm(initial={'_selected_action': request.POST.getlist('send email to selected users')})
#     # modeladmin.message_user(request, 'Email was sent')
#     # return form

# class UserAdmin(admin.ModelAdmin):
#     actions = [send_email]
#     send_email.short_description = "Send email to selected users"
#     send_email.allow_tags = True
#     send_email.template = 'admin/send_email.html'

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


# from django.contrib.auth.models import User
# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags

   
# def send_email(modeladmin, request, queryset):
#     for user in queryset:
#         user.email_user(
#             subject='Subject of the email',
#             message='Body of the email',
#             from_email=settings.EMAIL_HOST_USER ,
#         )

# class UserAdmin(admin.ModelAdmin):
#     actions = [send_email]

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('profile','wallet_address','amount','wallet_type','time','verified','usdt_amount')
    list_editable=  ('verified',)



@admin.register(WalletAddress)
class WalletAddressAdmin(admin.ModelAdmin):
    list_display = ('address','bitcoin_address','litecoin_address','xrp_address','etherum_address','usdt_address')
    list_editable=  ('bitcoin_address','litecoin_address','xrp_address','etherum_address','usdt_address')
    list_display_links = ('address',)
    
@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('profile','wallet_address','amount','wallet_type','time','verified')
    list_editable=  ('verified',)
    

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount','time','verified')
    list_editable=  ('verified',)
    


@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    pass

# @admin.register(PlanType)
# class PlanTypeAdmin(admin.ModelAdmin):
#     pass

@admin.register(Kyc)
class KycAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','address','verified')
    list_editable=  ('verified',)

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    pass

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('owned_by','name','email','address','second_address','logo','phone_number')
    list_editable = ('name','email','address','second_address','logo','phone_number')
    list_display_links = ('owned_by',)
    
@admin.register(SendEmail) 
class SendEmailAdmin(admin.ModelAdmin):
    list_display = ('username','email','subject','content')
    list_editable = ('subject','content')
    list_display_links = ('username',)

# admin.site.register(PendingDeposit)
# admin.site.register(Notification)
# admin.site.register(Deposit)
# admin.site.register(WalletAddress)