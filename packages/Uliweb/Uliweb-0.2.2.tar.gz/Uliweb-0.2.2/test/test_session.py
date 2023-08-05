import time, sys, os
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)
from uliweb import manage, functions

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
    >>> app = manage.make_simple_application(project_dir=path, include_apps=['uliweb.contrib.cache'])
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

def test_redis():
    """
    >>> manage.call('uliweb makeproject -f TestProject')
    >>> os.chdir('TestProject')
    >>> path = os.getcwd()
    >>> app = manage.make_simple_application(project_dir=path, include_apps=['uliweb.contrib.cache'])
    >>> cache = functions.get_cache(storage_type='redis', options={'connection_pool':{'host':'localhost', 'port':6379}})
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
    >>> cache.set('a', 1.0)
    True
    >>> cache.get('a')
    1.0
    >>> cache.delete('name')
    True
    >>> cache.delete('count')
    True
    >>> cache.delete('a')
    True
    >>> teardown()
    """

def test_memcache():
    """
    >>> manage.call('uliweb makeproject -f TestProject')
    >>> os.chdir('TestProject')
    >>> path = os.getcwd()
    >>> app = manage.make_simple_application(project_dir=path, include_apps=['uliweb.contrib.cache'])
    >>> cache = functions.get_cache(storage_type='memcache', options={'connection':['192.168.0.191:11211']})
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
    >>> cache.set('a', 1.0)
    True
    >>> cache.get('a')
    1.0
    >>> cache.delete('name')
    True
    >>> cache.delete('count')
    True
    >>> cache.delete('a')
    True
    >>> teardown()
    """

if __name__ == '__main__':
    import time
    
    manage.call('uliweb makeproject -f TestProject')
    try:
        
        os.chdir('TestProject')
        path = os.getcwd()
        app = manage.make_simple_application(project_dir=path, include_apps=['uliweb.contrib.session'])
        
        from weto.session import Session
        from time import sleep
        
        session1 = Session('test')
        session1['name'] = 'limodou'
        session1.set('timeout', 'abc', 5)
        session1.save()
        
        session2 = Session('test')
        print 'session2', session2.items()
        
        sleep(6)
        session3 = Session('test')
        print 'session3', session2.get('timeout')
        session3.save(force=True)
        
        sleep(6)
        session4 = Session('test')
        print 'session4', session4._accessed_time, time.time(), session4.items()
    finally:
        teardown()