#coding=utf-8

"Core exceptions raised by the SSDB client"
from ssdb._compat import unicode


class SSDBError(Exception):
        pass

# python 2.5 doesn't implement Exception.__unicode__. Add it here to all
# our exception types
if not hasattr(SSDBError, '__unicode__'):
    def __unicode__(self):
        if isinstance(self.args[0], unicode):
            return self.args[0]
        return unicode(self.args[0])
    SSDBError.__unicode__ = __unicode__

    
class AuthenticationError(SSDBError):
    pass

class ServerError(SSDBError):
    pass

class ConnectionError(SSDBError):
    pass

class BusyLoadingError(ConnectionError):
    pass

class InvalidResponse(ServerError):
    pass

class ResponseError(SSDBError):
    pass

class DataError(SSDBError):
    pass

class PubSubError(SSDBError):
    pass

class WatchError(SSDBError):
    pass

class NoScriptError(ResponseError):
    pass

class ExecAbortError(ResponseError):
    pass

