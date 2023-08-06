from django.conf.urls import *

# your_app = name of your root djang app.
urlpatterns = patterns('google_oauth.views',
    # First leg of the authentication journey...
    url(r'^login/?$', "begin_auth", name="google_login"),

    # Logout, if need be
    url(r'^logout/?$', "logout", name="google_logout"),  # Calling logout and what not

    # This is where they're redirected to after authorizing - we'll
    # further (silently) redirect them again here after storing tokens and such.
    url(r'^thanks/?$', "thanks", name="google_callback"),
)
