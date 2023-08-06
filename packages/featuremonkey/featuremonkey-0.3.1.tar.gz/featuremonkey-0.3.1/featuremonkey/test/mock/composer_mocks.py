class Base(object):
    
    base_prop = 8
    
    def base_method(self, a_str):
        return a_str


class MemberIntroduction(object):
    introduce_a = 1

class ExistingMemberIntroduction(object):
    introduce_base_prop = 1

class MethodIntroduction(object):

    def introduce_method(self):
        
        def method(self):
            return True
        
        return method

class MethodRefinement(object):
    
    def refine_base_method(self, original):
        
        def base_method(self, a_str):
            return original(self, a_str) + 'refined'
        
        return base_method


class MethodRefinement2(object):
    
    def refine_base_method(self, original):
        
        def base_method(self, a_str):
            return original(self, a_str) + 'refined'
        
        return base_method


class StaticBase(object):

    @staticmethod
    def base_method(a_str):
        return a_str


class StaticMethodRefinement(object):

    def refine_base_method(self, original):

        def base_method(a_str):
            return original(a_str) + 'refined'

        return base_method


class ClassMethodBase(object):

    @classmethod
    def base_method(cls, a_str):
        return a_str


class ClassMethodRefinement(object):

    def refine_base_method(self, original):

        def base_method(cls, a_str):
            return original(cls, a_str) + 'refined'

        return base_method



