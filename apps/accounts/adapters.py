from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url


class NoNewLocalUsersAccountAdapter(DefaultAccountAdapter):
    """
    Disables the local username/password signup + login flow entirely.
    The only way into the platform is 'Continue with Google'.
    """

    def is_open_for_signup(self, request):
        return False

    def get_login_redirect_url(self, request):
        return resolve_url("accounts:dashboard")


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Google sign-in automatically creates the account on first login —
    no separate signup step, no password, no username.
    """

    def is_open_for_signup(self, request, sociallogin):
        return True

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.first_name and data.get("first_name"):
            user.first_name = data.get("first_name")
        if not user.last_name and data.get("last_name"):
            user.last_name = data.get("last_name")
        return user
