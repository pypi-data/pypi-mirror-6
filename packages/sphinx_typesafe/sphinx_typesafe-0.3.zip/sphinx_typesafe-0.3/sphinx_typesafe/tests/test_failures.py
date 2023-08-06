from sphinx_typesafe.typesafe import typesafe


@typesafe
def function_f1a(x):
    """Function with one argument, returning one value.

    :type x: types.IntType
    :rtype:  types.StringType
    """
    return '{}'.format(x)


@typesafe({ 'x': 'types.IntType', 
            'return': 'types.StringType'} )
def function_f1b(x):
    """Function with one argument, returning one value.
    """
    return '{}'.format(x)


def test_function_fail_01():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe( 'rubbish' )
        def some_function():
            pass
        some_function()


def test_function_fail_02():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe( {}, 'rubbish' )
        def some_function():
            pass
        some_function()


def test_function_fail_03a():
    import pytest
    with pytest.raises(NameError):
        @typesafe( { 'a' : None } )
        def function_identity(x):
            return x
        function_identity(42)


def test_function_fail_03b():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe( { 'a' : '' } )
        def function_identity(x):
            return x
        function_identity(42)


def test_function_fail_03c():
    import pytest
    with pytest.raises(NameError):
        @typesafe( { 'a' : 5 } )
        def function_identity(x):
            return x
        function_identity(42)


def test_function_fail_03d():
    import pytest
    with pytest.raises(NameError):
        @typesafe( { 'a' : int } )
        def function_identity(x):
            return x
        function_identity(42)


def test_function_fail_03e():
    import pytest
    with pytest.raises(NameError):
        @typesafe( { str : int } )
        def function_identity(x):
            return x
        function_identity(42)


def test_function_fail_a3f():
    import pytest
    from sphinx_typesafe.tests.geometry import Point
    p = Point(3.0, 4.0)
    with pytest.raises(NameError):
        @typesafe( { p : int } )
        def function_identity(x):
            return x
        function_identity(42)


def test_function_success_04a():
    @typesafe
    def function_identity(x):
        '''
        :type x:int
        :rtype:int
        '''
        return x
    function_identity(42)


def test_function_success_04b():
    @typesafe
    def function_identity(x):
        '''
        :type    x   :    int     
        :rtype       :    int     
        '''
        return x
    function_identity(42)


def test_function_success_04c():
    @typesafe( { 'x'      : 'int',
                 'return' : 'int' } )
    def function_identity(x):
        return x
    function_identity(42)


def test_function_success_04d():
    @typesafe( { '  x  '      : '   int   ',
                 '  return  ' : '   int   ' } )
    def function_identity(x):
        return x
    function_identity(42)


def test_function_fail_05a():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(x):
            return x
        some_function(42)


def test_function_fail_05b():
    import pytest
    with pytest.raises(TypeError):
        @typesafe
        def some_function(x):
            '''
            :type x : int
            '''
            return x
        some_function(42)


def test_function_fail_05c():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(x):
            '''
            :type x : int
            :type y : int
            '''
            return x
        some_function(42)


def test_function_fail_05d():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function_(x):
            '''
            :type x : int
            :type y : int
            :rtype  : int
            '''
            return x
        some_function_(42)


def test_function_fail_05e():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(x):
            '''
            :type x: int
            :type y: int
            :rtype : int
            '''
            return x
        some_function()


def test_function_failure_05f():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(a, b, x=0, y=0):
            '''
            :type a : int
            :type b : int
            :type x : int
            :type y : int
            '''
            return x
        some_function(b=3)


def test_function_failure_05g():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(a, b, x=0, y=0):
            '''
            :type a : int
            :type b : int
            :type x : int
            :type y : int
            :type r : int
            :rtype  : int
            '''
            return x
        some_function(a=5, b=3)


def test_function_failure_05h():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(a, b, x=0, y=0):
            '''
            :type a : int
            :type b : int
            :type x : int
            :type y : int
            :type r : int
            :type s : int
            :rtype  : int
            '''
            return x
        some_function(a=5, b=3)


def test_function_fail_06a():
    import pytest
    with pytest.raises(AttributeError):
        @typesafe
        def some_function(a, b, c, d, e, f):
            """Function with argument which should not be checked and arguments missing specification.

            :type a: types.NotImplementedType
            :type b: types.IntType
            :rtype:  types.StringType
            """
            return '{},{}'.format(a, b) 
        assert(some_function('not checked',2) == 'not checked,2')


def test_function_fail_07a():
    import pytest
    with pytest.raises(TypeError):
        assert(function_f1a('rubbish') == '42')


def test_function_fail_07b():
    import pytest
    with pytest.raises(TypeError):
        assert(function_f1b('rubbish') == '42')


def test_function_fail_08a():
    import pytest
    with pytest.raises(TypeError):
        from sphinx_typesafe.tests.geometry import Point
        assert(function_f1a(Point(3.0, 4.0)) == '42')


def test_function_fail_08b():
    import pytest
    with pytest.raises(TypeError):
        from sphinx_typesafe.tests.geometry import Point
        assert(function_f1b(Point(3.0, 4.0)) == '42')


def test_function_fail_09a():
    import pytest
    with pytest.raises(TypeError):
        from sphinx_typesafe.tests.geometry import Point
        assert(function_f1a(type(Point(3.0, 4.0))) == '42')


def test_function_fail_09b():
    import pytest
    with pytest.raises(TypeError):
        from sphinx_typesafe.tests.geometry import Point
        assert(function_f1b(type(Point(3.0, 4.0))) == '42')
