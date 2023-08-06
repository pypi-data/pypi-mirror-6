import os

SPOJ_URL = 'http://www.spoj.com/'
LOGIN_URL = SPOJ_URL
spoj_dirname = None
user_name = None
password = None
wait_time = 4
pyver = "2.7"
cver = "4.3.2"
cppver = "4.3.2"
compiler_id = 41

#ROOM_URL = lambda : SPOJ_URL + spoj_dirname +'/'

CONFIG_FILE_NAME = os.path.expanduser('~/.spojcmdrc')
COOKIE_FILE_NAME = os.path.expanduser('~/.spojcmd_cookie')

def ROOM_URL():
	if(spoj_dirname):
		return SPOJ_URL + spoj_dirname +'/'
        return SPOJ_URL


#cookie jar
cj = None

def _url(path):
	return ROOM_URL() + path + '/'
#_url = lambda path: ROOM_URL() + path + '/'

def get_user_name():
    global user_name
    if user_name:
        return user_name

    user_name = raw_input('user name : ')
    return user_name
