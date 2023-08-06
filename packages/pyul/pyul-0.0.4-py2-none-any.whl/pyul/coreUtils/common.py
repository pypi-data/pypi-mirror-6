import os
import re
import types
from pyul.support import Path

__all__ = ['getClassName','wildcardToRe',
           'getUserTempDir','synthesize']

def getClassName(x):
    if not isinstance(x, basestring):
        if type(x) in [types.FunctionType, types.TypeType, types.ModuleType] :
            return x.__name__
        else:
            return x.__class__.__name__
    else:
        return x

def wildcardToRe(pattern):
    """Translate a wildcard pattern to a regular expression"""
    i, n = 0, len(pattern)
    res = '(?i)' #case insensitive re
    while i < n:
        c = pattern[i]
        i = i+1
        if c == '*':
            res = res + r'[^\\]*'
        elif c == '/':
            res = res + re.escape('\\')
        else:
            res = res + re.escape(c)
    return res + "$"

def getUserTempDir(temp_dirname='.tmp'):
    """
    Returns a path to a temp directory within the user folder
    
    :param dirname: A string representing the temp folder's name
    
    """
    return Path(os.path.expanduser('~')).joinpath(temp_dirname)

def synthesize(inst, name, value, readonly=False):
    """
    Convenience method to create getters, setters and a property for the instance.
    Should the instance already have the getters or setters defined this won't add them
    and the property will reference the already defined getters and setters
    Should be called from within __init__. Creates [name], get[Name], set[Name], 
    _[name] on inst.

    :param inst: An instance of the class to add the methods to.
    :param name: The base name to build the function names, and storage variable.
    :param value: The initial state of the created variable.

    """
    cls = type(inst)
    storageName = '_{0}'.format(name)
    getterName = 'get{0}{1}'.format(name[0].capitalize(), name[1:])
    setterName = 'set{0}{1}'.format(name[0].capitalize(), name[1:])
    deleterName = 'del{0}{1}'.format(name[0].capitalize(), name[1:])

    setattr(inst, storageName, value)
    
    #We always define the getter
    def customGetter(self):
        return getattr(self, storageName)

    #Add the Getter
    if not hasattr(inst, getterName):
        setattr(cls, getterName, customGetter)
    
    #Handle Read Only
    if readonly :
        if not hasattr(inst, name):
            setattr(cls, name, property(fget=getattr(cls, getterName, None) or customGetter, fdel=getattr(cls, getterName, None)))
    else:
        #We only define the setter if we arn't read only
        def customSetter(self, state):
            setattr(self, storageName, state)        
        if not hasattr(inst, setterName):
            setattr(cls, setterName, customSetter)
        member = None
        if hasattr(cls, name):
            #we need to try to update the property fget, fset, fdel incase the class has defined its own custom functions
            member = getattr(cls, name)
            if not isinstance(member, property):
                raise ValueError('Member "{0}" for class "{1}" exists and is not a property.'.format(name, cls.__name__))
        #Reguardless if the class has the property or not we still try to set it with
        setattr(cls, name, property(fget=getattr(member, 'fget', None) or getattr(cls, getterName, None) or customGetter,
                                    fset=getattr(member, 'fset', None) or getattr(cls, setterName, None) or customSetter,
                                    fdel=getattr(member, 'fdel', None) or getattr(cls, getterName, None)))

