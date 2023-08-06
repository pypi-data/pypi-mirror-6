from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest

from oauth2client.client import OAuth2WebServerFlow
from oauth2client import xsrfutil
from oauth2client.django_orm import Storage

from google_oauth.models import GoogleProfile

import httplib2

User = get_user_model()


def logout(request, redirect_url=settings.LOGOUT_REDIRECT_URL):
    django_logout(request)
    return HttpResponseRedirect(request.build_absolute_uri(redirect_url))


def begin_auth(request):

    # Request an authorization url to send the user to...
    callback_url = request.build_absolute_uri(reverse('google_oauth.views.thanks'))
    flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH_CLIENT_ID, client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
                               scope="https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/plus.profile.emails.read", redirect_uri=callback_url)

    flow.params['state'] = xsrfutil.generate_token(settings.GOOGLE_OAUTH_CLIENT_SECRET, request.user)

    auth_url = flow.step1_get_authorize_url()

    # Then send them over there, durh.
    return HttpResponseRedirect(auth_url)


def thanks(request, redirect_url=settings.LOGIN_REDIRECT_URL):
    if not xsrfutil.validate_token(settings.GOOGLE_OAUTH_CLIENT_SECRET, request.REQUEST['state'],
                                   request.user):
        return HttpResponseBadRequest()

    callback_url = request.build_absolute_uri(reverse('google_oauth.views.thanks'))
    flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH_CLIENT_ID, client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
                               scope="https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/plus.profile.emails.read",
                               redirect_uri=callback_url)

    credential = flow.step2_exchange(request.REQUEST)

    from apiclient.discovery import build

    http = httplib2.Http()
    credential.authorize(http)

    plus = build("plus", "v1", http=http)
    guser = plus.people().get(userId="me").execute()

    user = request.user if request.user.pk else None

    if user is None and 'emails' in guser and len(guser['emails']) > 0:
        try:
            user = User.objects.get(email=guser['emails'][0]['value'])
        except User.DoesNotExist:
            user = None
    if user is None:
        username = 'google%d' % guser['id']
        email = guser['emails'][0]['value'] if 'emails' in guser and len(guser['emails']) > 0 else ''
        if 'displayName' in guser:
            username = guser['displayName'].replace(' ', '_')
        user = User.objects.create_user(username, email, request.REQUEST['state'])
        profile = GoogleProfile()
        profile.user = user
        profile.credential = credential
        profile.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return HttpResponseRedirect(redirect_url)
