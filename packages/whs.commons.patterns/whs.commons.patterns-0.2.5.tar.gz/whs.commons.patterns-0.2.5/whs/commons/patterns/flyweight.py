from functools import wraps


class Flyweight:
    """
    Flyweight pattern by Filip Malczak.
    
    Inherit from this class, to ensure that every call to constructor with the
    same first argument (key) will return exactly the same instance.
    
    Instances have (by default) field _initialized, which is False. You probably
    wanna change its value to True after first initialization, so usual constructor
    will look like this:
    
        def __init__(self, key, arg1, arg2, <and more>):
            if not self._initialized:
                <do some stuff with key, arg1, arg2, <and more>, etc>
                self._initialized = True
    """
    _cache = {}
    def __new__(cls, key, *args, **kwargs):
        if not cls in Flyweight._cache:
            Flyweight._cache[cls] = {}
        if not key in Flyweight._cache[cls]:
            Flyweight._cache[cls][key] = super(Flyweight, cls).__new__(cls)
            Flyweight._cache[cls][key]._initialized = False
        return Flyweight._cache[cls][key]


class MetaFlyweight(type):
    '''
    Metaclass which will add Flyweight to base classes (if none of bases is
    already inheriting from it).
    Also, changes constructor, so it will be called once only (users implementation
    will be stored as __constructor__ method, and __init__ will be overloaded
    to inspect _initialized and call __constructor__ if needed; new __init__
    wraps provided, so signature won't change).
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
            print(self, "init")
            if not self._initialized:
                print("constr")
                self.__constructor__(*args, **kwargs)
                self._initialized = True
        dct["__init__"] = __init__
        dct["__constructor__"] = constructor
        if not any([issubclass(x, Flyweight) for x in bases]):
            bases = (Flyweight, )+bases
        for x in bases:
            if issubclass(x, Flyweight):
                dct['__new__']=x.__new__
                break
        return type.__new__(cls, name, bases, dct)

if __name__=="__main__":
    class A(metaclass=MetaFlyweight):
        x = 0
        def __init__(self, key):
            print("A init")
            self.x+=1

    class B(metaclass=MetaFlyweight):
        y = 0
        def __init__(self, key):
            self.y+=1

    a = A(1)
    b = A(1)
    x = A(2)
    print(a)
    print(b)
    print(a.x)
    print(x)
    print(a == b)
    print(a is b)
    print(a == x)
    print(a is x)

    c = B(1)
    d = B(1)
    print(c)
    print(c.y)
    print(c == a)
    print(c is a)
