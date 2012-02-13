from django.contrib.auth.models import User
from openid.consumer.consumer import SUCCESS
from accounts.models import OpenIDUser
from openid.extensions import sreg, ax


class IdentityAlreadyClaimed(Exception):
    pass


class OpenIDBackend:
    """A django.contrib.auth backend that authenticates the user based on
    an OpenID response."""

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist: #@UndefinedVariable
            return None

    def authenticate(self, **kwargs):
        """Authenticate the user based on an OpenID response."""
        # Require that the OpenID response be passed in as a keyword
        # argument, to make sure we don't match the username/password
        # calling conventions of authenticate.

        openid_response = kwargs.get('openid_response')
        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        user = None
        try:
            user_openid = OpenIDUser.objects.get(claimed_id__exact=openid_response.identity_url)
        except OpenIDUser.DoesNotExist: #@UndefinedVariable
            user = self.create_user_from_openid(openid_response)
        else:
            user = user_openid.user

        if user is None:
            return None

        details = self._extract_user_details(openid_response)
        self.update_user_details(user, details)
        return user

    def _extract_user_details(self, openid_response):
        email = fullname = first_name = last_name = nickname = None
        sreg_response = sreg.SRegResponse.fromSuccessResponse(openid_response)
        if sreg_response:
            email = sreg_response.get('email')
            fullname = sreg_response.get('fullname')
            nickname = sreg_response.get('nickname')

        # If any attributes are provided via Attribute Exchange, use
        # them in preference.
        fetch_response = ax.FetchResponse.fromSuccessResponse(openid_response)
        if fetch_response:
            # The myOpenID provider advertises AX support, but uses
            # attribute names from an obsolete draft of the
            # specification.  We check for them first so the common
            # names take precedence.
            email = fetch_response.getSingle('http://schema.openid.net/contact/email', email)
            fullname = fetch_response.getSingle('http://schema.openid.net/namePerson', fullname)
            nickname = fetch_response.getSingle('http://schema.openid.net/namePerson/friendly', nickname)
            email = fetch_response.getSingle('http://axschema.org/contact/email', email)
            fullname = fetch_response.getSingle('http://axschema.org/namePerson', fullname)
            first_name = fetch_response.getSingle('http://axschema.org/namePerson/first', first_name)
            last_name = fetch_response.getSingle('http://axschema.org/namePerson/last', last_name)
            nickname = fetch_response.getSingle('http://axschema.org/namePerson/friendly', nickname)

        if fullname and not (first_name or last_name):
            # Django wants to store first and last names separately,
            # so we do our best to split the full name.
            if ' ' in fullname:
                first_name, last_name = fullname.rsplit(None, 1)
            else:
                first_name = u''
                last_name = fullname

        return dict(email=email, nickname=nickname,
                    first_name=first_name, last_name=last_name)

    def create_user_from_openid(self, openid_response):
        details = self._extract_user_details(openid_response)
        nickname = details['nickname'] or details['email'] or 'openiduser'
        email = details['email'] or ''

        # Pick a username for the user based on their nickname,
        # checking for conflicts.
        i = 1
        while True:
            username = nickname
            if i > 1:
                username += str(i)
            try:
                User.objects.get(username__exact=username)
            except User.DoesNotExist: #@UndefinedVariable
                break
            i += 1

        user = User.objects.create_user(username, email, password=None)
        self.update_user_details(user, details)

        self.associate_openid(user, openid_response)
        return user

    def associate_openid(self, user, openid_response):
        """Associate an OpenID with a user account."""
        # Check to see if this OpenID has already been claimed.
        try:
            user_openid = OpenIDUser.objects.get(claimed_id__exact=openid_response.identity_url)
        except OpenIDUser.DoesNotExist: #@UndefinedVariable
            user_openid = OpenIDUser(user=user,claimed_id=openid_response.identity_url,display_id=openid_response.endpoint.getDisplayIdentifier())
            user_openid.save()
        else:
            if user_openid.user != user:
                raise IdentityAlreadyClaimed(
                    "The identity %s has already been claimed"
                    % openid_response.identity_url)
        return user_openid

    def update_user_details(self, user, details):
        updated = False
        if details['first_name']:
            user.first_name = details['first_name']
            updated = True
        if details['last_name']:
            user.last_name = details['last_name']
            updated = True
        if details['email']:
            user.email = details['email']
            updated = True
        if updated:
            user.save()

