from django.http import HttpResponseRedirect, HttpResponse
from accounts.utils import DjangoOpenIDStore #@UnresolvedImport
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.views.generic.create_update import update_object
from accounts.forms import UserChangeFormWithEmail, OpenIDForm
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.contrib.sites.models import Site, RequestSite
from openid.yadis.discover import DiscoveryFailure
from django.template.loader import render_to_string

from openid.consumer.consumer import Consumer, SUCCESS, FAILURE, CANCEL
from openid.extensions import ax, sreg
import urllib


def render_failure(request, message, status=403,
                           template_name='openid_failure.html'):
    data = render_to_string(template_name, dict(message=message),context_instance=RequestContext(request))
    return HttpResponse(data, status=status)

def make_consumer(request):
    session = request.session.setdefault('OPENID', {})
    store = DjangoOpenIDStore()
    return Consumer(session, store)

def openid_start(request, template_name='openid_login.html', redirect_field_name=REDIRECT_FIELD_NAME, default_redirect='/',
          authentication_form=OpenIDForm):
    
    redirect_to = request.REQUEST.get(redirect_field_name) or default_redirect
    
    if request.method == 'POST':
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            openid_url = form.cleaned_data['openid_url']
            consumer = make_consumer(request)
            try:
                openid_request = consumer.begin(openid_url)
            except DiscoveryFailure, exc:
                return render_failure(request, "OpenID discovery error: %s" % (str(exc),), status=500)
            if openid_request.endpoint.supportsType(ax.AXMessage.ns_uri):
                fetch_request = ax.FetchRequest()
                # We mark all the attributes as required, since Google ignores
                # optional attributes.  We request both the full name and
                # first/last components since some providers offer one but not
                # the other.
                for (attr, alias) in [
                    ('http://axschema.org/contact/email', 'email'),
                    ('http://axschema.org/namePerson', 'fullname'),
                    ('http://axschema.org/namePerson/first', 'firstname'),
                    ('http://axschema.org/namePerson/last', 'lastname'),
                    ('http://axschema.org/namePerson/friendly', 'nickname'),
                    # The myOpenID provider advertises AX support, but uses
                    # attribute names from an obsolete draft of the
                    # specification.  We request them for compatibility.
                    ('http://schema.openid.net/contact/email', 'old_email'),
                    ('http://schema.openid.net/namePerson', 'old_fullname'),
                    ('http://schema.openid.net/namePerson/friendly', 'old_nickname')]:
                    fetch_request.add(ax.AttrInfo(attr, alias=alias, required=True))
                openid_request.addExtension(fetch_request)
            else:
                openid_request.addExtension(
                    sreg.SRegRequest(optional=['email', 'fullname', 'nickname']))
            return_to = request.build_absolute_uri(reverse(openid_complete))
            return_to += "?"+urllib.urlencode({redirect_field_name: redirect_to})
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return render_openid_request(request, openid_request, return_to)

    else:
        form = authentication_form(request)
    
    request.session.set_test_cookie()
    
    if Site._meta.installed: #@UndefinedVariable
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    
    return render_to_response(template_name,
                              {'form':form,
                               redirect_field_name:redirect_to,
                               'site': current_site,
                               'site_name': current_site.name,
                               },
                              context_instance=RequestContext(request))

def render_openid_request(request, openid_request, return_to, trust_root=None):
    """Render an OpenID authentication request."""
    trust_root = request.build_absolute_uri('/')

    if openid_request.shouldSendRedirect():
        redirect_url = openid_request.redirectURL(trust_root, return_to)
        return HttpResponseRedirect(redirect_url)
    else:
        form_html = openid_request.htmlMarkup(trust_root, return_to, form_tag_attrs={'id': 'openid_message'})
        return HttpResponse(form_html, content_type='text/html;charset=UTF-8')

def openid_complete(request, redirect_field_name=REDIRECT_FIELD_NAME):

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    current_url = request.build_absolute_uri()

    consumer = make_consumer(request)
    openid_response = consumer.complete(dict(request.REQUEST.items()), current_url)

    if not openid_response:
        return render_failure(request, 'This is an OpenID relying party endpoint.')

    if openid_response.status == SUCCESS:
        user = authenticate(openid_response=openid_response)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(redirect_to)
            else:
                return render_failure(request, 'Disabled account')
        else:
            return render_failure(request, 'Unknown user')
    elif openid_response.status == FAILURE:
        return render_failure(
            request, 'OpenID authentication failed: %s' %
            openid_response.message)
    elif openid_response.status == CANCEL:
        return render_failure(request, 'Authentication cancelled')
    else:
        assert False, (
            "Unknown OpenID response type: %r" % openid_response.status)

## Create your views here.
#def signup(request, success_url=None,
#             form_class=UserCreationForm,
#             template_name='signup.html',
#             extra_context=None):
#    if request.method == 'POST':
#        form = form_class(data=request.POST, files=request.FILES)
#        if form.is_valid():
#            form.save()
#            # success_url needs to be dynamically generated here; setting a
#            # a default value using reverse() will cause circular-import
#            # problems with the default URLConf for this application, which
#            # imports this file.
#            return HttpResponseRedirect(success_url or reverse(signup_complete))
#    else:
#        form = form_class()
#    
#    if extra_context is None:
#        extra_context = {}
#    context = RequestContext(request)
#    for key, value in extra_context.items():
#        context[key] = callable(value) and value() or value
#    return render_to_response(template_name,
#                              { 'form': form },
#                              context_instance=context)

def user_change(request, form_class=UserChangeFormWithEmail, template_name='user_change.html', post_save_redirect=None):
    return update_object(request,
                         form_class=form_class,
                         object_id=request.user.id,
                         template_name=template_name,
                         post_save_redirect=post_save_redirect,
                         login_required=True
                         )

#
#def signup_complete(request, template_name='accounts/signup_complete.html'):
#    context = RequestContext(request)
#    return render_to_response(template_name, context)
