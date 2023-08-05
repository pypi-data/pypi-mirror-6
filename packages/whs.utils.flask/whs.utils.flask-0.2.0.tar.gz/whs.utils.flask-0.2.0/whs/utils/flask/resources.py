'''
Flask class mixin (see EnhancedFlask in flask_utils in this package) for easy
creation of resource representation with customizable set of operations (from
CRUDL operation model).
As for now, in-/output is possible only in JSON format.

TODO:
- CREATE SANE TESTS!
- introduce different output formats than JSON
- use specialized exceptions
- registration should be automatized (in some kind of loop, basing on roots,
    methods and functions mapping)
- add C* method - create with given id
- add decorator which will wrap call to _note_kwargs and _clear_kwargs
- switch from Flyweight to MetaFlyweight (or create two different implementations)
- figure out how to deal with ugly out-of-class crudl methods
'''

import logging
import uuid
from flask import request, Flask, jsonify, abort
from whs.commons.patterns.flyweight import Flyweight

logging.getLogger(__qualname__).warning('''
THIS IS HIGHLY UNSTABLE VERSION OF PACKAGE THAT WILL ALLOW EASY REST RESOURCE
CREATION. IT DOESNT WORK YET.
FEEL FREE TO REFACTOR, DEVELOP ON YoUR OWN, ETC, AND IF POSSIBLE - LET US KNOW.

PS. Commented lines are here for a reason - they may be useful in future.
''')

def combined_multi_to_dict(cmd):
    '''
    Utility methods converting CombinedMultiDict to standard dict.
    Shouldn't be used by user.
    '''
    out = {}
    for k in cmd.keys():
        out[k] = cmd[k]
    return out

class classproperty:
    '''
    Class for creating read-only class properties
    '''
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)


############################################################################
#                                                                          #
#                        CRUDL methods                                     #
#                                                                          #
############################################################################

def crudl_create(cls, id, content, **kwargs):
    if not cls in cls.app.parent(cls).children:
        cls.app.parent(cls).children[cls] = []
    if id in cls.app.parent(cls).children[cls]:
        raise Exception("You fucked up, man")
    cls.update(id, content, **kwargs)
    out = cls(id).id_dict()
    out["target"] = cls.name
    out["operation"] = "create"
    return jsonify(out)

def crudl_read(cls, id):
    if id in cls.app.parent(cls).children[cls]:
        return cls(id).json()
    abort(404)

def crudl_update(cls, id, content, **kwargs):
    out = cls(id, **kwargs)
    out.content = content
    if not cls in cls.app.parent(cls).children:
        cls.app.parent(cls).children[cls] = []
    if not id in cls.app.parent(cls).children[cls]:
        cls.app.parent(cls).children[cls].append(id)
    out = cls(id).id_dict()
    out["target"] = cls.name
    out["operation"] = "update"
    return jsonify(out)

def crudl_delete(cls, id):
    cls.app.parent(cls).children[cls].remove(id)
    out = cls(id).id_dict()
    del cls._cache[id]
    out["target"] = cls.name
    out["operation"] = "delete"
    return jsonify(out)

def crudl_delete_all(cls):
    for c in cls.app.parent(cls).children[cls]:
        del cls._cache[c]
    cls.app.parent(cls).children[cls] = []
    out = cls(id).id_dict()
    del out[cls.name+"_id"]
    out["target"] = cls.name
    out["operation"] = "delete_all"
    return jsonify(out)

def crudl_list(cls):
    out = cls.app.parent(cls).id_dict()
    out[cls.name+'_id'] = cls.app.parent(cls).children[cls]
    return jsonify(out)

class RegisteringMixin:
    '''
    Mixin introducing child resources registering.
    Users classes shouldn't inherit from this, but from FlaskResourceMixin or
    Resource (depending on intentions).
    
    Inheriting classes will have field children, which is dict mapping 
    (child class -> list of child instance ids)
    '''

    def __new__(cls, *args, **kwargs):
        out = super(RegisteringMixin, cls).__new__(cls, *args, **kwargs)
        out.children={}
        return out

    @classmethod
    def register_resource(cls, resource_cls):
        '''
        Class method, binding calling class with argument class in parent-child
        relation.
        '''
        resource_cls.app = cls.app
        resource_cls.parent_resource = cls
        #cls.children[resource_cls] = []
        multi = resource_cls.multi_part()
        single = resource_cls.single_part()
        to_register = []
        #       CRUDL method, and path)
        if 'C' in resource_cls.__crudl__:
            #@cls.app.route(rule=multi, methods=["POST"])
            def create(**kwargs):
                resource_cls._note_kwargs(**kwargs)
                kwargs[resource_cls.name+"_id"] = str(uuid.uuid4())
                data = request.data
                if data:
                    data = data.decode(request.content_encoding)
                out = resource_cls.create(id=kwargs[resource_cls.name+"_id"], content=data, **combined_multi_to_dict(request.values))
                resource_cls._clear_kwargs()
                return out
            create.__name__ = create.__name__+"_"+resource_cls.name
            to_register.append({"rule": multi, "method": "POST", "foo": create})
        if 'R' in resource_cls.__crudl__:
            #@cls.app.route(rule=single, methods=["GET"])
            def read(**kwargs):
                resource_cls._note_kwargs(**kwargs)
                out = resource_cls.read(id=kwargs[resource_cls.name+"_id"])
                resource_cls._clear_kwargs()
                return out
            read.__name__ = read.__name__ + "_"+resource_cls.name
            to_register.append({"rule": single, "method": "GET", "foo": read})
        if "U" in resource_cls.__crudl__:
            #@cls.app.route(rule=single, methods=["PUT"])
            def update(**kwargs):
                resource_cls._note_kwargs(**kwargs)
                data = request.data
                if data:
                    data = data.decode(request.content_encoding)
                out = resource_cls.update(id=kwargs[resource_cls.name+"_id"], content=data, **combined_multi_to_dict(request.values))
                resource_cls._clear_kwargs()
                return out
            update.__name__ = update.__name__ + "_"+resource_cls.name
            to_register.append({"rule": single, "method": "PUT", "foo": update})
        if "D" in resource_cls.__crudl__:
            #@cls.app.route(rule=single, methods=["DELETE"])
            def delete(**kwargs):
                resource_cls._note_kwargs(**kwargs)
                out = resource_cls.delete(id=kwargs[resource_cls.name+"_id"])
                resource_cls._clear_kwargs()
                return out
            delete.__name__ = delete.__name__+ "_"+resource_cls.name
            to_register.append({"rule": single, "method": "DELETE", "foo": delete})
        if "D*" in resource_cls.__crudl__:
            #@cls.app.route(rule=multi, methods=["DELETE"])
            def delete_all(**kwargs):
                resource_cls._note_kwargs(**kwargs)
                out = resource_cls.delete_all()
                resource_cls._clear_kwargs()
                return out
            delete_all.__name__ = delete_all.__name__+"_"+resource_cls.name
            to_register.append({"rule": multi, "method": "DELETE", "foo": delete_all})
        if "L" in resource_cls.__crudl__:
            #@cls.app.route(rule=multi, methods=["GET"])
            def list(**kwargs):
                resource_cls._note_kwargs(**kwargs)
                out = resource_cls.list()
                resource_cls._clear_kwargs()
                return out
            list.__name__ = list.__name__+ "_"+resource_cls.name
            to_register.append({"rule": multi, "method": "GET", "foo": list})
        if not hasattr(cls.app, "to_register"):
            cls.app.to_register = to_register
        else:
            cls.app.to_register += to_register

    def register_resource_routes(self):
        '''
        Call this at instance to register resource routes for it.
        '''
        for desc in type(self).to_register:
            self.app().route(rule=desc["rule"], methods=[desc['method']])(desc['foo'])
        del type(self).to_register

    @classmethod
    def _note_kwargs(cls, **kwargs):
        '''
        Unless you override standard CRUDL methods, you shouldn't use this.
        If you do, call this at the beginning of each method.
        It will bind request with its arguments (taken from url rule), so that
        parent() can work properly
        '''
        if not hasattr(cls.app, "_kwargs_cache"):
            cls.app._kwargs_cache = {}
        cls.app._kwargs_cache[hash(request)] = kwargs

    @classmethod
    def _clear_kwargs(cls):
        '''
        Unless you override standard CRUDL methods, you shouldn't use this.
        If you do, call this at the end of each method.
        It will remove binding request -> url rule args.
        '''
        del cls.app._kwargs_cache[hash(request)]

    @classmethod
    def parent(cls,src):
        '''
        Get parent resource instance for working request. If caller is top-level
        resource, it will return flask app.
        '''
        kwargs = dict(cls.app._kwargs_cache[hash(request)])
        temp = src

        ancestors = []      # collect ancestor classes, including app class
        while not issubclass(temp, Flask):
            ancestors = [temp.parent_resource] + ancestors
            temp = temp.parent_resource
        ancestors = ancestors[1:]   # remove app class

        if ancestors:   # if app was not only ancestor
            arg_name = ancestors[0].name+"_id"
            ancestor = ancestors[0](kwargs[arg_name])
            ancestors = ancestors[1:]
            del kwargs[arg_name]
            while not list(kwargs.keys()) in [ [], [src.name+"_id"] ]:
                arg_name = ancestors[0].name+"_id"
                if not kwargs[arg_name] in ancestor.children[type(ancestor)]:
                    raise Exception("Hierarchy is messed up")
                ancestor = ancestors[0](kwargs[arg_name])
                ancestors = ancestors[1:]
                del kwargs[arg_name]
            return ancestor
        else:
            return temp()

class FlaskResourceMixin(RegisteringMixin):
    '''
    Mixin for Flask app classes, enabling resource registration and adding some
    internal methods.
    '''
    @classmethod
    def single_part(cls):
        '''
        Return url rule for single resource choosing.
        Stub, for easier implementation.
        '''
        return ""

    @classmethod
    def multi_part(cls):
        '''
        Return url rule for choosing all resources from context.
        Stub, for easier implementation.
        '''
        return ""

    @classproperty
    def app(cls):
        '''
        Return app with which desired resource is bound.
        Stub, for easier implementation.
        '''
        return cls if isinstance(cls, type) else type(cls)

    @classmethod
    def id_dict(self_or_cls):
        '''
        Return dict representation of desired resource (allowing its localization).
        Stub, for easier implementation.
        '''
        return {}


class Resource(Flyweight, RegisteringMixin):
    '''
    Base class for resources.
    You should override name class property. By convention <name> will mean name
    property value.
    
    You should also override __crudl__ class field.
    It should contain collections being subset of default __crudl__ value - list
    of C, R, U, D, D*, L strings.
        | CRUDL stands for:
        | C - create
        | R - read
        | U - update
        | D - delete
        | L - list
    Depending on this fields values, appropriate REST methods will be created:
    C - create resource         (POST /<name>) - returns all data that allows
        us to recognise created resource
    R - read resource           (GET /<name>/<id>) - summarizes resource of 
        given type with given <id>, returns mentioned summary
    U - update resource         (PUT /<name>/<id>) - updated resource of given
        type, returning similiat output as C
    D - delete one resource     (DELETE /<name>/<id>) - delete resource of given
        type with given <id>
    D* - delete all resources   (DELETE /<name>) - delete all resources of given
        type
    L - list resources          (GET /<name>) - returns list of ids of every
        resource of given type
    
    Resources may be organized in hierarchies (with register_resource method of 
    resource). If resource B is child of resource A (so A is parent of A), then
    semantics change as below:
    C - POST /A/<A_id>/B - create new B resource as child of A with id <A_id>
    R - GET /A/<A_id>/B/<B_id> - get data of B instance if A with id <A_id> has
        child of type B with <B_id>, else return 404
    U - PUT /A/<A_id>/B/<B_id> - update data of chosen B instance; if chosen A
        instance has no described child, return 404
    D - DELETE /A/<A_id>/B/<B_id> - delete B instance with id <B_id>; if A with
        id <A_id> has no child of type B with id <B_id>, return 404
    D* - DELETE /A/<A_id>/B - delete all children of A with id <A_id> of type B
    L - GET /A/<A_id>/B - get all ids of children (with type B) of A with id <A_id>
    
    It may go for many levels; for example, if hierarchy looks like
        A -> B -> C -> D -> E
    (x -> y meaning "x is parent of y")
    then calling
    GET /A/<A_id>/B/<B_id>/C/<C_id>/D/<D_id>/E
    will list ids of all E instances which are child of D with id <D_id>, but only if:
      - A with id <A_id> has child B with id <B_id>
      - B with id <B_id> has child C with id <C_id>
      - C with id <C_id> has child D with id <D_id>
    else - it will return 404.
    
    Default implementation uses url rule arguments as id, HTTP arguments (after ?
    in url) as kwargs argument, and body of request as content.
    
    For example, request:
        POST /A?x=y
    with body:
        b'some_binary'
    will result in creation A instance with random (UUID v.4) id, kwargs={"x": "y"}:
        created_instance = A(str(uuid.uuid4()), x="y")
    and assigning:
        created_instance.content = b'some_binary'
    
    Create will raise Exception* if given id exists.
    Updating non-existing id will raise Exception*.
    
    * specialized exception classes are coming, marked as TODO
    '''

    __crudl__ = "C R U D D* L".split()

    @classproperty
    def name(cls):
        raise Exception("Override this!")


    def __init__(self, id, **kwargs):
        '''
        Remember id in id field, and keyword arguments as map in kwargs field.
        '''        
        self.id = id
        if not hasattr(self, "kwargs"):
            self.kwargs = kwargs
        else:
            self.kwargs.update(kwargs)


    ############################################################################
    #                                                                          #
    #                        CRUDL methods                                     #
    #                                                                          #
    ############################################################################

    @classmethod
    def create(cls, id, content, **kwargs):
        return crudl_create(cls, id, content, **kwargs)

    @classmethod
    def read(cls, id):
        return crudl_read(cls, id)

    @classmethod
    def update(cls, id, content, **kwargs):
        return crudl_update(cls, id, content, **kwargs)

    @classmethod
    def delete(cls, id):
        return crudl_delete(cls, id)

    @classmethod
    def delete_all(cls):
        return crudl_delete_all(cls)

    @classmethod
    def list(cls):
        return crudl_list(cls)

    ############################################################################
    #                                                                          #
    #                        technical stuff                                   #
    #                                                                          #
    ############################################################################

    @classmethod
    def single_part(cls):
        '''
        Return url rule for single resource choosing.
        For example, with hierarchy A->B (for notation see: class docstring)
        it will return (literally):
            /A/<A_id>/B/<B_id>
        because it points to single B instance.
        '''
        return cls.parent_resource.single_part() + ("/%(name)s/<%(name)s_id>" % {"name": cls.name})

    @classmethod
    def multi_part(cls):
        '''
        Return url rule for choosing all resources from context.
        For example, with hierarchy A->B (for notation see: class docstring)
        it will return (literally):
            /A/<A_id>/B
        because it points to all children of A with id <A_id> of type B.
        '''
        return cls.parent_resource.single_part() + ("/%(name)s" % {"name": cls.name})

    def id_dict(self):
        '''
        Return dict representation of desired resource (allowing its localization).
        '''
        parent = type(self).app.parent(type(self))
        out = parent.id_dict()
        out[ type(self).name+"_id" ] = self.id
        return out

    def json(self):
        '''
        JSONify representation of self, containing id, kwargs and content field.
        '''
        if self.content:
            return jsonify({ "id": self.id, "args": self.kwargs, "content": self.content })
        return jsonify({ "id": self.id, "args": self.kwargs, "content": ""})


