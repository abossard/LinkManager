from django.conf.urls.defaults import *
from accounts.forms import UserCreationFormCustomized, UserChangeFormCustomized, OpenIDForm
from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login, logout, password_change,\
    password_change_done, password_reset, password_reset_complete,\
    password_reset_done, password_reset_confirm
from django.views.generic import create_update, simple
from accounts.views import openid_start, openid_complete, user_change

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('',
                       url(r'^login/$', login, {'template_name': 'login.html', },'login'),
                       url(r'^logout/$', logout, {'template_name': 'logout.html'},'logout'),
                       url(r'^password_change/$', password_change, {'template_name': 'password_change.html'},'password_change'),
                       url(r'^password_change_done/$', password_change_done, {'template_name': 'password_change_done.html'},'password_change_done'),
                       url(r'^password_reset/$', password_reset, {'template_name': 'accounts/password_reset.html', 'email_template_name':'password_reset_email.html'},'password_reset'),
                       url(r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)$', password_reset_confirm, {'template_name': 'password_reset_confirm.html'},'password_reset_confirm'),
                       url(r'^password_reset_complete/$', password_reset_complete, {'template_name': 'password_reset_complete.html'},'password_reset_complete'),
                       url(r'^password_reset_done/$', password_reset_done, {'template_name': 'password_reset_done.html'},'password_reset_done'),
) 

urlpatterns += patterns('',
                        url(r'^signup/$', create_update.create_object, {'form_class':UserCreationFormCustomized, 'template_name': 'signup.html', 'post_save_redirect':reverse_lazy('signup_complete')}, "signup"),
                        url(r'^signup_complete/$', simple.direct_to_template, {'template': 'signup_complete.html',},'signup_complete'),
                        url(r'^user_change_complete/$', simple.direct_to_template, {'template': 'user_change_complete.html',},'user_change_complete'),
                        #url(r'^openid_complete/$', 'simple.direct_to_template', {'template': 'openid_login_complete.html',},'openid_login_complete'),

                     )

urlpatterns += patterns('',
                        url(r'^openid/$', openid_start, {'authentication_form':OpenIDForm, 'template_name': 'openid_login.html','default_redirect':'/'},'openid_login'),
                        url(r'^openid_complete/$', openid_complete,{}, 'openid_complete'),
                        url(r'^user_change/$', user_change, {'form_class':UserChangeFormCustomized, 'template_name': 'user_change.html','post_save_redirect':reverse_lazy('user_change_complete')},'user_change'),
                     )
