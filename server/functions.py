class Functions:
    """
    Privileged functions inside our server
    """

    @staticmethod
    def square_root(value):
        """
        Method that performs a square root of a given number

        :param value: Value on which the square root will be calculated
        :return: Square root of the passed value
        """

        return value**(1/2.0)

    @staticmethod
    def cubic_root(value):
        """
        Method that performs a cubic root of a given number

        :param value: Value on which the cubic root will be calculated
        :return: Cubic root of the passed value
        """

        return value**(1/3.0)

    @staticmethod
    def n_root(value, n):
        """
        Method that performs a n root of a given number

        :param value: Value on which the n root will be calculated
        :param n: root that will be calculated
        :return: N root of the passed value
        """
        return value**(1/float(n))
