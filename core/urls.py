app_name = "core"
from core import views as vtins
from django.urls import path

urlpatterns = [
	path('',vtins.homepage, name='homepage'),
	path('dashboard',vtins.Dashboard.as_view(),name='dashboard'),
	path('transactions/',vtins.Transaction.as_view(),name='transactions'),
	path('fund-transfer/',vtins.initiate_transfer,name='initiate_transfer'),
	path('contact-us/',vtins.EmailView.as_view(),name='email'),
	path('transfer-data/',vtins.CreateTransferFund.as_view(),name="create_transfer"),
	path('transfer-token/<slug:ttoken>/',vtins.ProcessFormWithToken.as_view(), name="update_token"),
	path('transfer-failed/<slug:transfer_slug>/',vtins.transfer_failed, name="transfer_failed"),
	path('transfers/',vtins.AllTransfer.as_view(),name='all_transfers'),
	path('update-transfer/<slug:transfer_slug>/', vtins.ChangeTransferStatus.as_view(), name='update_transfer'),
	path('<slug:useraccount_slug>/failed-transfers/',vtins.failed_transfers, name="failed_transfer"),
	path('transfer-charge/<slug:slug>/', vtins.UpdateCotCharge.as_view(), name='transfer_charge'),
	path('transfer-charges/<slug:slug>/',vtins.UpdateGenericBilling.as_view(),name='transfer_chargex'),
]