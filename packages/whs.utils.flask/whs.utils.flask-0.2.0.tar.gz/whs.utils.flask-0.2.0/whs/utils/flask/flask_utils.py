'''
A few decorators, functions and classes for easier Flask usage.
The whole module is intended to be used with one Flask-app per application, but
some of its parts are usable with other  philosophy.
'''
from functools import wraps
import traceback
from flask import request, Flask, jsonify
import sys
from whs.commons.patterns.singleton import Singleton

before_req_foos = {}

def register_before_request_functions(app):
    '''
    Ensure that all before_request(rule) decorated functions will be registered
    as functions to be called before request matching given rule for given app.
    
    It needs to register additional function (dispatch) as before_request.
    '''
    @app.before_request
    def dispatch():
        if str(request.url_rule) in before_req_foos:
            for foo in before_req_foos[str(request.url_rule)]:
                foo()

def before_request(rule):
    '''
    Decorator that will ensure (after calling register_before_request_functions)
    that each request matching given rule will be preceded with parameterless
    call to decorated function.
    '''
    def decorator(f):
        if rule in before_req_foos:
            before_req_foos[rule] += [f]
        else:
            before_req_foos[rule] = [f]
        return f
    return decorator

def has_args(*arg):
    '''
    Decorator for views.
    Checks, whether all arguments (GET arguments, just after ?) provided
    in argument for this function are provided by client.
    If any of specified arguments is not found, request will result in HTTP 400
    with proper message.
    '''
    def decorator(f):
        @wraps(f)
        def out(*args, **kwargs):
            for a in arg:
                if not a in request.values:
                    return "Argument %r not provided!" % a, 400
            return f(*args, **kwargs)
        return out
    return decorator

def set_default_args(**kwarg):
    '''
    Decorator for views.
    Examines request and if some argument from decorator arguments is not
    provided by client, appends it to request argument list.
    '''
    def decorator(f):
        @wraps(f)
        def out(*args):
            for a, v in kwarg.items():
                if not a in request.args:
                    request.args[a] = v
            return f(*args)
        return out
    return decorator

def route(*args, **kwargs):
    '''
    Decorator that will add some metadata* to decorated function, that may be
    used to lazy registering of routes.
    For further explanation see register_routes docstring.

    * in form of function field
    '''
    def decorator(f):
        f._route_args = args
        f._route_kwargs = kwargs
        return f
    return decorator

def register_routes(app):
    '''
    Ensure that every function (also method) decorated with route is registered
    as route for given app.
    Long story short, following code:
    
    app = Flask(<something>)    # or something inheriting from Flask
    @app.route(<rule>, methods=<methods>, somethin=else)
    def foo(x, rule_dependent_args):
        <body>
    
    is equivalent to:
    
    class MyClass(Flask):       #or something inheriting from Flask
        @route(<rule>, methods=<methods>, somethin=else)
        def foo(self, x, rule_dependent_args):
            <body>
    app = MyClass(<something>)
    app.register_routes()
    '''
    for field in dir(app):
        val = getattr(app, field)
        try:
            app.route(*val._route_args, **val._route_kwargs)(val)
        except:
            pass

def safe_method(f):
    '''
    View decorator.
    
    Ensure that if call to f method raises an exception, it returns 
    self.return_exception(raised exception) (see: EnhancedFlask.return_exception).
    '''
    @wraps(f)
    def out(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except BaseException as e:
            return self.return_exception(e)
    return out

class EnhancedFlask(Flask, Singleton):

    def finalize(self):
        '''
        Short decription: use decorators, so that whole app is usable.
        
        Register routes (marked with route decorator) and dispatched 
        before_request functions (marked with before_request decorator).
        '''
        self.register_routes()
        self.register_before_request_functions()
    
    def register_routes(self):
        '''
        Call register_routes on self.
        '''
        register_routes(self)
    
    def register_before_request_functions(self):
        '''
        Call register_before_request_functions on self.
        '''
        register_before_request_functions(self)

    def return_exception(self, e):
        '''
        Depending on instance debug value, return short info about exception
        (if not in debug mode) or some details about exception (if in debug
        mode).
        '''
        traceback.print_tb(e.__traceback__, file=sys.stdout)
        print("Exception: "+repr(e))
        if self.debug:
            return jsonify({"exception": repr(e), "file": e.__traceback__.tb_frame.f_back.f_code.co_filename, "lineno": e.__traceback__.tb_frame.f_back.f_lineno
        }), 500 #internal server error
        return "Exception occured!", 500
