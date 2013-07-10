## Jarvis kernel
import functions.function
import application

import tornado.ioloop

class kernel(object):

    # Base functionality
    _data = {}
    _function = {}
    _interface = {}

    # Configuration dictionary
    _config = {}

    # Tornado application instance
    _application = None

    # Tornado application settings
    _appsettings = {
        'xsrf_cookies': False,
        'autoescape':   None
    }

    # Tornado application handler list
    # Attach to a URI endpoint here
    _handlers = []


    def __init__(self, config):
        self.log('Initialised')
        self.log('Load configuration')
        for c in config:
            self.setConfig(c, config[c])


    def start(self):
        self.log('Initialise Tornado')
        self._application = application.app(self)
        self._application.listen(self.getConfig('interface_http_port'))

        self.log('Start IOLoop')
        tornado.ioloop.IOLoop.instance().start()


    def log(self, message):
        print 'MSG: %s' % message


    def register(self, type, items):
        self.log('Registering %ss' % type)
        citems = getattr(self, '_'+type)

        for item in items:
            iname = item.name
            item.setKernel(self)
            citems[iname] = item
            self.log('"%s" %s registered' % (iname, type))


    def get(self, type, key = None):
        citems = getattr(self, '_'+type)

        if key == None:
            return citems
        elif key in citems:
            return citems[key]
        else:
            return None


    def call(self, function, action, data = None):
        # Get function
        func = self.get('function', function)

        if func == None:
            raise JarvisException('Function does not exist', function)

        # Get action
        act = func.get_action(action)

        if act == None:
            raise JarvisException('Action does not exist', action)

        # Run action
        act.function = func
        return act().execute(data)


    def runJobs(self, type):
        # Get all functions
        funcs = self.get('function')

        for f in funcs:
            func = funcs[f]

            # Look for jobs
            job = func.get_job(type)
            if job:
                self.log('Run "%s" job for "%s"' % (type, f))
                job.function = func
                job().execute()


    def setConfig(self, key, value):
        self._config[key] = value


    def getConfig(self, key):
        return self._config[key]


    def getDataPrimary(self):
        '''
        Get primary data interface
        '''
        return self.get('data', 'primary')


class JarvisException(Exception):
    state = functions.function.STATE_FAILURE
    httpcode = functions.function.HTTPCODE_FAILURE

    def __init__(self, message, data = []):
        self.message = message
        self.data = data

class JarvisAuthException(JarvisException):
    state = functions.function.STATE_AUTHERR
    httpcode = functions.function.HTTPCODE_AUTHERR

class JarvisPanicException(JarvisException):
    state = functions.function.STATE_PANIC
    httpcode = functions.function.HTTPCODE_PANIC
