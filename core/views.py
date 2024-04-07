from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from core.models import *
from django.db.models import Sum
from django.core.mail import send_mail, BadHeaderError
from core.forms import ContactForm, TransferFundForm, ConfirmToken, ChangeTransferStatusForm, COTchargeCodeUpdateForm, GenericBillingUpdateForm
from core.models import TransferFund, TransferToken
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

class Dashboard(View):

	def get(self, request):
		return HttpResponse('we good')
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

def _user_balance(user_account):
	# test to ensure that its a userAccount that is passed in as variable

	user_total_debit = DebitTransaction.objects.filter(account=user_account).aggregate(total=Sum('amount'))
	user_total_debit = user_total_debit['total'] if user_total_debit['total'] else 0
	user_total_credit = CreditTransaction.objects.filter(account=user_account).exclude(transfer_status=2).exclude(Q(transfer_operation=True)&Q(transfer_status=0)).aggregate(total=Sum('amount'))
	#exclude(transfer_status=2).
	# .exclude(Q(transfer_operation=True)&Q(transfer_status=0))
	
	user_total_credit = user_total_credit['total'] if user_total_credit['total'] else 0
	mark_astericks = CreditTransaction.objects.filter(Q(transfer_operation=True)&Q(transfer_status=0))
	return user_total_debit - user_total_credit

def _user_book_balance(user_account):
	user_total_debit = DebitTransaction.objects.filter(account=user_account).aggregate(total=Sum('amount'))
	user_total_debit = user_total_debit['total'] if user_total_debit['total'] else 0
	user_total_credit = CreditTransaction.objects.filter(account=user_account).exclude(transfer_status=2).aggregate(total=Sum('amount'))
	user_total_credit = user_total_credit['total'] if user_total_credit['total'] else 0
	#print('credit',user_total_credit, 'debit',user_total_debit)
	return user_total_debit - user_total_credit



class Transaction(View):
	"""this displays all the transactions that a user has been making"""
	def get(self, request):
		if not hasattr(request.user, "userprofile"):
			#messages.warning(request, "No profile found")
			return redirect('core:homepage')
		loggedin_user = request.user.userprofile
		if not hasattr(loggedin_user, 'useraccount'):
			messages.warning(request,"Bank account details not created yet!")
			return redirect('core:homepage')
		useraccount = loggedin_user.useraccount
		debit_transactions = useraccount.debittransaction_set.all()
		credit_transactions = useraccount.credittransaction_set.exclude(transfer_status=2)
		failed_transfers = useraccount.credittransaction_set.filter(transfer_status=2)

		deb_cre = []
		for i in debit_transactions:
			deb_cre.append(i)
		for i in credit_transactions:
			deb_cre.append(i)
		deb_cre = sorted(deb_cre, key=lambda x:x.time_created, reverse=True)
		#print(deb_cre_sorted)
		user_account_balance = _user_balance(useraccount)
		user_book_balance  = _user_book_balance(useraccount)

		#print(user_account_balance)
		mark_astericks = useraccount.credittransaction_set.filter(transfer_operation=True,transfer_status=0)
		mark_astericks = [str(x.pk) for x in mark_astericks]
		mark_astericks = ",".join(mark_astericks)

		transfer_under_billing = useraccount.transferfund_set.filter(cotcharge__paid=False)
		transfer_under_billing2 = useraccount.transferfund_set.filter(genericbilling__paid=False)
		#print(transfer_under_billing2)
		#transfer_under_billing2 = transfer_under_billing
		transfer_under_billing = [x.cotcharge for x in transfer_under_billing]
		transfer_under_billing2 = [[i for i in x.genericbilling_set.all() if i.paid == False] for x in transfer_under_billing2]
		
		x8 = []
		for i in transfer_under_billing2:
			for z in i:
				x8.append(z)

		transfer_under_billing2 = x8
		#print(x8)
		context = {"debit_transactions":debit_transactions, "credit_transactions":credit_transactions, 'deb_cre':deb_cre, 'useraccount':useraccount,'user_account_balance':user_account_balance, 'mark_astericks':mark_astericks, "user_book_balance":user_book_balance, 'failed_transfers':failed_transfers, 'transfer_under_billing':transfer_under_billing, 'transfer_under_billing2':transfer_under_billing2}

		try:
			x = send_mail("SUCCESSFUL LOGIN NOTIFICATION", f"Dear {loggedin_user.last_name.title()},\nThis is to notify you that you have successfully logged into your account.\nIf this was not you, contact the support desk by email immediately.\n\nRegards\nMary Barnes | Head Customer Service","info@nblfinancial.com",[loggedin_user.email])
		except:
			print("q work")


		return render(request, 'transaction/transact2.html',context)
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

def homepage(request):
	return render(request,'index_generic.html',{})#index_clone.html  'index2.html'

def homepage_exception(request,exception):
	return render(request,'index2.html',{})
def handler500view(request):
	return render(request, 'index2.html',{})

@login_required
def initiate_transfer(request):
	context = {}
	loggedin_user = request.user.userprofile
	useraccount = loggedin_user.useraccount
	if useraccount.account_status == 0:
		return render(request, 'transaction/initiate_frozen_transfer.html', context)
	else:
		return render(request, 'transaction/initiate_transfer.html',context)

class EmailView(View):
	''' this processes the contact us form on the indexpage'''
	template_name = 'index2.html'
	form_class = ContactForm
	def get(self, request):
		''' jus display the index page'''
		return redirect('core:homepage')
	def post(self, request):
		bounded_form = self.form_class(request.POST)
		if bounded_form.is_valid():
			sender_name = bounded_form.cleaned_data['sender_name']
			sender_email = bounded_form.cleaned_data['from_email']
			sender_msg = bounded_form.cleaned_data['message']


			#.format(sender_name) sender_email
			
			# clean the characters using that request method u used
			try:
				x = send_mail("Inquiries By {}".format(sender_name), "sender email: {}\n message body\n{}".format(sender_email,sender_msg),"info@nblfinancial.com",['info@nblfinancial.com'] )
				print(x)
			except BadHeaderError:
				return redirect('core:homepage')
				#return HttpResponse('invalid header')
				#print tell the person to send a regular mail
			except:

				return redirect('core:homepage')# send a regular mail HttpResponse('something went wrong')
		else:
			print('something was wrong; mail did not go tru')
		return redirect('core:homepage')

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

class CreateTransferFund(View):
	model = TransferFund
	template_name = "transaction/transfer_form.html"
	form_class = TransferFundForm

	def get(self, request):
		"""
		the moment u initiate a transfer, an instance of the model is created, and its transfer fund created; code_request time is updated when the request for the token delivery by mail hits
		"""
		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		context = {'form':self.form_class, 'useraccount':loggedin_user, "user_account_balance":user_account_balance, "user_book_balance":user_book_balance}
		return render(request, self.template_name, context)


	def post(self, request):
		# save the form; create an instance of TransferToken; and return the form with the field to update;
		# add a field to check mail and get the token
		# redisplay the page with the check your mail info
		#process bank to title case
		loggedin_user = request.user.userprofile.useraccount
		user_book_balance  = _user_book_balance(loggedin_user)
		user_account_balance = _user_balance(loggedin_user)
		bounded_form = self.form_class(request.POST)

		
		context = {'form':bounded_form, 'useraccount':loggedin_user, "user_account_balance":user_account_balance,"user_book_balance":user_book_balance}
		if bounded_form.is_valid():
			if float(bounded_form.cleaned_data['amount']) >= user_account_balance:
				#user_book_balance
				bounded_form.add_error('amount',"Insufficient balance in account {}".format(user_book_balance))
				return render(request, self.template_name, context)

			obj = bounded_form.save(commit=False)
			obj.owner_account = loggedin_user#request.user.userprofile
			obj.save()
			# create the TransferToken
			ttoken = TransferToken.objects.create(transfer=obj)

			# then send the token by mail

			try:
				x = send_mail("Transfer Token","Your token for the your transfer is: {}".format((str(obj.transfertoken.token_key)).split('-')[1].upper()),"info@nblfinancial.com",["{}".format(obj.owner_account.account_owner.email),])
				print(x)
			except BadHeaderError:
				print('error sending email')


			return redirect('core:update_token', obj.slug)
		else:
			return render(request, self.template_name, context)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

class ProcessFormWithToken(View):

	model = TransferFund
	form_class = ConfirmToken
	template_name = "transaction/transfer_token_form.html"
	# now we have to do 404 redirect page
	def get(self, request, ttoken):#, transfer_token):
		obj = get_object_or_404(self.model,slug=ttoken)
		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		context = {'form':self.form_class(instance=obj), "user_account_balance":user_account_balance,"user_book_balance":user_book_balance}
		messages.success(request, "Token has been forwarded to {}. Please check your email and enter the transfer token in it's field below within 5 minutes".format(obj.owner_account.account_owner.email))
		return render(request, self.template_name, context)
	def post(self, request, ttoken):
		obj = get_object_or_404(self.model,slug=ttoken)
		# check if the submision time has exceeded the time bound and then redirect with message to restart the procedure
		# add a countdown timer to time the person with the start point the time request was sent
		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		bounded_form = self.form_class(request.POST, instance=obj)
		context = {'form':bounded_form, "obj":obj, "user_account_balance":user_account_balance,"user_book_balance":user_book_balance}
		if bounded_form.is_valid():
			# ensure the token field is not empty
			# add a cancel/reset button with a prompt that say u'll have to restart the process again if you want to
			
			token_ = bounded_form.cleaned_data['confirmation_code'].strip()
			errors = {}
			time_bound_exceeded = False
			# test if the amount exceeds the total available in the account
			if token_:
				if token_.upper() == str(obj.transfertoken.token_key).split('-')[1].upper():
					pass
					# send email notifying the person

				else:
					errors['confirmation_code'] = "Invalid Token"
					# remove the autofocus from the token field
					messages.warning(request, "Invalid Token Entered. Please check your email: {}, for the correct token".format(obj.owner_account.account_owner.email))
			current_time = timezone.now()
			difference = current_time - obj.transfertoken.time_generated
			minutes_ = divmod(difference.seconds, 60)
			if minutes_[0] > 5:
				time_bound_exceeded = True
			if time_bound_exceeded:
				# update transfer_failure_reason
				obj.transfer_failure_reason = "Validity period exceeded!"
				obj.save()
				messages.info(request, "The time bound for transaction validity has been exceeded. Please initiate a new transfer as your request has been cancelled!")
				return redirect('core:transfer_failed', obj.slug)

			if errors:
				for key, value in errors.items():
					bounded_form.add_error(key, value)
				return render(request, self.template_name, context)
			else:
				# create a credit transfer that has an asterics*
				obj.save()
				description = "Transfer of {} to {} from self".format(obj.amount, obj.beneficiary)
				description = obj.remarks if len(obj.remarks) > 1 else description
				CreditTransaction.objects.create(transfer_status=0, transfer_operation=True, payee=obj.beneficiary, transaction_type=1,account=obj.owner_account,amount=obj.amount,description=description, date_of_transaction=timezone.now().date(), fund_transfer_instance=obj.pk)
				return render(request, "transaction/transfer_successful.html", context)
			
			return redirect('core:homepage')
		else:
			messages.success(request, "Token has been forwarded to {}. Please check your email and enter the transfer token in it's field below within 5 minutes".format(obj.owner_account.account_owner.email))
			messages.warning(request, "Errors in some entries detected!")
			return render(request, self.template_name,context)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
def transfer_failed(request, transfer_slug):
	
	obj = get_object_or_404(TransferFund, slug=transfer_slug)
	messages.info(request, "Transfer was unsuccesful due to: {}".format(obj.transfer_failure_reason))
	context = {"obj":obj}
	return render(request, "transaction/transaction_failed.html", context)
class AllTransfer(ListView):
	''' once a transfer fails, add an asterics with a message that says some recent transfers failed'''
	model = TransferFund
	template_name = "transaction/all_transfers.html"

	def get_context_data(self, **kwargs):
		context_data = super().get_context_data(**kwargs)
		loggedin_user = self.request.user.userprofile.useraccount
		context_data['user_account_balance'] = _user_balance(loggedin_user)
		context_data['user_book_balance']  = _user_book_balance(loggedin_user)
		return context_data

	@method_decorator(login_required)
	@method_decorator(permission_required('core.can_change_transfer_status', raise_exception=True))
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
class ChangeTransferStatus(View):

	model = TransferFund
	form_class = ChangeTransferStatusForm
	template_name = "transaction/change_transfer_status.html"

	def get(self, request, transfer_slug):
		obj = get_object_or_404(TransferFund, slug=transfer_slug)
		context = {'form':self.form_class(instance=obj), 'obj':obj}
		return render(request, self.template_name, context)

	def post(self, request, transfer_slug):
		# save the status and send for update process
		"""
		write a method in the model that checks for the change in transfer_status and updates the credit transaction accordingly making it permanent or not.
		then write views for users to see thr transfers and see why it failed.
		make sure the book balance and balance are reflected properly.
		"""
		obj = get_object_or_404(TransferFund, slug=transfer_slug)
		bounded_form = self.form_class(request.POST, instance=obj)
		context = {'form':bounded_form, 'obj':obj}
		if bounded_form.is_valid():
			obj.save()
			messages.info(request, "update succesful")
			return redirect('core:all_transfers')
		else:
			return render(request, self.template_name, context)

"""
add a * that says some recent transfers failed, pls check your transfers and follow up with customer service on affected transactions.
"""

def failed_transfers(request, useraccount_slug):
	useraccount = get_object_or_404(UserAccount, pk=useraccount_slug)
	failed_transfers = useraccount.credittransaction_set.filter(transfer_status=2)
	user_account_balance = _user_balance(useraccount)
	user_book_balance  = _user_book_balance(useraccount)
	context = {"object_list":failed_transfers, 'useraccount':useraccount, 'user_account_balance':user_account_balance,'user_book_balance':user_book_balance}
	return render(request, 'transaction/failed_transfers.html', context)

class UpdateCotCharge(View):

	form_class = COTchargeCodeUpdateForm
	model = COTcharge
	model_update = GenericBilling
	template_name = "transaction/cotupdate.html"

	def get(self, request, slug):
		obj_ = get_object_or_404(self.model, pk=slug)
		#context = {}

		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		context = {'form':self.form_class(instance=obj_),'useraccount':loggedin_user, "user_account_balance":user_account_balance, "user_book_balance":user_book_balance}

		return render(request, self.template_name, context)

	def post(self, request, slug):
		obj_ = get_object_or_404(self.model, pk=slug)
		bounded_form = self.form_class(request.POST, instance=obj_)

		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		context = {'form':bounded_form, 'useraccount':loggedin_user, "user_account_balance":user_account_balance, "user_book_balance":user_book_balance}
		if bounded_form.is_valid():
			# compare here
			if str(obj_.cotchargecode.token_key).split('-')[1].upper() != bounded_form.cleaned_data['user_code_entered'].upper():
				messages.warning(request, "Incorrect authorization code entered")
				return render(request, self.template_name, context)
			obj = bounded_form.save(commit=False)
			obj.paid = True
			obj.save()
			return redirect('core:transactions')
		else:
			return render(request, self.template_name, context)

class UpdateGenericBilling(View):

	form_class = GenericBillingUpdateForm
	model = GenericBilling
	template_name = "transaction/cotupdate.html"

	def get(self, request, slug):
		obj_ = get_object_or_404(self.model, pk=slug)
		#context = {}

		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		context = {'form':self.form_class(instance=obj_),'useraccount':loggedin_user, "user_account_balance":user_account_balance, "user_book_balance":user_book_balance}

		return render(request, self.template_name, context)

	def post(self, request, slug):
		obj_ = get_object_or_404(self.model, pk=slug)
		bounded_form = self.form_class(request.POST, instance=obj_)

		loggedin_user = request.user.userprofile.useraccount
		user_account_balance = _user_balance(loggedin_user)
		user_book_balance  = _user_book_balance(loggedin_user)

		context = {'form':bounded_form, 'useraccount':loggedin_user, "user_account_balance":user_account_balance, "user_book_balance":user_book_balance}
		if bounded_form.is_valid():
			# compare here
			if str(obj_.genericbillingtoken.token_key).split('-')[1].upper() != bounded_form.cleaned_data['user_code_entered'].upper():
				messages.warning(request, "Incorrect authorization code entered")
				return render(request, self.template_name, context)
			obj = bounded_form.save(commit=False)
			obj.paid = True
			obj.save()
			return redirect('core:transactions')
		else:
			return render(request, self.template_name, context)
