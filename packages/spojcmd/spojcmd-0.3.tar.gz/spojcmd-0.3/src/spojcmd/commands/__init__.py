# -*- coding: utf-8 -*-
import requests, getpass, cookielib
from BeautifulSoup import BeautifulSoup
from requests.cookies import RequestsCookieJar
from .. import settings
from ..settings import _url


class Command(object):

    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self._session = None

    def save_cookies(self):
        mcj = cookielib.MozillaCookieJar(settings.COOKIE_FILE_NAME)
        [mcj.set_cookie(c) for c in self.getHTTPClient().cookies]
        mcj.save()

    def do(self, args):
        self.doing(args)
        self.save_cookies()

    def doing(self, args):
        '''
        chilren should implement it
        '''
        raise NotImplemented()

    def getHTTPClient(self):
        if self._session:
            return self._session

        rcj = RequestsCookieJar()
        for c in settings.cj:
            rcj.set_cookie(c)

        self._session = requests.Session()
        self._session.cookies = rcj

        return self._session

    def is_authenticated(self):
        try:
		import os
		assert self.requests.cookies['autologin_hash'], 'hash'
		assert self.requests.cookies['autologin_login'], 'login'

		__, soup = self.get_soup(_url('myaccount'))
		assert soup.find('h3'), 'h3'

		if(os.path.isfile(settings.COOKIE_FILE_NAME)):
			f=open(settings.COOKIE_FILE_NAME)
			lines=f.readlines()
			for line in lines:
				if(not "autologin_login" in line):
					continue
				if(not settings.user_name in line):
					os.remove(settings.COOKIE_FILE_NAME)
					return False
		return True
        except:
            return False

    def auth_if(self):
        if not self.is_authenticated():
            self.authenticate()

    def __getattribute__(self, name):
        if name == 'requests':
            return self.getHTTPClient()
        else:
            return super(Command, self).__getattribute__(name)

    def add_arguments(self, parser):
        pass

    def authenticate(self):
        loop = True
        name = settings.user_name or 'user'
        print 'Authenticating %s for %s' % (name, settings.SPOJ_URL)

        self.requests.cookies.clear()

	first_time=1
        while loop:
            name = settings.user_name
            if name is None:
                if settings.user_name:
                    name = settings.user_name
                    print 'Loaded user name from config, [%s]' % name
                else:
                    name = raw_input('user name:')

	    if(settings.password==None or first_time==0):
	            passw = getpass.getpass()
	    else:
		    first_time=0
		    passw=settings.password

            payload = dict(login_user=name, password=passw,
                    autologin=1, submit='Log In')

            r = self.post(settings.LOGIN_URL, data=payload)
            if self.is_authenticated():
                print 'Welcome %s to %s' % (name, settings.SPOJ_URL)
                settings.user_name = name
                self.save_cookies()
                loop = False
            else:
		if(first_time==0):
			print 'Password is wrong/outdated in '+settings.CONFIG_FILE_NAME+'. Please update it.'
		else:
			print 'Consider writing your password in  '+settings.CONFIG_FILE_NAME+' as `password = *****`'
		print 'Try Again.'


    def get(self, url, **kwargs):
        return self.requests.get(url, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.requests.post(url, data, **kwargs)

    def get_soup(self, url, **kwargs):
        r = self.get(url, **kwargs)
        soup = BeautifulSoup(r.text)
        return r, soup
