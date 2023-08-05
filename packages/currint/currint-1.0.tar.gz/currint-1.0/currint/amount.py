from decimal import Decimal, ROUND_HALF_UP


class Amount(object):
    """
    An amount of a currency.
    """

    def __init__(self, currency, value):
        """
        Initialises the Amount with a Currency object and an
        integer value of its minor unit (i.e. cents for USD)
        """
        assert isinstance(value, (int, long))
        assert not isinstance(currency, basestring)
        self.currency = currency
        self.value = value

    def __str__(self):
        return unicode(self).encode("utf8")

    def __unicode__(self):
        return self.currency.format(self.value)

    def __repr__(self):
        return "<Amount %s, %s>" % (self.currency, self.value)

    def __eq__(self, other):
        return (self.currency == other.currency) and (self.value == other.value)

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("You cannot add amounts of different currencies (%s and %s)" % (self.currency, other.currency))
        return Amount(self.currency, self.value + other.value)

    def __sub__(self, other):
        if self.currency != other.currency:
            raise ValueError("You cannot subtract amounts of different currencies (%s and %s)" % (self.currency, other.currency))
        return Amount(self.currency, self.value - other.value)

    def apply_factor(self, other):
        if not isinstance(other, (int, long, Decimal)):
            raise ValueError("You can only apply an integer, long or Decimal factor to an Amount")
        return Amount(
            self.currency,
            int(Decimal(self.value * other).to_integral(ROUND_HALF_UP)),
        )
