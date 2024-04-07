from django import forms
from core.models import TransferFund, COTcharge, GenericBilling
from django.core.exceptions import ValidationError

class ContactForm(forms.Form):
	from_email = forms.EmailField(required=True)
	sender_name = forms.CharField(required=True)
	message = forms.CharField(widget=forms.Textarea, required=True)

class TransferFundForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class':'form-control'})
		self.fields['amount'].widget.attrs.update({'min':'1'})
		self.fields['account_number'].widget.attrs.update({'id':"acct_number"})
	def clean_beneficiary_bank(self):
		beneficiary_bank = self.cleaned_data['beneficiary_bank'].title()
		return beneficiary_bank

	class Meta:
		model = TransferFund
		exclude = ['owner_account','time_initiated', 'confirmation_code', 'slug', 'transfer_failure_reason', 'transfer_status']
		labels = {
			"swift_bic_code": "Swift Code (BIC)",
			"iban_routing_number": "IBAN (Routing Number)"
		}
		widgets = {
			'beneficiary_address':forms.Textarea(attrs={'rows':'3'}),
			'bank_address':forms.Textarea(attrs={'rows':'3'})
		}

class ConfirmToken(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class':'form-control'})
		self.fields['amount'].widget.attrs.update({'min':'1'})
		self.fields['account_number'].widget.attrs.update({'id':"acct_number"})
		self.fields['confirmation_code'].widget.attrs.update({'id':'confirmation_code', "required":True}) #"autofocus":True,

	def clean_confirmation_code(self):
		confirmation_code = self.cleaned_data['confirmation_code'].strip()
		if len(confirmation_code) < 1:
			self.add_error('confirmation_code','Enter confirmation code')
		return confirmation_code

	class Meta:
		model = TransferFund
		exclude = ['owner_account','time_initiated', 'slug', 'transfer_failure_reason','transfer_status']

		labels = {
			"swift_bic_code": "Swift Code (BIC)",
			"iban_routing_number": "IBAN (Routing Number)",
			'confirmation_code': "Transfer Token"
		}
		widgets = {
			'beneficiary_address':forms.Textarea(attrs={'rows':'3'}),
			'bank_address':forms.Textarea(attrs={'rows':'3'})
		}

class ChangeTransferStatusForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class':'form-control'})
		self.fields['transfer_failure_reason'].widget.attrs.update({'rows':'3', "required":True})

	class Meta:
		model = TransferFund
		fields = ['transfer_status','transfer_failure_reason']
		labels = {
			'transfer_status': "Current Status"
		}

class COTchargeCodeUpdateForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class':'form-control'})
		self.fields['amount'].widget.attrs.update({'readonly':True})

	class Meta:
		model = COTcharge
		exclude = ['transfer','description','paid','date_created','last_updated']
		labels = {
			'user_code_entered':'Authorization Code'
		}

class GenericBillingUpdateForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class':'form-control'})
		self.fields['amount'].widget.attrs.update({'readonly':True})
		self.fields['billing'].widget.attrs.update({'readonly':True})

	class Meta:
		model = GenericBilling
		exclude = ['transfer','description','paid','date_created','last_updated','billing_abbreviation']
		labels = {
			'user_code_entered':'Authorization Code',
			'billing': 'Purpose'
		}