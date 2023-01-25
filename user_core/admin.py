from django.contrib import admin
from user_core.models import Profile,Referral,Notification,Deposit,WalletAddress,Withdraw,Transfer,InvestmentPlan,Site
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('profile','wallet_address','amount','wallet_type','time','verified')
    list_editable=  ('verified',)



@admin.register(WalletAddress)
class WalletAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('profile','wallet_address','amount','wallet_type','time','verified')
    list_editable=  ('verified',)
    

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('profile','wallet_address','amount','wallet_type','time','verified')
    list_editable=  ('verified',)
    


@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    pass

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    pass

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('owned_by','name','email','address','second_address','logo','phone_number')
    list_editable = ('name','email','address','second_address','logo','phone_number')
    list_display_links = ('owned_by',)
# admin.site.register(PendingDeposit)
# admin.site.register(Notification)
# admin.site.register(Deposit)
# admin.site.register(WalletAddress)