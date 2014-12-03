from config import ConfigBase
class DevelopmentConfig(ConfigBase):

    ## enable/disable debug mode
    DEBUG = True

	## explicitly enable or disable the propagation of exceptions. 
    ## If not set or explicitly set to None this is implicitly true if either TESTING or DEBUG is true.
    #PROPAGATE_EXCEPTIONS = None

    ## By default if the application is in debug mode the request context is not popped on exceptions to
    ## enable debuggers to introspect the data. This can be disabled by this key. You can also use this 
    ## setting to force-enable it for non debug execution which might be useful to debug production 
    ## applications (but also very risky).
    #PRESERVE_CONTEXT_ON_EXCEPTION = False

    ## If this is set to True Flask will not execute the error handlers of HTTP exceptions but instead
    ## treat the exception like any other and bubble it through the exception stack. This is helpful 
    ## for hairy debugging situations where you have to find out where an HTTP exception is coming from.
    #TRAP_HTTP_EXCEPTIONS = False

    ## Werkzeug's internal data structures that deal with request specific data will raise special key 
    ## errors that are also bad request exceptions. Likewise many operations can implicitly fail with a
    ## BadRequest exception for consistency. Since it's nice for debugging to know why exactly it 
    ## failed this flag can be used to debug those situations. If this config is set to True you will get
    ## a regular traceback instead.
    #TRAP_BAD_REQUEST_ERRORS False

    ## If this is set to True (the default) jsonify responses will be pretty printed if they are not 
    ## requested by an XMLHttpRequest object (controlled by the X-Requested-With header)
    JSONIFY_PRETTYPRINT_REGULAR = True


