from django.db import models
from django.contrib.auth import get_user_model
from oauth2client.django_orm import CredentialsField

User = get_user_model()


class GoogleProfile(models.Model):
    """
        An example Profile model that handles storing the oauth_token and
        oauth_secret in relation to a user. Adapt this if you have a current
        setup, there's really nothing special going on here.
    """
    user = models.OneToOneField(User)
    credential = CredentialsField()
