from django.db import models
from django.contrib.auth import settings
import uuid
# simply create admin interface for entering different transactions;
# then login as a user and get to see an individuals transactions
# jus individual @ view level
class UserProfile(models.Model):
	"""we capture the user who has a bank account """
	username = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone_number = models.CharField(max_length=15)
	email = models.EmailField()

	def __str__(self):
		return "{} {}".format(self.last_name,self.first_name)
	class Meta:
		verbose_name_plural = 'Users Profile'


class Bank(models.Model):
	""" This model represents a Bank """
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name
	# only admin creates different banks

class UserAccount(models.Model):
	""" This models a user's bank account in a bank"""
	ACCOUNT_TYPE = (
		(1,'SAVINGS ACCOUNT'),
		(2,'COOPORATE ACCOUNT'),
		(3,'JOINT ACCOUNT')
	)
	ACCOUNT_STATUS = (
		(0, "FROOZEN"),
		(1, "ACTIVE")
	)

	account_owner = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
	bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
	account_number = models.CharField(max_length=20)
	date_created = models.DateTimeField(auto_now_add=True)
	account_type = models.PositiveSmallIntegerField(choices=ACCOUNT_TYPE, default=2)
	account_status = models.PositiveSmallIntegerField(choices=ACCOUNT_STATUS, default=1)

	def __str__(self):
		return "{}: {}, {}".format(self.account_owner, self.bank, self.account_number)
	class Meta:
		verbose_name_plural = 'Users Bank Account'
		unique_together = (('account_owner','bank','account_number'),)

class Transaction(models.Model):
	'''
	ORIGINATING_SOURCE = (
		(1,'E-Channels'),
		(2,'OTHERS')
	)
	'''
	account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=12,decimal_places=2)
	#originating_source = models.PositiveSmallIntegerField(choices=ORIGINATING_SOURCE)
	alternative_source = models.CharField(max_length=50,blank=True)#only if originating_source is 2
	description = models.TextField()
	date_of_transaction = models.DateField()
	time_created = models.DateTimeField(auto_now_add=True)


	class Meta:
		abstract=True
class DebitTransaction(Transaction):
	'''This model captures transactions (payments) into the bank account of a user'''
	# the history of different deposits has to be captured
	# the transaction is either transfer, cash deposit, or withdrawal
	# capture amount, time, etc
	TRANSACTION_CODE = "1"
	TRANSACTION_TYPE = (
		(1,'E-Channels'), 
		(2,'Cash Deposit'),
		(3,'Cheque Deposit')
	)
	# E-channels covers all electronic means of transactions tht we may or may not for the now know
	# normally u credit the giver and debit the receiver; but banks flip it
	transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPE)
	depositor = models.CharField(max_length=75)


	def __str__(self):
		return "debit transaction: {}-{}".format(self.account,self.amount)
	class Meta:
		verbose_name_plural = 'Debit Transactions'
		ordering = ['-date_of_transaction']


class CreditTransaction(Transaction):
	'''This captures transactions out of the bank account of a user'''
	TRANSACTION_CODE = "2"
	TRANSACTION_TYPE = (
		(1,'E-Channels'),
		(2,'Cash Withdrawal'),
		(3,'Cheque Withdrawal')
	)
	TRANSFER_STATUS = (
		(0, 'PENDING'),
		(1, 'COMPLETE'),
		(2, 'CANCELLED')
	)
	# can we capture the means? like a cheque or physically
	transaction_type = models.PositiveSmallIntegerField(choices=TRANSACTION_TYPE)
	payee = models.CharField(max_length=50, blank=True)
	transfer_operation = models.BooleanField(default=False)
	transfer_status = models.PositiveSmallIntegerField(choices=TRANSFER_STATUS, default=0)
	fund_transfer_instance = models.PositiveSmallIntegerField(null=True)

	@property
	def transfer_reference(self):
		if self.fund_transfer_instance:
			try:
				return TransferFund.objects.get(pk=self.fund_transfer_instance)
			except:
				# raise Exception
				return None
		else:
			return None
			
	def __str__(self):
		return "credit transaction: {}-{}".format(self.account,self.amount)

	class Meta:
		verbose_name_plural = "Credit Transactions"
		ordering = ['-date_of_transaction']

class TransferFund(models.Model):
	"""This models captures the transfer of funds from the """
	
	TRANSFER_STATUS = (
		(0, 'PENDING'),
		(1, 'COMPLETE'),
		(2, 'CANCELLED')
	)

	owner_account = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
	time_initiated = models.DateTimeField(auto_now_add=True)
	beneficiary = models.CharField(max_length=250)
	beneficiary_address = models.CharField(max_length=250)
	beneficiary_bank = models.CharField(max_length=100)
	# use js to ensure only digits are allowed
	account_number = models.CharField(max_length=20) 
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	bank_address = models.TextField()
	swift_bic_code = models.CharField(max_length=20)
	iban_routing_number = models.CharField(max_length=50, blank=True)
	remarks = models.CharField(max_length=250, blank=True)
	confirmation_code = models.CharField(max_length=250, blank=True)
	slug = models.SlugField(default=uuid.uuid4, unique=True)
	transfer_status = models.PositiveSmallIntegerField(choices=TRANSFER_STATUS, default=0)
	transfer_failure_reason = models.TextField(max_length=250, blank=True)
	last_updated = models.DateTimeField(auto_now=True)
	#date_of_transaction = models.DateField(auto_now_add=True, null=True)

	def get_slug(self):
		return uuid.uuid4

	def __str__(self):
		return "{}: {}".format(self.owner_account.account_owner, self.amount)

	class Meta:
		ordering = ['-time_initiated']
		permissions = (
			('can_change_transfer_status','user can change transfer status'),
		)

	def update_effects(self, old_instance):
		if old_instance.transfer_status != self.transfer_status:
			# update the credit operation here
			try:
				cr_instance = CreditTransaction.objects.get(fund_transfer_instance=self.pk)
				cr_instance.transfer_status = self.transfer_status
				cr_instance.save()
			except:
				print('an error occured')
	def delete_credit_instance(self):
		try:
			cr_instance = CreditTransaction.objects.get(fund_transfer_instance=self.pk)
			cr_instance.delete()
		except:
			print('an error occured')

	def save(self, *args, **kwargs):
		if self.pk:
			old_instance = TransferFund.objects.get(pk=self.pk)
			self.update_effects(old_instance)
		super().save(*args, **kwargs)


class TransferToken(models.Model):
	"""this model generates a token for a transaction; the token is valid for a given time range"""
	
	transfer = models.OneToOneField(TransferFund, on_delete=models.CASCADE)
	token_key = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
	validation_period = models.PositiveSmallIntegerField(default=180)
	time_generated = models.DateTimeField(auto_now_add=True)
	confirmed = models.BooleanField(default=False)
	time_requested = models.DateTimeField(null=True)
	time_confirmed = models.DateTimeField(null=True)
	
	
	def __str__(self):
		return "{}".format(self.token_key)

class COTcharge(models.Model):
	"""COT charge on a transfer transaction"""
	billing_description = "Cost of Transfer (COT)"
	
	transfer = models.OneToOneField(TransferFund, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	description = models.TextField()
	paid = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	user_code_entered = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return "COT charge on {}".format(self.transfer)

	class Meta:
		ordering = ['-date_created']
		verbose_name_plural = "COT charges"
		verbose_name = "COT charge"

	# def save(self, *args, **kwargs):
	# 	if not hasattr(self, 'cotchargecode'):
	# 		COTchargeCode.objects.create(cotcharge=self)
	# 	super().save(*args, **kwargs)

class COTchargeCode(models.Model):
	"""COT charge codes """
	cotcharge = models.OneToOneField(to=COTcharge, on_delete=models.CASCADE)
	token_key = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
	time_created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} code".format(self.cotcharge)

	class Meta:
		verbose_name = "COT Charge Code"
		verbose_name_plural = "COT Charge Codes"

class GenericBilling(models.Model):
	"""Billing on client transfer"""

	billing = models.CharField(max_length=50)
	billing_abbreviation = models.CharField(max_length=10)
	transfer = models.ForeignKey(TransferFund, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	description = models.TextField()
	paid = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	user_code_entered = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return "{}: {}".format(self.transfer.owner_account, self.billing)

	class Meta:
		ordering = ['-date_created']
		verbose_name_plural = "Client Billings"
		verbose_name = "Client Billing"

class GenericBillingToken(models.Model):
	"""Token on client Billing"""
	billing = models.OneToOneField(to=GenericBilling, on_delete=models.CASCADE)
	token_key = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
	time_created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} code".format(self.billing)

	class Meta:
		ordering = ['-time_created']
		verbose_name = "Client Billing Code"
		verbose_name_plural = "Client Billing Codes" 
