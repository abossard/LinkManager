# Create your views here.
from models import Site, Proxy, Credential
from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.core.context_processors import csrf
from django.db.models import Q
from pprint import pprint
import re
URL1 = re.compile('^.*h..p(s?)://([^:]+):([^@]+)@([^/ ]+)(\S*).*$')
URL2 = re.compile('^.*?h..p(s?)://([^/ ]+)(\S*)[^:]+:\s*(\S+)[^:]+:\s*(\S+).*$')
def cleanup(request):
    Credential.objects.filter(keeper=False).delete()
    messages.add_message(request, messages.INFO, 'Cleaned it up, boy!')
    return redirect('/')

def keep(request, credential_id):
    credential = Credential.objects.get(pk=credential_id)
    credential.keeper = not credential.keeper
    credential.save()
    messages.add_message(request, messages.INFO, 'keep credential %s = %s'%(credential,credential.keeper))
    return redirect('/')

def ignore_site(request, site_id):
    site = Site.objects.get(pk=site_id)
    site.ignore = True
    site.save()
    messages.add_message(request, messages.INFO, 'Ignoring site %s now'%(site,))
    return redirect('/')

def home(request):
    if request.method == 'POST': # If the form has been submitted...
        messages.add_message(request, messages.INFO, 'POST %s'%(request.POST,))
        for line in request.POST['content'].split("\n"):
            result = URL1.match(line)
            result2 = URL2.match(line)
            schema = username = password = hostname = path = ""
            if result:
                schema, username, password, hostname, path = result.group(1,2,3,4,5)
            elif result2:
                schema, username, password, hostname, path = result2.group(1,4,5,2,3)
            else:
                messages.add_message(request, messages.INFO, 'NO MATCH %s'%(line,))
            scheme = 'https' if schema else 'http'
            # search or create site
            if path.find('login') > -1:
                messages.add_message(request, messages.INFO, 'DITCHED LOGIN %s'%(path,))
            else:
                if path[-1:] == "/":
                    path = path[0:-1]
                site = Site.objects.get_or_create(hostname=hostname, path=path, scheme=scheme)[0]
                if site.ignore:
                    messages.add_message(request, messages.INFO, 'IGNORE %s'%(site,))
                    continue
                credential = Credential.objects.get_or_create(site_id=site.id,username=username, password=password)
                messages.add_message(request, messages.INFO, 'RESULT %s'%(credential,))
        
    saved_sites = Site.objects.filter(credential__keeper=True, ignore=False).distinct()
    unsaved_credentials = Credential.objects.filter(works=True, keeper=False, site__ignore=False).distinct()
    saved_credentials = Credential.objects.filter(keeper=True, site__ignore=False).distinct()
    proxies = Proxy.objects.all()
    return render_to_response('home.html', locals(), context_instance=RequestContext(request))
    
