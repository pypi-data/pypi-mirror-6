#######################################################
#                                                     #
# This modules demonstrates only few common use cases #
#                                                     #
#######################################################


from sphinx_typesafe.typesafe import typesafe


@typesafe
def f_1(a, b, c):
    """
    :type a: types.StringType
    :type b: types.StringType
    :type c: types.StringType
    :rtype:  types.StringType
    """
    return '{}+{}+{}'.format(a, b, c) 


@typesafe({ 'a': 'types.StringType',
            'b': 'types.StringType',
            'c': 'types.StringType',
            'return': 'types.StringType', })
def f_2(a, b, c):
    return '{}+{}+{}'.format(a, b, c) 


class ClassA(object):

    def __init__(self):
        self.x = 'ClassA:'

    @typesafe
    def method_1(self, a, b, c):
        """
        :type a: types.StringType
        :type b: types.StringType
        :type c: types.StringType
        :rtype:  types.StringType
        """
        return '{} {}+{}+{}'.format(self.x, a, b, c) 

    @typesafe({ 'a': 'types.StringType',
                'b': 'types.StringType',
                'c': 'types.StringType',
                'return': 'types.StringType', })
    def method_2(self, a, b, c):
        return '{} {}+{}+{}'.format(self.x, a, b, c) 


def test_function():
    assert(f_1('a', 'b', 'c') == 'a+b+c')
    assert(f_2('a', 'b', 'c') == 'a+b+c')


def test_classA():
    c = ClassA()
    assert(c.method_1('a', 'b', 'c') == 'ClassA: a+b+c')
    assert(c.method_2('a', 'b', 'c') == 'ClassA: a+b+c')
