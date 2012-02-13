from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class OpenIDForm(forms.Form):
    openid_url = forms.URLField(max_length=80, label='Open ID Url')

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(OpenIDForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
        return self.cleaned_data
    class Media:
        css = {
            'all': ('css/openid.css',),
        }
        js = ('js/openid-jquery.js', )


class UserCreationFormCustomized(UserCreationForm):
    UserCreationForm.Meta.fields = ("username", "email", "first_name", "last_name", )
    
    def __init__(self, *args, **kwargs):
        super(UserCreationFormCustomized, self).__init__(*args, **kwargs)
        self.fields['email'].required=True

class UserCreationFormWithEmail(UserCreationForm):
    UserCreationForm.Meta.fields = ("username", "first_name", "last_name", )
    
    def __init__(self, *args, **kwargs):
        super(UserCreationFormWithEmail, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username']=forms.EmailField(label=_('Email'),help_text=_('This will be your username'))  

    def save(self, commit=True):
        user = super(UserCreationFormWithEmail, self).save(commit=False)
        user.email = self.cleaned_data["username"]
        if commit:
            user.save()
        return user

class UserChangeFormCustomized(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','first_name','last_name')
    
class UserChangeFormWithEmail(UserChangeForm):
    UserChangeForm.Meta.fields = ("username", "first_name", "last_name", )
    
    def __init__(self, *args, **kwargs):
        super(UserChangeFormWithEmail, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username']=forms.EmailField(label=_('Email'),help_text=_('This will be your username'))
        self.fields['username'].widget.attrs['readonly'] = True

        
    def save(self, commit=True):
        user = super(UserChangeFormWithEmail, self).save(commit=False)
        user.email = self.cleaned_data["username"]
        if commit:
            user.save()
        return user
