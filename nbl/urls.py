"""nbl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from core.views import homepage
from django.conf.urls.static import static
from django.conf import settings
from generic.views import homepage2, about, services, Contact

admin.site.site_header = 'NBL Administrative Portal'
admin.site.site_title = 'NBL'
admin.site.index_title = 'Admin Portal'

urlpatterns = [
    path('',homepage,name='homepage'),
    path('jeffs-door/', admin.site.urls),
    path('online-banking/',include('core.urls',namespace='core')),
    path('users/',include('users.urls',namespace='users')),
    path('alternate/', homepage2, name='alternate'),
    path('about/',about, name="about"),
    path('services/',services,name='services'),
    path('contact-us/',Contact.as_view(), name='contact'),
]
"""
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
"""
handler403 = 'core.views.homepage_exception'
handler404 = 'core.views.homepage_exception'
handler500 = 'core.views.handler500view'
"""