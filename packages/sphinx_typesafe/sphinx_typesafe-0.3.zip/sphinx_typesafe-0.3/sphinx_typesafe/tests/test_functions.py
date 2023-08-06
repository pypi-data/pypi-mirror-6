from sphinx_typesafe.typesafe import typesafe


def test_function_01a():
    @typesafe
    def some_function():
        """Function without arguments, returning void (implicit)
        """
        pass
    some_function()


def test_function_01b():
    @typesafe
    def some_function():
        """Function without arguments, returning void (explicit)

        :rtype: None
        """
        pass
    some_function()


def test_function_01c():
    @typesafe
    def some_function():
        """Function without arguments, returning void (explicit)

        :rtype: types.NoneType
        """
        pass
    some_function()


def test_function_02a():
    @typesafe
    def some_function():
        """Function without arguments, returning one value.

        :rtype: int
        """
        return 42
    assert(some_function() == 42)


def test_function_02b():
    @typesafe
    def some_function(a):
        """Function with one argument, returning void (explicit)

        :type a: int
        :rtype: None
        """
        pass
    some_function(5)


def test_function_02c():
    @typesafe
    def some_function(a):
        """Function with one argument, returning one value.

        :type a: types.IntType
        :rtype:  types.StringType
        """
        return '{}'.format(a)
    assert(some_function(42) == '42')


def test_function_02d():
    @typesafe
    def some_function(a, b, c):
        """Function with various argument, returning one value.

        :type a: types.IntType
        :type b: types.IntType
        :type c: types.IntType
        :rtype:  types.StringType
        """
        return '{},{},{}'.format(a, b, c) 
    assert(some_function(1,2,3) == '1,2,3')


def test_function_03a():
    from sphinx_typesafe.tests.geometry import Circle
    c = Circle(-2.0, -1.0, 5.0)

    @typesafe
    def some_function(c):
        """Function with various argument, returning one value.

        :type c: sphinx_typesafe.tests.geometry.Circle
        :rtype:  str
        """
        return '({},{}, {}) = {}'.format(c.x, c.y, c.r, c.area())
    assert(some_function(c) == '(-2.0,-1.0, 5.0) = 78.5398163397')


def test_function_03b():
    from sphinx_typesafe.tests.geometry import Point
    p = Point(-2.0, -1.0)
    q = Point( 1.0,  3.0)

    @typesafe
    def some_function(p, q):
        """Function with various argument, returning one value.

        :type p: sphinx_typesafe.tests.geometry.Point
        :type q: sphinx_typesafe.tests.geometry.Point
        :rtype:  str
        """
        return '({},{}) - ({},{}) = {}'.format(p.x, p.y, q.x, q.y, p.distance(q))
    assert(some_function(p, q) == '(-2.0,-1.0) - (1.0,3.0) = 5.0')


def test_function_03c():
    from sphinx_typesafe.tests.geometry import Circle
    from sphinx_typesafe.tests.geometry import Point
    c = Circle(-2.0, -1.0, 5.0)
    p = Point( 1.0,  4.0)

    @typesafe
    def some_function(c, p):
        """Function with various argument, returning one value.

        :type c: sphinx_typesafe.tests.geometry.Circle
        :type p: sphinx_typesafe.tests.geometry.Point
        :rtype:  str
        """
        return '({},{},{}) - ({},{}) = {}'.format(c.x, c.y, c.r, p.x, p.y, c.distance(p))
    assert(some_function(c, p) == '(-2.0,-1.0,5.0) - (1.0,4.0) = 0.830951894845')


def test_function_04a():
    @typesafe
    def some_function(a, b):
        """Function with argument which should not be checked.

        :type a: types.NotImplementedType
        :type b: types.IntType
        :rtype:  types.StringType
        """
        return '{},{}'.format(a, b) 
    assert(some_function('not checked',2) == 'not checked,2')


def test_function_11a():
    @typesafe( {} )
    def some_function():
        """Function without arguments, returning void."""
        pass
    some_function()


def test_function_11b():
    @typesafe( { 'return': 'int' } )
    def some_function():
        """Function without arguments, returning one value."""
        return 42
    assert(some_function() == 42)


def test_function_11c():
    @typesafe( { 'a' : 'int' } )
    def some_function(a):
        """Function with one argument, returning void."""
        pass
    some_function(5)


def test_function_11d():
    @typesafe( { 'a'     : 'types.IntType', 
                 'return': 'types.StringType' } )
    def some_function(a):
        """Function with one argument, returning one value."""
        return '{}'.format(a)
    assert(some_function(42) == '42')


def test_function_11e():
    @typesafe( { 'a'     : 'types.IntType', 
                 'b'     : 'types.IntType', 
                 'c'     : 'types.IntType', 
                 'return': 'types.StringType' } )
    def some_function(a, b, c):
        """Function with various arguments, returning one value."""
        return '{},{},{}'.format(a, b, c) 
    assert(some_function(1,2,3) == '1,2,3')


def test_function_11f():
    from sphinx_typesafe.tests.geometry import Point
    p = Point(-2.0, -1.0)
    q = Point( 1.0,  3.0)

    @typesafe( { 'p'     : 'sphinx_typesafe.tests.geometry.Point', 
                 'q'     : 'sphinx_typesafe.tests.geometry.Point', 
                 'return': 'str' } )
    def some_function(p, q):
        """Function with various arguments, returning one value."""
        return '({},{}) - ({},{}) = {}'.format(p.x, p.y, q.x, q.y, p.distance(q))
    assert(some_function(p, q) == '(-2.0,-1.0) - (1.0,3.0) = 5.0')
