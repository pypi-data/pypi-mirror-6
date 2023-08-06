import inspect

import debris
from debris import helpers


class Cache(type):
    def __call__(cls, *args, **kwargs):
        """Get any piece of data through a series of locations
        """
        _ = cls.__debris__

        # removes the repeated keyword arguments
        # Provide examples here....
        #
        [kwargs.pop(k) for k in inspect.getargspec(cls.__init__).args if k in kwargs]

        # Build the collection of initializing variables
        # this will be used for varius callable requests
        #
        _initvars = dict(clsname=cls.__name__)
        insp = inspect.getargspec(cls.__init__)
        # remove the default "__debris__" argument
        insp.args.remove('__debris__')
        # remove the default "self" argument
        insp.args.remove('self')
        defaults = [None for x in range(len(insp.args) if args else 0)]
        if insp.defaults:
            _d = list(insp.defaults)
            _d.reverse()
            for x, d in enumerate(_d):
                defaults[x] = d
            defaults.reverse()
        _initvars.update(dict([(k, defaults.pop()) for k in insp.args]))
        _initvars.update(kwargs)

        # substiture class
        if _.get('substitute'):
            cls = helpers.call(_.get('substitute'))(cls, **_initvars)

        # namespace
        namespace = helpers.call(_.get('namespace'), **_initvars)
        namespace = namespace % _initvars
        
        # Must have namespace to stash
        if namespace:
            if type(namespace) is list:
                pass

            else:
                _in_memory = helpers.call(_.get('memory'), **_initvars)
                if _in_memory:
                    # check for this namespace
                    obj = debris.locale.Memory.get(namespace)
                    if obj:
                        return obj

                # get the data via the "retreive" method
                # which is required to be an attribute of the class, or a callable
                data = helpers.callattr(cls, _.get("retreive", "__assemble__"), **_initvars)

                obj = cls.__new__(cls, *args, **kwargs)
                obj.__init__(__debris__=data, *args, **kwargs)
                if _.get('stash') is not False:
                    pile = helpers.callattr(obj, _.get('locale'), **_initvars)
                    if type(pile) is str:
                        pile = getattr(debris, pile)
                    if pile:
                        if _.get('stash') is not True:
                            data = helpers.callattr(obj, _.get('stash'))
                        pile.stash(data, namespace)
                if _in_memory:
                    debris.locale.Memory.set(namespace, obj)
                return obj

        # namespace was not found true therfore
        # construct the object normally, dont stash it.
        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(*args, **kwargs)
        return obj
