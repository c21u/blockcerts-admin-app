"""admin_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from issuer.views import AddPersonView, UpdatePersonView, CredentialView, IssuanceView, UnsignedCertificatesView, ThankYouView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<issuance_id>\d+)/add_person/', csrf_exempt(AddPersonView.as_view())),
    url(r'^update_person/', csrf_exempt(UpdatePersonView.as_view())),
    url(r'^add_credential/', csrf_exempt(CredentialView.as_view())),
    url(r'^add_issuance/', csrf_exempt(IssuanceView.as_view())),
    url(r'^unsigned_certificates/', csrf_exempt(UnsignedCertificatesView.as_view())),
    url(r'^thankyou/', ThankYouView.as_view())
]
