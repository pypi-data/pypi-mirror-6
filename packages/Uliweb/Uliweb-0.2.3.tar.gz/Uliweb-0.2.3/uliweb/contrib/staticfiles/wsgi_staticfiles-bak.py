import os
from werkzeug.wsgi import SharedDataMiddleware
from uliweb import settings
from uliweb.utils.filedown import filedown

class StaticFilesMiddleware(SharedDataMiddleware):
    """
    This WSGI middleware is changed from werkzeug ShareDataMiddleware, but
    I made it Uliweb compatable.
    """

    def __init__(self, app, STATIC_URL, disallow=None, cache=True,
                 cache_timeout=60 * 60 * 12):
        self.app = app
        self.url_suffix = STATIC_URL.rstrip('/') + '/'
        
        self.app = app
        self.exports = {}
        self.cache = cache
        self.cache_timeout = cache_timeout
        self.exports[self.url_suffix] = self.loader(settings.STATICFILES.STATIC_FOLDER)
        if disallow is not None:
            from fnmatch import fnmatch
            self.is_allowed = lambda x: not fnmatch(x, disallow)

    def is_allowed(self, filename):
        """Subclasses can override this method to disallow the access to
        certain files.  However by providing `disallow` in the constructor
        this method is overwritten.
        """
        return True

    def loader(self, dir):
        
        def _loader(filename):
            from werkzeug.exceptions import Forbidden, NotFound
            from uliweb.utils.common import pkg
            
            app = self.app
            f = None
            if dir:
                fname = os.path.normpath(os.path.join(dir, filename)).replace('\\', '/')
                if not fname.startswith(dir):
                    return Forbidden("You can only visit the files under static directory."), None
                if os.path.exists(fname):
                    f = fname
            else:
                for p in reversed(app.apps):
                    fname = os.path.normpath(os.path.join('static', filename)).replace('\\', '/')
                    if not fname.startswith('static/'):
                        return Forbidden("You can only visit the files under static directory."), None
                    
                    ff = pkg.resource_filename(p, fname)
                    if os.path.exists(ff):
                        f = ff
                        break
            
            if f:
                return f, self._opener(f)
            
            return NotFound("Can't found the file %s" % filename), None
        return _loader
    
    def __call__(self, environ, start_response):
        from werkzeug.exceptions import Forbidden
        from werkzeug.http import parse_range_header
        
        # sanitize the path for non unix systems
        cleaned_path = environ.get('PATH_INFO', '').strip('/')
        for sep in os.sep, os.altsep:
            if sep and sep != '/':
                cleaned_path = cleaned_path.replace(sep, '/')
        path = '/'.join([''] + [x for x in cleaned_path.split('/')
                                if x and x != '..'])
        file_loader = None
        flag = False
        for search_path, loader in self.exports.iteritems():
            if search_path == path:
                flag = True
                real_filename, file_loader = loader(None)
                if file_loader is not None:
                    break
            if not search_path.endswith('/'):
                search_path += '/'
            if path.startswith(search_path):
                flag = True
                real_filename, file_loader = loader(path[len(search_path):])
                if file_loader is not None:
                    break
        if file_loader is None:
            if flag:
                return real_filename(environ, start_response)
            else:
                return self.app(environ, start_response)
        
        if not self.is_allowed(real_filename):
            return Forbidden("You can not visit the file %s." % real_filename)(environ, start_response)
    
        range = parse_range_header(environ.get('HTTP_RANGE'))
        range_size = settings.GLOBAL.DEFAULT_RANGE_SIZE
        res = filedown(environ, real_filename, self.cache, self.cache_timeout, 
            range=range, range_size=range_size)
        return res(environ, start_response)
        
