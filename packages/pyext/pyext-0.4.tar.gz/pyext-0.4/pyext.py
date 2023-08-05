'''
Copyright (C) 2013 Ryan Gonzalez


Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

g_backup = globals().copy()

__all__ = ['overload', 'RuntimeModule', 'switch', 'tail_recurse', 'copyfunc', 'set_docstring', 'annotate', 'safe_unpack', 'modify_function']

import sys, inspect, types

def __targspec(func, specs, attr='__orig_arg__'):
    if hasattr(func, '__is_overload__') and func.__is_overload__:
        return getattr(func, attr)
    return specs(func)

def set_docstring(doc):
    '''A simple decorator to set docstrings.
       
       :param doc: The docstring to tie to the function.
       
       Example::
          
          @set_docstring('This is a docstring')
          def myfunc(x):
              pass'''
    def _wrap(f):
        f.__doc__ = doc
        return f
    return _wrap

__modify_function_doc = '''
Creates a copy of a function, changing its attributes.

:param globals: Will be added to the function's globals.

:param name: The new function name. Set to ``None`` to use the function's original name.

:param code: The new function code object. Set to ``None`` to use the function's original code object.

:param defaults: The new function defaults. Set to ``None`` to use the function's original defaults.

:param closure: The new function closure. Set to ``None`` to use the function's original closure.

.. warning:: This function can be potentially dangerous.
'''

def copyfunc(f):
   '''Copies a funcion.
      
      :param f: The function to copy.
      
      :return: The copied function.
      
      .. deprecated:: 0.4
         Use :func:`modify_function` instead.
      '''
   return modify_function(f)

if sys.version_info.major == 3:
    @set_docstring(__modify_function_doc)
    def modify_function(f, globals={}, name=None, code=None, defaults=None,
                        closure=None):
        if code is None: code = f.__code__
        if name is None: name = f.__name__
        if defaults is None: defaults = f.__defaults__
        if closure is None: closure = f.__closure__
        newf = types.FunctionType(code, dict(f.__globals__, **globals), name=name,
                                  argdefs=defaults, closure=closure)
        newf.__dict__.update(f.__dict__)
        return newf
    def argspec(f):
        return inspect.getfullargspec(f)
    def _exec(s, g):
        exec(s, g)
    ofullargspec = inspect.getfullargspec
    def _fullargspec(func):
        return __targspec(func, ofullargspec)
    inspect.getfullargspec = _fullargspec
else:
    @set_docstring(__modify_function_doc)
    def modify_function(f, globals={}, name=None, code=None, defaults=None,
                        closure=None):
        if code is None: code = f.func_code
        if name is None: name = f.__name__
        if defaults is None: defaults = f.func_defaults
        if closure is None: closure = f.func_closure
        newf = types.FunctionType(code, dict(f.func_globals, **globals), name=name,
                                  argdefs=defaults, closure=closure)
        newf.__dict__.update(f.__dict__)
        return newf
    def argspec(f):
        return inspect.getargspec(f)
    eval(compile('def _exec(s, g): exec s in g', '<exec_function>', 'exec'))

def _gettypes(args):
    return tuple(map(type, args))

oargspec = inspect.getargspec

def _argspec(func):
    return __targspec(func, oargspec)

inspect.getargspec = _argspec

try:
    import IPython
except ImportError:
    IPython = None
else:
    # Replace IPython's argspec
    oipyargspec = IPython.core.oinspect.getargspec
    def _ipyargspec(func):
        return __targspec(func, oipyargspec, '__orig_arg_ipy__')
    IPython.core.oinspect.getargspec = _ipyargspec

class _overload(object):
    '''Simple function overloading in Python.'''
    _items = {}
    _types = {}
    def argc(self, argc=None):
        '''Overloads a function based on the specified argument count.

           :param argc: The argument count. Defaults to ``None``. If ``None`` is given, automatically compute the argument count from the given function.
           
           .. note::
              
              Keyword argument counts are NOT checked! In addition, when the argument count is automatically calculated, the keyword argument count is also ignored!
               
           Example::

               @overload.argc()
               def func(a):
                   print 'Function 1 called'
               
               @overload.argc()
               def func(a, b):
                   print 'Function 2 called'

               func(1) # Calls first function
               func(1, 2) # Calls second function
               func() # Raises error
               '''
        # Python 2 UnboundLocalError fix
        argc = {'argc': argc}
        def _wrap(f):
            def _newf(*args, **kwargs):
                if len(args) not in self._items[f.__name__]:
                    raise TypeError("No overload of function '%s' that takes %d args" % (f.__name__, len(args)))
                return self._items[f.__name__][len(args)](*args, **kwargs)
            if f.__name__ not in self._items:
                self._items[f.__name__] = {}
            if argc['argc'] is None:
                argc['argc'] = len(argspec(f).args)
            self._items[f.__name__][argc['argc']] = f
            _newf.__name__ = f.__name__
            _newf.__doc__ = f.__doc__
            _newf.__is_overload__ = True
            _newf.__orig_arg__ = argspec(f)
            if IPython:
                _newf.__orig_arg_ipy__ = IPython.core.oinspect.getargspec(f)
            return _newf
        return _wrap
    def args(self, *argtypes):
        '''Overload a function based on the specified argument types.

           :param argtypes: The argument types. If None is given, get the argument types from the function annotations(Python 3 only)
           
           Example::

               @overload.args(str)
               def func(s):
                   print 'Got string'

               @overload.args(int, str)
               def func(i, s):
                   print 'Got int and string'

               @overload.args()
               def func(i:int): # A function annotation example
                   print 'Got int'

               func('s')
               func(1)
               func(1, 's')
               func(True) # Raises error'''
        # Python 2 UnboundLocalError fix...again!
        argtypes = {'args': tuple(argtypes)}
        def _wrap(f):
            def _newf(*args):
                if _gettypes(args) not in self._types[f.__name__]:
                    raise TypeError("No overload of function '%s' that takes '%s' types and %d arg(s)" % (f.__name__, _gettypes(args), len(args)))
                return self._types[f.__name__][_gettypes(args)](*args)
            if f.__name__ not in self._types:
                self._types[f.__name__] = {}
            if len(argtypes['args']) == 1 and argtypes['args'][0] is None:
                aspec = argspec(f)
                argtypes['args'] = tuple(map(lambda x: x[1], sorted(
                    aspec.annotations.items(), key=lambda x: aspec.args.index(x[0]))))
            self._types[f.__name__][argtypes['args']] = f
            _newf.__name__ = f.__name__
            _newf.__doc__ = f.__doc__
            _newf.__is_overload__ = True
            _newf.__orig_arg__ = argspec(f)
            if IPython:
                _newf.__orig_arg_ipy__ = IPython.core.oinspect.getargspec(f)
            return _newf
        return _wrap

overload = _overload()

class _RuntimeModule(object):
    'Create a module object at runtime and insert it into sys.path. If called, same as :py:func:`from_objects`.'
    def __call__(self, *args, **kwargs):
        return self.from_objects(*args, **kwargs)
    @staticmethod
    @overload.argc(1)
    def from_objects(name, **d):
        return _RuntimeModule.from_objects(name, '', **d)
    @staticmethod
    @overload.argc(2)
    def from_objects(name, docstring, **d):
        '''Create a module at runtime from `d`.
           
           :param name: The module name.
           
           :param docstring: Optional. The module's docstring.
           
           :param d: All the keyword args, mapped from name->value.
           
           Example: ``RuntimeModule.from_objects('name', 'doc', a=1, b=2)``'''
        module = types.ModuleType(name, docstring)
        module.__dict__.update(d)
        module.__file__ = '<runtime_module>'
        sys.modules[name] = module
        return module
    @staticmethod
    @overload.argc(2)
    def from_string(name, s):
        return _RuntimeModule.from_string(name, '', s)
    @staticmethod
    @overload.argc(3)
    def from_string(name, docstring, s):
        '''Create a module at runtime from `s``.
           
           :param name: The module name.

           :param docstring: Optional. The module docstring.

           :param s: A string containing the module definition.'''
        g = {}
        _exec(s, g)
        return _RuntimeModule.from_objects(name, docstring, **dict(filter(lambda x: x[0] not in g_backup, g.items())))

RuntimeModule = _RuntimeModule()

class CaseObject(object):
    'The object returned by a switch statement. When called, it will return True if the given argument equals its value, else False.'
    def __init__(self, value):
        self.value = value
    def __call__(self, other):
        return self.value == other
    def __iter__(self):
        yield self
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

class _switch(object):
    '''A Python switch statement implementation that can be used either with a ``with`` statement or as an iterator.

       :param value: The value to "switch".

       ``with`` statement example::

           with switch('x'):
               if case(1): print 'Huh?'
               if case('x'): print 'It works!!!'
       
       Iterator example::

           for case in switch('x'):
               if case(1): print 'Huh?'
               if case('x'): print 'It works!!!'
       
       .. warning:: If you modify a variable named "case" in the same scope that you use the ``with`` statement version, you will get an UnboundLocalError. The soluction is to use ``with switch('x') as case:`` instead of ``with switch('x'):``.
       
       .. warning:: Using as an iterator is DEPRECATED!'''
    def __call__(self, value):
        res = CaseObject(value)
        inspect.stack()[1][0].f_globals['case'] = res
        return res

switch = _switch()

def tail_recurse(spec=None):
    '''Remove tail recursion from a function.

       :param spec: A function that, when given the arguments, returns a bool indicating whether or not to exit. If ``None,`` tail recursion is always called unless the function returns a value.
       
       .. note::
           
           This function has a slight overhead that is noticable when using timeit. Only use it if the function has a possibility of going over the recursion limit.

       Example::

           @tail_recurse()
           def add(a, b):
               if a == 0: return b
               return add(a-1, b+1)

           add(10000000, 1) # Doesn't max the recursion limit.
           '''
    def _wrap(f):
        class TailRecursion(Exception):
            def __init__(self, args, kwargs):
                self.args = args
                self.kwargs = kwargs
        def _newf(*args, **kwargs):
            if inspect.stack()[1][3] == f.__name__:
                if (spec and spec(args)) or not spec:
                    raise TailRecursion(args, kwargs)
            while True:
                try:
                    res = f(*args, **kwargs)
                except TailRecursion as ex:
                    args = ex.args
                    kwargs = ex.kwargs
                    continue
                else:
                    return res
        _newf.__doc__ = f.__doc__
        return _newf
    return _wrap

def annotate(*args, **kwargs):
    '''Set function annotations using decorators.
       
       :param args: This is a list of annotations for the function, in the order of the function's parameters. For example, ``annotate('Annotation 1', 'Annotation 2')`` will set the annotations of parameter 1 of the function to ``Annotation 1``.
       
       :param kwargs: This is a mapping of argument names to annotations. Note that these are applied *after* the argument list, so any args set that way will be overriden by this mapping. If there is a key named `ret`, that will be the annotation for the function's return value.
       
       Example::
           
           @annotate('This is for parameter 1', b='This is for b', ret='This is the return annotation')
           def x(a, b):
               pass'''
    def _wrap(f):
        if not hasattr(f, '__annotations__'):
            f.__annotations__ = {}
        if 'ret' in kwargs:
            f.__annotations__['return'] = kwargs.pop('ret')
        f.__annotations__.update(dict(zip(argspec(f).args, args)))
        f.__annotations__.update(kwargs)
        return f
    return _wrap

def safe_unpack(seq, ln, fill=None):
    '''Safely unpack a sequence to length `ln`, without raising ValueError. Based on Lua's method of unpacking. Empty values will be filled in with `fill`, while any extra values will be cut off.
       
       :param seq: The sequence to unpack.
       
       :param ln: The expected length of the sequence.
       
       :param fill: The value to substitute if the sequence is too small. Defaults to ``None``.
       
       Example::
           
           s = 'a:b'
           a, b = safe_unpack(s.split(':'), 2)
           # a = 'a'
           # b = 'b'
           s = 'a'
           a, b = safe_unpack(s.split(':'), 2)
           # a = 'a'
           # b = None'''
    if len(seq) > ln:
        return seq[:ln]
    elif len(seq) < ln:
        return seq + type(seq)([fill]*(ln-len(seq)))
    else:
        return seq

