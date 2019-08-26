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
from django.urls import path
import django_cas_ng.views

from issuer.views import (HomePageView,
                          AddPersonView,
                          UpdatePersonView,
                          CredentialView,
                          IssuanceView,
                          UnsignedCertificatesView,
                          ThankYouView,
                          UpdateCredentialView,
                          ApproveRecipientsView,
                          CompletedRecipientsView,
                          InviteRecipientsView,
                          RemindRecipientsView,
                          ManageRecipientsView)

urlpatterns = [
    path('accounts/login', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
    path('accounts/logout', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
    url(r'^accounts/callback$', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomePageView.as_view()),
    url(r'^(?P<issuance_id>\w+)/add_person/', csrf_exempt(AddPersonView.as_view())),
    url(r'^credential/(?P<id>\d+)', csrf_exempt(UpdateCredentialView.as_view())),
    url(r'^update_person/', csrf_exempt(UpdatePersonView.as_view())),
    url(r'^add_credential/', csrf_exempt(CredentialView.as_view())),
    url(r'^add_issuance/', csrf_exempt(IssuanceView.as_view())),
    url(r'^unsigned_certificates/', csrf_exempt(UnsignedCertificatesView.as_view())),
    url(r'^thankyou/', ThankYouView.as_view()),
    url(r'^manage_recipients/(?P<pk>\w+)/approve', ApproveRecipientsView.as_view(), name='recipients/approve'),
    url(r'^manage_recipients/(?P<pk>\w+)/completed', CompletedRecipientsView.as_view(), name='recipients/completed'),
    url(r'^manage_recipients/(?P<pk>\w+)/invite', InviteRecipientsView.as_view(), name='recipients/invite'),
    url(r'^manage_recipients/(?P<pk>\w+)/remind', RemindRecipientsView.as_view(), name='recipients/remind'),
    url(r'^manage_recipients/', ManageRecipientsView.as_view(), name='recipients/manage'),
]
