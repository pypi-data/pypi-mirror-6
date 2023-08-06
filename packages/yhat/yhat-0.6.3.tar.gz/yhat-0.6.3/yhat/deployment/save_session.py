import pickle
import ast
import inspect
import types
import json
import sys
import os
import dill


def _in_directory(filepath, directory):
    #make both absolute    
    directory = os.path.realpath(directory)
    filepath = os.path.realpath(filepath)
    #return true, if the common prefix of both is equal to directory
    #e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    return os.path.commonprefix([filepath, directory]) == directory

def _is_on_syspath(filepath):
    if filepath is None:
        return False
    for libpath in sys.path:
        if libpath==os.getcwd():
            continue
        elif libpath!="":
            if _in_directory(filepath, libpath)==True:
                return True
    return False

def _get_source(func):
    """
    Gets the source of a function and handles cases when user is in an 
    interactive session

    func: function
        a function who's source we want
    """
    try:
        return inspect.getsource(func)
    except:
        if inspect.isclass(func):
            source = ""
            source += "class %s(%s):" % (func.__name__, func.__base__.__name__)
            source += "\n"
            for name, method in inspect.getmembers(func, predicate=inspect.ismethod):
                if hasattr(method, '__wrapped_func__'):
                    wrapped_source = dill.source.getsource(method.__wrapped_func__)
                    wrapped_source = wrapped_source.split('\n')
                    nchar = len(wrapped_source[1]) - len(wrapped_source[1].lstrip())
                    wrapped_source[0] = " "*nchar + wrapped_source[0]
                    wrapped_source = "\n".join(wrapped_source)
                    wrapped_source = "\n" + wrapped_source + "\n"
                    source += wrapped_source
                else:
                    source += inspect.getsource(method) + "\n"
        else:
            return inspect.getsource(func) + "\n"
        return source


def _strip_function_source(src):
    """
    Takes the source code of a function and dedents it so that it.

    Parameters
    ----------
    src: string
        function code

    Returns
    -------
    source: string
        source code of the same function, but "dedented"
    """
    src = src.split('\n')
    n = len(src[0]) - len(src[0].lstrip())
    return "\n".join([line[n:] for line in src])

def _get_naked_loads(function):
    """
    Takes a reference to a function and determines which variables used in the 
    function are not defined within the scope of the function.

    Parameters
    ----------
    function: function

    Returns
    -------
    variables: generator
        returns the variables in a function that are not:
            1) passed in as parameters 
            2) created within the scope of the function
    """
    source = _get_source(function)
    source = _strip_function_source(source)
    tree = ast.parse(source)
    params = set()
    loaded = set()
    created = set()
    for thing in ast.walk(tree):
        thingvars = vars(thing)
        if "ctx" in thingvars:
            if isinstance(thingvars['ctx'], ast.Param):
                params.add(thingvars['id'])
            elif isinstance(thingvars['ctx'], ast.Load):
                if 'id' in thingvars:
                    loaded.add(thingvars['id'])
                    # variable = thingvars['id']
                    # if variable not in params and variable not in created:
                        # yield variable
            elif isinstance(thingvars['ctx'], ast.Store):
                if 'id' in thingvars:
                    created.add(thingvars['id'])
    
    for variable in loaded:
        # TODO: if created but loaded before that as something else
        if variable not in params and variable not in created:
            yield variable

def _spider_function(function, session, pickles={}):
    # TODO: need to grab variables passed as kwargs to decorators
    # TODO: some issues in regards to the order in which classes are defined
    # and inherited from
    # TODO: currently doesn't support "local modules"
    """
    Takes a function and global variables referenced in an environment and 
    recursively finds dependencies required in order to execute the function. 
    This includes references to classes, libraries, variables, functions, etc.

    Parameters
    ----------
    function: function
        a function referenced in an environment
    session: dictionary
        variables referenced from a seperate environment; i.e. globals()
    pickles: dictionary
        holds the variables needed to execute the function

    Returns
    -------
    imports: list
        list of import statements required for the function to execute
    source: string
        source code of the function
    pickles: dictionary
        dictionary of variable names and their values as pickled strings
    """
    if '_objects_seen' not in pickles:
        pickles['_objects_seen'] = []
    pickles['_objects_seen'].append(str(function))
    imports = []
    source = "# code for %s\n" % str(function)
    source += _get_source(function) + '\n'
    for varname in _get_naked_loads(function):
        if varname not in session:
            continue
        obj = session[varname]
        if hasattr(obj, '__call__'):
            # if it's a pre-installed library, just import it
            object_file = vars(inspect.getmodule(obj)).get('__file__')
            if _is_on_syspath(object_file):
                ref = inspect.getmodule(obj).__name__
                imports.append("from %s import %s" % (ref, varname))
            else:
                # check if we've already seen it
                if str(obj) in pickles['_objects_seen']:
                    continue
                new_imports, new_source, new_pickles = _spider_function(obj, session, pickles)
                source += new_source + '\n'
                imports += new_imports
                pickles.update(new_pickles)
        elif inspect.isclass(obj):
            object_file = vars(inspect.getmodule(obj)).get('__file__')
            if _is_on_syspath(object_file):
                ref = inspect.getmodule(obj).__name__
                imports.append("import %s as %s" % (ref, varname))
            else:
                source += _get_source(obj) + '\n'
                class_methods = inspect.getmembers(obj,
                                            predicate=inspect.ismethod)
                for name, method in class_methods:
                    for subfunc in _get_naked_loads(method):
                        if subfunc in session:
                            # check if we've already seen it
                            if str(obj) in pickles['_objects_seen']:
                                continue
                            new_imports, new_source, new_pickles = _spider_function(
                                    session[subfunc], session, pickles
                                )
                            source += new_source
                            imports += new_imports
                            pickles.update(new_pickles)
        else:
            if isinstance(obj, types.ModuleType):
                ref = inspect.getmodule(obj).__name__
                imports.append("import %s as %s" % (ref, varname))
                continue
            pickles[varname] = pickle.dumps(obj)
    return imports, source, pickles

def save_function(function, session):
    """
    Saves a user's session and all dependencies to a big 'ole JSON object with
    accompanying pickles for any variable.

    Parameters
    ----------
    function: function
        function we're saving
    session: dictionary
        globals() from the user's environment
    """
    imports, source_code, pickles = _spider_function(function, session)
    # de-dup and order the imports
    imports = sorted(list(set(imports)))
    imports.append("import json")
    imports.append("import pickle")
    source_code = "\n".join(imports) + "\n\n\n" + source_code
    pickles = {
        "objects": pickles,
        "code": source_code
    }

    if "_objects_seen" in pickles["objects"]:
        del pickles["objects"]["_objects_seen"]
    return pickles

