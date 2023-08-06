'''
composer.py - feature oriented composition of python code
'''
from __future__ import absolute_import
import inspect
import importlib
import sys
from functools import wraps
from .importhooks import LazyComposerHook
from .helpers import (_delegate, _is_class_instance, _get_role_name,
    _get_base_name, _get_method, _extract_classmethod, _extract_staticmethod)

def get_features_from_equation_file(filename):
    '''
    returns list of feature names read from equation file given
    by ``filename``.

    format: one feature per line; comments start with ``#``

    Example::

        #this is a comment
        basefeature
        #empty lines are ignored

        myfeature
        anotherfeature

    '''
    features = []
    for line in open(filename):
        line = line.split('#')[0].strip()
        if line:
            features.append(line)
    return features

class CompositionError(Exception): pass

class Composer(object):


    def _introduce(self, role, target_attrname, transformation, base):
        if hasattr(base, target_attrname):
            raise CompositionError(
                'Cannot introduce "%s" from "%s" into "%s"!'
                ' Attribute exists already!' % (
                    target_attrname,
                    _get_role_name(role),
                    _get_base_name(base),
                )
            )
        if callable(transformation):
            evaluated_trans = transformation()
            if not callable(evaluated_trans):
                raise CompositionError(
                    'Cannot introduce "%s" from "%s" into "%s"!'
                    ' Method Introduction is not callable!' % (
                        target_attrname,
                        _get_role_name(role),
                        _get_base_name(base),
                    )
                )
            setattr(base, target_attrname, _get_method(evaluated_trans, base))
        else:
            setattr(base, target_attrname, transformation)


    def _refine(self, role, target_attrname, transformation, base):
        if not hasattr(base, target_attrname):
            raise CompositionError(
                'Cannot refine "%s" of "%s" by "%s"!'
                ' Attribute does not exist in original!' % (
                    target_attrname,
                    _get_base_name(base),
                    _get_role_name(role),
                )
            )
        if callable(transformation):
            baseattr = getattr(base, target_attrname)
            if callable(baseattr):
                wrapper = self._create_refinement_wrapper(
                    transformation, baseattr, base, target_attrname
                )
                setattr(base, target_attrname, wrapper)
            else:
                setattr(base, target_attrname, transformation(baseattr))
        else:
            setattr(base, target_attrname, transformation)


    def _create_refinement_wrapper(self, transformation, baseattr, base, target_attrname):
        """
        applies refinement ``transformation`` to ``baseattr`` attribute of ``base``.
        ``baseattr`` can be any type of callable (function, method, functor)
        this method handles the differences.
        docstrings are also rescued from the original if the refinement
        has no docstring set.
        """
        #first step: extract the original
        special_refinement_type=None
        instance_refinement = _is_class_instance(base)

        if instance_refinement:
            dictelem = base.__class__.__dict__.get(target_attrname, None)
        else:
            dictelem = base.__dict__.get(target_attrname, None)


        if isinstance(dictelem, staticmethod):
            special_refinement_type = 'staticmethod'
            original = _extract_staticmethod(dictelem)
        elif isinstance(dictelem, classmethod):
            special_refinement_type = 'classmethod'
            original = _extract_classmethod(dictelem)
        else:
            if instance_refinement:
                #methods need a delegator
                original = _delegate(baseattr)
                ##TODO: evaluate this: 
                #original = base.__class__.__dict__[target_attrname]
            else:
                #default handling
                original = baseattr

        #step two: call the refinement passing it the original
        #the result is the wrapper
        wrapper = transformation(original)

        #rescue docstring
        if not wrapper.__doc__:
            wrapper.__doc__ = baseattr.__doc__

        #step three: make wrapper ready for injection
        if special_refinement_type == 'staticmethod':
            wrapper = staticmethod(wrapper)
        elif special_refinement_type == 'classmethod':
            wrapper = classmethod(wrapper)

        if instance_refinement:
            wrapper = wrapper.__get__(base, base.__class__)

        return wrapper


    def _apply_transformation(self, role, base, transformation, attrname):
        if attrname.startswith('introduce_'):
            target_attrname = attrname[len('introduce_'):]
            self._introduce(role, target_attrname, transformation, base)
        elif attrname.startswith('refine_'):
            target_attrname = attrname[len('refine_'):]
            self._refine(role, target_attrname, transformation, base)
        elif attrname.startswith('child_'):
            target_attrname = attrname[len('child_'):]
            refinement = transformation()
            self.compose(refinement, getattr(base, target_attrname))

    def _compose_pair(self, role, base):
        '''
        composes onto base by applying the role
        '''
        #apply transformations in role to base
        for attrname in dir(role):
            transformation = getattr(role, attrname)
            self._apply_transformation(role, base, transformation, attrname)

        return base


    def compose(self, *things):
        '''
        compose applies multiple fsts onto a base implementation.
        Pass the base implementation as last parameter.
        fsts are merged from RIGHT TO LEFT (like function application)
        e.g.:

        class MyFST(object):
            #place introductions and refinements here
            introduce_foo = 'bar'

        compose(MyFST(), MyClass)
        '''
        if not len(things):
            raise CompositionError('nothing to compose')
        if len(things) == 1:
            #composing one element is simple
            return things[0]
        else:
            #recurse after applying last role to object
            return self.compose(*(
                list(things[:-2]) #all but the last two 
                #plus the composition of the last two
                + [self._compose_pair(things[-2], things[-1])]
            ))


    def compose_later(self, *things):
        """
        register list of things for composition using compose()

        compose_later takes a list of fsts.
        The last element specifies the base module as string
        things are composed directly after the base module
        is imported by application code
        """
        if len(things) == 1:
            return things[0]
        module_name = things[-1]
        if module_name in sys.modules:
            raise CompositionError(
                'compose_later call after module has been imported: '
                 + module_name
            )
        LazyComposerHook.add(module_name, things[:-1], self)


    def select(self, *features):
        """
        selects the features given as string
        e.g
        passing 'hello' and 'world' will result in imports of
        'hello' and 'world'. Then, if possible 'hello.feature'
        and 'world.feature' are imported and select is called
        in each feature module.
        """
        for feature_name in features:
            feature_module = importlib.import_module(feature_name)
            #if available, import feature.py and select the feature
            try:
                feature_spec_module = importlib.import_module(
                    feature_name + '.feature'
                )
                if not hasattr(feature_spec_module, 'select'):
                    raise CompositionError(
                        'Function %s.feature.select not found!\n '
                        'Feature modules need to specify a function'
                        ' select(composer).' % (
                            feature_name
                        )
                    )
                args, varargs, keywords, defaults = inspect.getargspec(
                    feature_spec_module.select
                )
                if varargs or keywords or defaults or len(args) != 1:
                    raise CompositionError(
                        'invalid signature: %s.feature.select must '
                        'have the signature select(composer)' % (
                            feature_name
                        )
                    )
                #call the feature`s select function
                feature_spec_module.select(self)
            except ImportError:
                #Unfortunately, python makes it really hard
                #to distinguish missing modules from modules
                #that contain errors.
                #Hacks like parsing the exception message will
                #not work reliably due to import hooks and such.
                #Conclusion: features must contain a feature.py for now

                #reraise
                raise


    def select_equation(self, filename):
        """
        select features from equation file

        format: one feature per line; comments start with ``#``

        Example::

            #this is a comment
            basefeature
            #empty lines are ignored

            myfeature
            anotherfeature

        """
        features = get_features_from_equation_file(filename)
        self.select(*features)
