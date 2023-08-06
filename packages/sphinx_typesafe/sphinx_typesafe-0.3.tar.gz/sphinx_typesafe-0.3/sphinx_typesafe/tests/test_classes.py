from sphinx_typesafe.typesafe import typesafe


class ClassA(object):

    @typesafe
    def method_a1(self):
        """Function without arguments, returning void.
        """
        pass

    @typesafe
    def method_a2(self):
        """Function without arguments, returning one value.

        :rtype: int
        """
        return 42

    @typesafe
    def method_a3(self, a):
        """Function with one argument, returning void.

        :type a: int
        """
        pass

    @typesafe
    def method_a4(self, a):
        """Function with one argument, returning one value.

        :type a: types.IntType
        :rtype:  types.StringType
        """
        return '{}'.format(a)

    @typesafe
    def method_a5(self, a, b, c):
        """Function with various argument, returning one value.

        :type a: types.IntType
        :type b: types.IntType
        :type c: types.IntType
        :rtype:  types.StringType
        """
        return '{},{},{}'.format(a, b, c) 

    @typesafe
    def method_a6(self, p, q):
        """Function with various argument, returning one value.

        :type p: sphinx_typesafe.tests.geometry.Point
        :type q: sphinx_typesafe.tests.geometry.Point
        :rtype:  str
        """
        return '({},{}) - ({},{}) = {}'.format(p.x, p.y, q.x, q.y, p.distance(q))

    @typesafe
    def method_a7(self, a, b, x=0, y=0):
        '''
        :type a : int
        :type b : int
        :type x : int
        :type y : int
        :rtype  : int
        '''
        return x

    @typesafe( {} )
    def method_b1(self):
        """Function without arguments, returning void."""
        pass

    @typesafe( { 'return': 'int' } )
    def method_b2(self):
        """Function without arguments, returning one value."""
        return 42

    @typesafe( { 'a' : 'int' } )
    def method_b3(self, a):
        """Function with one argument, returning void."""
        pass

    @typesafe( { 'a'     : 'types.IntType', 
                 'return': 'types.StringType' } )
    def method_b4(self, a):
        """Function with one argument, returning one value."""
        return '{}'.format(a)

    @typesafe( { 'a'     : 'types.IntType', 
                 'b'     : 'types.IntType', 
                 'c'     : 'types.IntType', 
                 'return': 'types.StringType' } )
    def method_b5(self, a, b, c):
        """Function with various arguments, returning one value."""
        return '{},{},{}'.format(a, b, c) 

    @typesafe( { 'p'     : 'sphinx_typesafe.tests.geometry.Point', 
                 'q'     : 'sphinx_typesafe.tests.geometry.Point', 
                 'return': 'str' } )
    def method_b6(self, p, q):
        """Function with various arguments, returning one value."""
        return '({},{}) - ({},{}) = {}'.format(p.x, p.y, q.x, q.y, p.distance(q))

    @typesafe({ 'a' : 'int',
                'b' : 'int',
                'x' : 'int',
                'y' : 'int',
                'return' : 'int' })
    def method_b7(self, a, b, x=0, y=0):
        return x


def test_method_a1():
    c = ClassA()
    c.method_a1()


def test_method_a2():
    c = ClassA()
    assert(c.method_a2() == 42)


def test_method_a3():
    c = ClassA()
    c.method_a3(5)


def test_method_a4():
    c = ClassA()
    assert(c.method_a4(42) == '42')


def test_method_a5():
    c = ClassA()
    assert(c.method_a5(1,2,3) == '1,2,3')


def test_method_a6():
    from sphinx_typesafe.tests.geometry import Point
    p = Point(-2.0, -1.0)
    q = Point( 1.0,  3.0)
    c = ClassA()
    assert(c.method_a6(p, q) == '(-2.0,-1.0) - (1.0,3.0) = 5.0')


def test_method_a7():
    c = ClassA()
    c.method_a7(a=5, b=3)


def test_method_b1():
    c = ClassA()
    c.method_b1()


def test_method_b2():
    c = ClassA()
    assert(c.method_b2() == 42)


def test_method_b3():
    c = ClassA()
    c.method_b3(5)


def test_method_b4():
    c = ClassA()
    assert(c.method_b4(42) == '42')


def test_method_b5():
    c = ClassA()
    assert(c.method_b5(1,2,3) == '1,2,3')


def test_method_b6():
    from sphinx_typesafe.tests.geometry import Point
    p = Point(-2.0, -1.0)
    q = Point( 1.0,  3.0)
    c = ClassA()
    assert(c.method_b6(p, q) == '(-2.0,-1.0) - (1.0,3.0) = 5.0')


def test_method_b7():
    c = ClassA()
    c.method_b7(b=3, a=5)
