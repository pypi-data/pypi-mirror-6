from sphinx_typesafe.typesafe import typesafe


class Point(object):

    @typesafe
    def __init__(self, x=0.0, y=0.0):
        """Initialize a Point.
        :type x: float
        :type y: float
        """
        self.x = x
        self.y = y

    #@typesafe({ 'p': 'sphinx_typesafe.tests.geometry.Point',
    #            'result': 'float' })
    @typesafe
    def distance(self, p):
        """Calculates the distance to a Point p.

        :type p: sphinx_typesafe.tests.geometry.Point
        :rtype:  float
        """
        import math
        return math.sqrt( math.pow((self.x - p.x), 2) + math.pow((self.y - p.y), 2) )

    @typesafe
    def area(self):
        '''Returns the area of a Point, which is zero.

        :rtype: float
        '''
        return 0.0


class Circle(Point):

    @typesafe
    def __init__(self, x=0.0, y=0.0, r=0.0):
        """Initialize a Circle.
        :type x: float
        :type y: float
        :type r: float
        """
        super(Circle,self).__init__(x, y)
        self.r = r

    @typesafe
    def distance(self, p):
        """Calculates the distance to a Point p.

        :type p: sphinx_typesafe.tests.geometry.Point
        :rtype:  float
        """
        return super(Circle,self).distance(p) - self.r

    @typesafe({ 'return': 'float' })
    def area(self):
        '''Returns the area of a Circle.
        '''
        import math
        return math.pi * math.pow(self.r, 2)


def function_main():
    from sphinx_typesafe.tests.geometry import Circle
    from sphinx_typesafe.tests.geometry import Point
    c = Circle(-2.0, -1.0, 5.0)
    p = Point( 1.0,  4.0)
    print(c.area())
    print(c.distance(p))


if __name__ == "__main__":
    function_main()
