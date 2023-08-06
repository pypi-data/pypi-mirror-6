__author__ = 'oakfang'


def mixout(*mixins):
    """
    Create a mixin from a bunch of other mixins.
    """
    return type('CainMixin', mixins)