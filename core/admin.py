from django.contrib import admin
from core.models import *

class UserProfileAdmin(admin.ModelAdmin):
	fields = ('username','first_name','last_name','phone_number', 'email')
	search_fields = ['first_name','last_name']
admin.site.register(UserProfile,UserProfileAdmin)


class BankAdmin(admin.ModelAdmin):	
	def upper_case_name(self,obj):
		#return ("{}".format(obj.name)).upper() 
		return ("%s" % (obj.name)).upper()
	upper_case_name.short_description = "Name of Bank"
	
	fields = ['name']
	list_display = ['upper_case_name']
	

admin.site.register(Bank,BankAdmin)

class UserAccountAdmin(admin.ModelAdmin):
	fields = ['account_owner','bank','account_number','account_type','account_status']
	list_display = ['bank','account_owner','account_number','account_type','account_status']

	#search_fields = ['bank','account_owner']
admin.site.register(UserAccount, UserAccountAdmin)
class DebitTransactionAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_display = ('date_of_transaction','account','amount','description')
	fields = ['account','amount','transaction_type','alternative_source','description','date_of_transaction','depositor']
	search_fields = ['account__account_owner__last_name', 'account__account_owner__first_name']
admin.site.register(DebitTransaction,DebitTransactionAdmin)

class CreditTransactionAdmin(admin.ModelAdmin):
	def amount_(self,obj):
		return obj.amount
	amount_.short_description = 'Amount (USD)'

	list_per_page = 20
	list_display = ('date_of_transaction','account','amount_','payee','description')
	fields = ['account','amount','payee','transaction_type','alternative_source','description','date_of_transaction']
	search_fields = ['account__account_owner__last_name', 'account__account_owner__first_name']
admin.site.register(CreditTransaction,CreditTransactionAdmin)

class FundTransferModificationAdmin(admin.ModelAdmin):
	
	def owner_account_(self, obj):
		return ("{}".format(obj.owner_account.account_owner))
	

	fields = ['owner_account','transfer_status','transfer_failure_reason']
	list_display = ['owner_account_', 'beneficiary', 'amount']
admin.site.register(TransferFund, FundTransferModificationAdmin)

class COTchargeAdmin(admin.ModelAdmin):

	fields = ['transfer','amount','description','paid']
admin.site.register(COTcharge, COTchargeAdmin)

class COTchargeCodeAdmin(admin.ModelAdmin):

	list_display = ['cotcharge','token_key','time_created']
	fields = ['cotcharge',]
admin.site.register(COTchargeCode, COTchargeCodeAdmin)

class GenericBillingAdmin(admin.ModelAdmin):
	fields = ['billing','billing_abbreviation','transfer','amount','description']
	list_display = ['transfer','amount','billing', 'paid']
admin.site.register(GenericBilling,GenericBillingAdmin)

class GenericBillingTokenAdmin(admin.ModelAdmin):

	list_display = ['billing', 'token_key', 'time_created']
	fields = ['billing']
admin.site.register(GenericBillingToken, GenericBillingTokenAdmin)