'''
WHS Ltd. takes only partial credit for this module.

Implementation is based on pattern by Duncan Booth.

It is included here, because it nicely matches whole structure.
Also, small modifications were introduced.
'''
from functools import wraps


class Singleton:
    """
    Singleton class by Duncan Booth.
    Multiple object variables refers to the same object.
    http://www.suttoncourtenay.org.uk/duncan/accu/pythonpatterns.html
    (slightly modified by Filip Malczak)
    
    Inherit from this class to make it singleton.
    Instance automatically gets _initialized field. Usual constructor will look
    like this:
    
        def __init__(self, <some args, maybe *args or **kwargs>):
            if not self._initialized:
                <do some stuff with arguments>
                self._initialized = True

    Also, Duncan's implementation was changed, so that if A inherits from Singleton
    and B inherits from A, each class (A and B) will have different instances.
    """
    _instances = {}
    def __new__(cls, *args, **kwargs):
        if not cls in Singleton._instances:
            Singleton._instances[cls] = super(Singleton, cls).__new__(cls)
            Singleton._instances[cls]._initialized = False
        return Singleton._instances[cls]

class MetaSingleton(type):
    '''
    Metaclass which will add Singleton to base classes (if none of bases is
    already inheriting from it).
    Also, changes constructor, so it will be called once only (users implementation
    will be stored as __constructor__ method, and __init__ will be overloaded
    to inspect _initialized and call __constructor__ if needed; new __init__
    wraps provided, so signature won't change).

    This is WHS implementation, depending on Singleton class, we take credit for
    it.
    '''
    def __new__(cls, name, bases=(), dct={}, *args, **kwargs):
        try:
            constructor = dct["__init__"]
        except KeyError:
            if bases:
                if hasattr(bases[0], "__constructor__"):
                    constructor = bases[0].__constructor__
                else:
                    constructor = bases[0].__init__
            else:
                constructor = object.__init__
        @wraps(constructor)
        def __init__(self, *args, **kwargs):
            if not self._initialized:
                self.__constructor__(*args, **kwargs)
                self._initialized = True
        dct["__init__"] = __init__
        dct["__constructor__"] = constructor
        if not any([issubclass(x, Singleton) for x in bases]):
            bases = (Singleton, )+bases
        for x in bases:
            if issubclass(x, Singleton):
                dct['__new__']=x.__new__
                break
        return type.__new__(cls, name, bases, dct)

if __name__=="__main__":
    class A(metaclass=MetaSingleton):
        f = 0
        def __init__(self):
            print("A constructor")
            self.f += 1

    class B(A):
        g = 0
        def __init__(self):
            print("B constructor")
            self.g += 1

    print("A\n\n")

    print("class", A)
    print("meta", A.__class__)
    print("new", A.__new__)
    print("init", A.__init__)
    print("constr", A.__constructor__)
    print(dir(A))

    a = A()
    print("a", a)
    b = A()
    print("b", b)

    print(a==b)
    print(a is b)
    print(a.f)

    print("B\n\n")

    print("class", B)
    print("meta", B.__class__)
    print("new", B.__new__)
    print("init", B.__init__)
    print("constr", B.__constructor__)

    a = B()
    print("a", a)
    b = B()
    print("b", b)

    print(a==b)
    print(a is b)
    print(a.g)

    class C:
        pass

    class D(C, B):
        def __init__(self):
            print("Hi, wanna get some D?")

    d1 = D()
    d2 = D()
    print("d1", d1)
    print("d2", d2)
    print(d1 == d2)
    print(d1 is d2)