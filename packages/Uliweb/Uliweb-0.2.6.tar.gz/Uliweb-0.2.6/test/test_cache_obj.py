import time, sys, os
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)
from uliweb import manage, functions

def setup():
    import shutil
    if os.path.exists('TestProject'):
        shutil.rmtree('TestProject', ignore_errors=True)
    
def teardown():
    import shutil
    os.chdir('..')
    if os.path.exists('TestProject'):
        shutil.rmtree('TestProject', ignore_errors=True)

def test_file():
    """
    >>> manage.call('uliweb makeproject -f TestProject')
    >>> os.chdir('TestProject')
    >>> path = os.getcwd()
    >>> app = manage.make_simple_application(project_dir=path, include_apps=['uliweb.contrib.redis_cli', 'uliweb.contrib.orm', 'uliweb.contrib.objcache'])
    >>> cache = functions.get_cache()
    >>> cache.get('name', None)
    >>> def set_name():
    ...     return 'test'
    >>> cache.get('name', creator=set_name)
    'test'
    >>> cache.get('name')
    'test'
    >>> cache.get('hello', 'default')
    'default'
    >>> cache['test'] = 'ooo'
    >>> cache['test']
    'ooo'
    >>> del cache['test']
    >>> cache.setdefault('a', set_name)
    'test'
    >>> cache['a']
    'test'
    >>> cache.inc('count')
    1
    >>> cache.dec('count')
    0
    >>> cache.inc('count')
    1
    >>> cache.get('count')
    1
    >>> cache.set('count', 2)
    True
    >>> cache.inc('count', 2)
    4
    >>> teardown()
    """

if __name__ == '__main__':
    setup()
    manage.call('uliweb makeproject -f TestProject')
    os.chdir('TestProject')
    path = os.getcwd()
    manage.call('uliweb makeapp Test')
    f = open('apps/Test/models.py', 'w')
    f.write('''
from uliweb.orm import *

class User(Model):
    username = Field(str)
    birth = Field(datetime.date)
    email =Field(str)
    
class Group(Model):
    name = Field(str)
    members = ManyToMany('user')
    manager = Reference('user')
''')
    f.close()
    f = open('apps/settings.ini', 'w')
    f.write('''
[GLOBAL]
INSTALLED_APPS = [
'uliweb.contrib.redis_cli', 
'uliweb.contrib.orm', 
'uliweb.contrib.objcache', 
'Test'
]

[LOG]
level = 'debug'

[MODELS]
user = 'Test.models.User'
group = 'Test.models.Group'

[OBJCACHE_TABLES]
user = 'username', 'email'
group = 'name'
''')
    f.close()
    manage.call('uliweb syncdb')
    app = manage.make_simple_application(project_dir=path)
    User = functions.get_model('user')
    Group = functions.get_model('group')
    a = User(username='limodou', email='limodou@abc.om')
    a.save()
    b = User(username='test', email='test@abc.com')
    b.save()
    g = Group(name='python', manager=a, members=[a, b])
    g.save()
    ca = User.get_cached(a.id)
    print "user=", ca.username, ca.email
    redis = functions.get_redis()
    print "redis user=", redis.hgetall('objcache:user:%d' % a.id)
    gc = Group.get_cached(g.id)
    print "group=", gc.name
    print "group.manager=", repr(gc.manager)
    gd = Group.get_cached(g.id)
    print "group.cached_manager=", repr(gd.get_cached_reference('manager'))
    teardown()