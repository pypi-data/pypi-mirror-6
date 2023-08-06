#-*- coding:utf-8 -*-
import re
import django.dispatch
from django.core.urlresolvers import resolve
from django.conf import settings
from django.utils.importlib import import_module
from django.http  import  HttpResponseRedirect
from django.contrib.sessions.middleware import SessionMiddleware
# Obscure the session id when passing it around in HTML
from cookieless.utils import CryptSession
from cookieless.config import LINKS_RE, DEFAULT_SETTINGS

# Add a signal as a hook for the creation or saving of cookieless sessions
# since these may need different handling to normal cookie based ones
# NB: There is the django.contrib.sessions.models.Session model to hook to, 
#     but creates and saves happen later and for both cookie and cookieless sessions
cookieless_signal = django.dispatch.Signal() 

class CookielessSessionMiddleware(object):
    """ Django snippets julio carlos and Ivscar 
        http://djangosnippets.org/snippets/1540/
        Plus django.session.middleware combined

        Install by replacing 
        'django.contrib.sessions.middleware.SessionMiddleware'
        with 'cookieless.middleware.CookielessSessionMiddleware'

        NB: Remember only decorated methods are cookieless
        cookieless sessions get the no_cookies = True key added
    """

    def __init__(self):
        """ Add regex for auto inserts and an instance of
            the standard django.contrib.sessions middleware
        """
        self.settings = getattr(settings, 'COOKIELESS', DEFAULT_SETTINGS)
        self._re_links = re.compile(LINKS_RE, re.I)
        self._re_forms = re.compile('</form>', re.I)
        self._re_body = re.compile('</body>', re.I)
        self._sesh = CryptSession()
        self.standard_session = SessionMiddleware()
        self.engine = import_module(settings.SESSION_ENGINE)


    def process_request(self, request):
        """ Check if we have the session key from a cookie, 
            if not check post, and get if allowed
            If decryption fails 
            (ie secret is wrong because of other setting restrictions)
            decrypt may not return a real key so
            test for that and start a new session if so
            NB: Use resolve to check view for no_cookies 
                - because its before view is processed
        """
        name = settings.SESSION_COOKIE_NAME
        session_key = ''
        match = resolve(request.path)
        no_cookies = False
        
        if match and getattr(match.func, 'no_cookies', False):
            no_cookies = True
            if request.POST:
                session_key = self._sesh.decrypt(request, 
                                                 request.POST.get(name, None))
            if not session_key and self.settings.get('USE_GET', False):
                session_key = self._sesh.decrypt(request, 
                                                 request.GET.get(name, ''))
        else:
            session_key = request.COOKIES.get(name, '')

        try:
            request.session = self.engine.SessionStore(session_key)
        except:
            pass
        # NB: engine may work but return empty key less session
        try:
            session_key = request.session.session_key
        except:
            session_key = ''

        # If the session_key isn't tied to a session - create a new one
        if not session_key:
            request.session = self.engine.SessionStore() 
            if no_cookies:
                request.session['no_cookies'] = True
                # Flag it here so we can send created session signal 
                # with data later on in process_response
                request.session['created_cookieless'] = True
            request.session.save()


    def process_response(self, request, response):
        """
        Copied from contrib.session.middleware with no_cookies switch added ...
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        NB: request.COOKIES are the sent ones and response.cookies the set ones!
        """
        if getattr(request, 'no_cookies', False):
            if request.COOKIES:
                if self.settings.get('NO_COOKIE_PERSIST', False):
                    # Don't persist a session with cookieless for any session 
                    # thats been set against a cookie 
                    # - may be attached to a user - so always start a new separate one
                    cookie_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, '')
                    if cookie_key == request.session.session_key:
                        request.session = self.engine.SessionStore()
                        request.session['no_cookies'] = True
                        request.session['created_cookieless'] = True
                        request.session.save()
                if self.settings.get('DELETE_COOKIES', False):
                    # Blat any existing cookies
                    for key in request.COOKIES.keys():
                        response.delete_cookie(key)

            # Dont set any new cookies
            if hasattr(response, 'cookies'):
                response.cookies.clear()

            # cookieless - do same as standard process response
            #              but dont set the cookie
            if self.settings.get('REWRITE', False):
                response = self.nocookies_response(request, response)
            # Check for created flag for signal and turn off
            created = request.session.get('created_cookieless', False)
            if created:
                request.session['created_cookieless'] = False
            try:
                # accessed = request.session.accessed
                modified = request.session.modified
            except AttributeError:
                pass
            else:
                if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                    try:
                        # Save the session data 
                        request.session.save()
                    except:
                        # Ensure all keys are strings - required by move to JSON serializer with 1.6
                        for key in request.session.keys():
                            if type(key) not in (type(''), type(u'')):
                                request.session[str(key)] = str(request.session[key])
                                del request.session[key]
                            #elif type(value) not in (type(''), type(u''), type(True)):
                            #    request.session[key] = str(request.session[key])
                        request.session.save()
                    cookieless_signal.send(sender=request, created=created)
            return response
        else:
            return self.standard_session.process_response(request, response)

    def nocookies_response(self, request, response):
        """ Option to rewrite forms and urls to add session automatically """
        name = settings.SESSION_COOKIE_NAME
        session_key = ''
        if request.session.session_key and not request.path.startswith("/admin"):  
            session_key = self._sesh.encrypt(request, request.session.session_key) 

            if self.settings.get('USE_GET', False) and session_key:
                if type(response) is HttpResponseRedirect:
                    host = request.META.get('HTTP_HOST', 'localhost')
                    redirect_url = [x[1] for x in response.items() if x[0] == "Location"][0]
                    if redirect_url.find(host) > -1:
                        redirect_url = self._sesh.prepare_url(redirect_url)
                        return HttpResponseRedirect('%s%s=%s' % (redirect_url, name, 
                                                             session_key)) 
                    else:
                        return HttpResponseRedirect(redirect_url)

            def new_url(match):
                anchor_value = ""
                if match.groupdict().get("anchor"): 
                    anchor_value = match.groupdict().get("anchor")
                return_str = '<a%shref="%s%s=%s%s"%s>' % (
                                 match.groupdict()['pre_href'],
                                 self._sesh.prepare_url(match.groupdict()['in_href']),
                                 name,
                                 session_key,
                                 anchor_value,
                                 match.groupdict()['post_href']
                                 )
                return return_str                                 

            if self.settings.get('USE_GET', False):            
                try:
                    response.content = self._re_links.sub(new_url, response.content)
                except:
                    pass

            # Check in case response has already got a manual session_id inserted
            repl_form = '<input type="hidden" name="%s"' % name
            if hasattr(response, 'content') and response.content.find(repl_form) == -1:
                repl_form = '''%s value="%s" />
                               </form>''' % (repl_form, session_key)
                try:
                    response.content = self._re_forms.sub(repl_form, response.content)
                except:
                    pass
            
            return response
        else:
            return response





