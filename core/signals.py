from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from core.models import *
from django.core.mail import send_mail, BadHeaderError
import unicodedata
@receiver(post_save,sender=COTchargeCode)
def create_cotchargetoken(sender, created, instance, **kwargs):
	if created:
		try:
			x = send_mail("COT CODE","Your cost of transfer code is: {}".format((str(instance.token_key)).split('-')[1].upper()),"info@nblfinancial.com",["{}".format(instance.cotcharge.transfer.owner_account.account_owner.email),])
			'''
			x = "COT CODE","Your cost of transfer code is: {}".format((str(instance.token_key)).split('-')[1].upper())
			x2 = "info@nblfinancial.com {}".format(instance.cotcharge.transfer.owner_account.account_owner.email)
			'''
			print(x)
		
		except BadHeaderError:
			print('error sending email')
		

@receiver(post_save, sender=DebitTransaction)
def notify_mail(sender, created, instance, **kwargs):
	if created:
		try:
			x = send_mail("Deposit Successful",f"Dear {instance.account.account_owner.last_name}\nThe sum of {unicodedata.lookup('POUND SIGN')}{instance.amount} has been successfully deposited in your account.\nLog in to your NBL Financial account to check your balance.\nHappy Banking!\nNew Buryland Financial","info@nblfinancial.com",[instance.account.account_owner.email])
		except:
			print('an error occurred.')
@receiver(post_save, sender=CreditTransaction)
def notify_mail_credit(sender, created, instance, **kwargs):
	if created:
		try:
			x = send_mail("Withdrawal Successful",f"Dear {instance.account.account_owner.last_name}\nThe sum of {unicodedata.lookup('POUND SIGN')}{instance.amount} has been withdrawn from your account. Log in to your NBL Financial account to check your balance.\nHappy Banking\nNew Buryland Financial","info@nblfinancial.com",[instance.account.account_owner.email])
		except:
			print('an error occurred')