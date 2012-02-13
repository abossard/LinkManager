from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
from links.models import Credential, Proxy, Site
import requests
import pprint
from BeautifulSoup import BeautifulSoup
from multiprocessing import Pool
from optparse import make_option
from django.forms.models import model_to_dict

def proxy_test(proxy):
    tag = "%s " %(proxy.id,)
    print(tag+'Checking Proxy "%s"... \n' % (proxy.hostname))
    try:
        start_time = datetime.now()
        r = requests.get("http://www.google.com/ncr", 
                         verify=False, 
                         proxies={'http':proxy.hostname,},
                         timeout=5.0)
        print(r.status_code)
        proxy.works = True if r.status_code == 200 else False
        lag = datetime.now() - start_time
        proxy.lag = lag.microseconds / 1000
    except requests.exceptions.Timeout:
        print(tag+'Checking Proxy "%s". TIMEOUT!!!! \n' % (proxy.hostname,))
        proxy.works = False
    except requests.exceptions.ConnectionError:
        print(tag+'Checking Proxy "%s". CONNECTION LIMIT!!!! \n' % (proxy.hostname,))
        proxy.works = False
    print(tag+'Preparing save')
    proxy.save()
    print(tag+'Checking Proxy "%s" done. Result: %s (%s ms)\n' % (proxy.hostname, proxy.works, proxy.lag))

def credential_test(credential_pair):
    credential, proxy = credential_pair
    tag = "%s.%s " %(credential.site_id, credential.id,)
    print(tag +"Checking credential %s .... on proxy %s"% (credential, proxy,))
    try:
        start_time = datetime.now()
        r = requests.get(credential.url, 
                         verify=False, 
                         auth=(credential.username, credential.password),
                         proxies={'http':proxy.hostname},
                         timeout=5.0)
        credential.last_http_code = r.status_code
        lag = datetime.now() - start_time
        credential.last_lag = lag.microseconds / 1000
        soup = BeautifulSoup(r.text)
        title = soup.title or soup.h1
        credential.last_title = str(title.string) if title else "NOT FOUND"
        if not credential.last_title:
            credential.last_title = "empty"
        credential.works = True if (credential.last_http_code == 200) else False
    except requests.exceptions.Timeout:
        print(tag +'Checking Credential "%s". TIMEOUT!!!! \n' % (credential,))
        credential.last_title = "TIMEOUT"
        credential.last_http_code = 0
        credential.works = False
    except requests.exceptions.ConnectionError:
        print(tag +'Checking Credential "%s". CONNECNTION LIMIT!!!! \n' % (credential,))
        credential.last_title = "CONNECTION LIMIT"
        credential.last_http_code = 0
        credential.works = False
    except requests.packages.oreos.monkeys.CookieError:
        print(tag +'Checking Credential "%s". COOOKIE ERRIOR!!!! \n' % (credential,))
        credential.last_title = "COOKE ERROR"
        credential.last_http_code = 0
        credential.works = False
    except TypeError:
        print(tag +'Checking Credential "%s". type error!!!! \n' % (credential,))
        credential.last_title = "type error"
        credential.last_http_code = 0
    except UnicodeError:
        print(tag +'Checking Credential "%s". UNICODERROR!!!! \n' % (credential,))
        credential.last_title = "unicode error"
        credential.last_http_code = 0
    credential.save()
    print(tag+"Done credential %s done. http status: %s, title: %s. (%s ms)"% (credential, credential.last_http_code, credential.last_title, credential.last_lag))


class Command(BaseCommand):
    args = '<time since last check in days>'
    help = 'Check all credentials which last checks are already a bit in the past, mate!'

    def handle(self, *args, **options):
        force_update = True if "force" in args else False
        pool = Pool(5)
        if force_update:
            older_than = datetime.now()
        else:
            older_than = datetime.now() - timedelta(hours=1)
        pool.map(proxy_test, Proxy.objects.filter(update_on__lte=older_than))
        
        proxies = Proxy.objects.filter(works=True)
        credential_per_site_limit = len(proxies)
        if force_update:
            older_than = datetime.now()
        else:
            older_than = datetime.now() - timedelta(minutes=30)
        credential_pairs = list()
        for site in Site.objects.filter(ignore=False):
            credential_index = 0
            self.stdout.write('%s Checking "%s"\n' % (site.id, site,))
            for credential in site.credential_set.filter(Q(update_on__lte=older_than) | Q(last_http_code__lt=200)).order_by('last_http_code','-update_on', '-inserted_on')[:credential_per_site_limit]:
                credential_pairs.append((credential, proxies[credential_index]))
                credential_index += 1
        pool.map(credential_test, credential_pairs)
        return            

