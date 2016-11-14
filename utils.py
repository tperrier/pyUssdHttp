def not_iterable(obj):
    """ Return True if obj is a string or non iterable"""
    return hasattr(obj,"rstrip") or not (hasattr(obj,"__getitem__") or hasattr(obj,"__iter__"))

# From: http://stackoverflow.com/a/32536493/2708328
class abstract_attribute(object):
    def __get__(self, obj, type):
        # Now we will iterate over the names on the class,
        # and all its superclasses, and try to find the attribute
        # name for this descriptor
        # traverse the parents in the method resolution order
        for cls in type.__mro__:
            # for each cls thus, see what attributes they set
            for name, value in cls.__dict__.items():
                # we found ourselves here
                if value is self:
                    # if the property gets accessed as Child.variable,
                    # obj will be done. For this case
                    # If accessed as a_child.variable, the class Child is
                    # in the type, and a_child in the obj.
                    this_obj = obj if obj else type

                    raise NotImplementedError(
                         "%r does not have the attribute %r "
                         "(abstract from class %r)" %
                             (this_obj, name, cls.__name__))

        # we did not find a match, should be rare, but prepare for it
        raise NotImplementedError(
            "%s does not set the abstract attribute <unknown>", type.__name__)
