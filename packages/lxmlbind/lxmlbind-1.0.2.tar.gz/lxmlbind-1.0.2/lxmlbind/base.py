"""
Declarative object base class.
"""
from functools import partial
from inspect import getmro
from itertools import imap
from logging import getLogger

from lxml import etree

from lxmlbind.property import Property, set_child
from lxmlbind.search import search


class Base(object):
    """
    Base class for objects using LXML object binding.
    """
    def __init__(self, element=None, parent=None, **kwargs):
        """
        :param element: an optional root `lxml.etree` element
        :param parent: an optional parent pointer to another instance of `Base`
        """
        self._parent = parent
        self._init_element(element)
        self._init_properties(**kwargs)

    def _init_element(self, element):
        if element is None:
            self._element = self._create_element(self.__class__.tag())
        elif element.tag == self.__class__.tag():
            self._element = element
        else:
            raise Exception("'{}' object requires tag '{}', not '{}'".format(self.__class__,
                                                                             self.__class__.tag(),
                                                                             element.tag))

    def _create_element(self, tag):
        """
        Generate a new element for this object.

        Subclasses may override this function to provide more complex default behavior.
        """
        return etree.Element(tag, self.__class__.attributes())

    def _init_properties(self, **kwargs):
        """
        Initialize property names and default values.
        """
        for class_ in getmro(self.__class__):
            for name, member in class_.__dict__.iteritems():
                if not isinstance(member, Property):
                    continue
                if member.path is None:
                    member.path = name
                if not member.auto and name not in kwargs:
                    continue
                if member.__get__(self, self.__class__) is None:
                    member.__set__(self, kwargs.get(name, member.default))

    @classmethod
    def tag(cls):
        """
        Defines the expected tag of the root element of objects of this class.

        The default behavior is to use the class name with a leading lower case.

        For PEP8 compatible class names, this gives a lowerCamelCase name.
        """
        return cls.__name__[0].lower() + cls.__name__[1:]

    @classmethod
    def attributes(cls):
        """
        Defines attributes for the root element of objects of this class.
        """
        return {}

    def to_xml(self, pretty_print=False):
        """
        Encode as XML string.
        """
        return etree.tostring(self._element, pretty_print=pretty_print)

    @classmethod
    def from_xml(cls, xml):
        """
        Decode from an XML string.
        """
        return cls(etree.XML(bytes(xml)))

    def search(self, property_, create=False):
        """
        Search for property with instance.

        :param create: whether the property's elements be created if absent
        """
        return search(self, property_, create)

    def __str__(self):
        """
        Return XML string.
        """
        return self.to_xml()

    def __hash__(self):
        """
        Hash using XML element.
        """
        return self._element.__hash__()

    def __eq__(self, other):
        """
        Compare using XML element equality, ignoring whitespace differences.
        """
        if other is None:
            return False
        return eq_xml(self._element, other._element)

    def __ne__(self, other):
        """
        Compare using XML element equality, ignoring whitespace differences.
        """
        return not self.__eq__(other)

    @classmethod
    def property(cls, path=None, default=None, auto=True, filter_func=None, **kwargs):
        """
        Generate a property that matches this class.
        """
        return Property(cls.tag() if path is None else path,
                        get_func=cls,
                        set_func=set_child,
                        attributes_func=lambda instance: cls.attributes(),
                        filter_func=filter_func,
                        auto=auto,
                        default=default,
                        **kwargs)


class List(Base):
    """
    Extension that supports treating elements as list of other types.

    Attempts to maintainer _parent references.
    """
    @classmethod
    def of(cls):
        """
        Defines what this class is a list of.

        :returns: a function that operates on `lxml.etree` elements, returning instances of `Base`.
        """
        return Base

    def _of(self):
        return partial(self.of(), parent=self)

    def append(self, value):
        self._element.append(value._element)
        value._parent = self

    def __getitem__(self, key):
        item = self._of()(self._element.__getitem__(key))
        return item

    def __setitem__(self, key, value):
        self._element.__setitem__(key, value._element)
        value._parent = self

    def __delitem__(self, key):
        # Without keeping a parallel list of Base instances, it's not
        # possible to detach the _parent pointer of values added via
        # append() or __setitem__. So far, not keeping a parallel list
        # is worth it.
        self._element.__delitem__(key)

    def __iter__(self):
        return imap(self._of(), self._element.__iter__())

    def __len__(self):
        return len(self._element)


def tag(name):
    """
    Class decorator that replaces `Base.tag()` with a function that returns `name`.
    """
    def wrapper(cls):
        if not issubclass(cls, Base):
            raise Exception("lxmlbind.base.tag decorator should only be used with subclasses of lxmlbind.base.Base")

        @classmethod
        def tag(cls):
            return name

        cls.tag = tag
        return cls
    return wrapper


def attributes(**kwargs):
    """
    Class decorator that replaces `Base.attributes()` with a function that returns `kwargs`.
    """
    def wrapper(cls):
        if not issubclass(cls, Base):
            raise Exception("lxmlbind.base.attributes decorator should only be used with subclasses of lxmlbind.base.Base")  # noqa

        @classmethod
        def attributes(cls):
            return kwargs

        cls.attributes = attributes
        return cls
    return wrapper


def of(child_type):
    """
    Class decorator that replaces `List.of()` with a function that returns `child_type`.
    """
    def wrapper(cls):
        if not issubclass(cls, Base):
            raise Exception("lxmlbind.base.of decorator should only be used with subclasses of lxmlbind.base.Base")

        @classmethod
        def of(cls):
            return child_type

        cls.of = of
        return cls
    return wrapper


def eq_xml(this,
           that,
           ignore_attributes=None,
           ignore_whitespace=True,
           logger=getLogger("lxmlbind.base")):
    """
    XML comparison on `lxml.etree` elements.

    :param this: an `lxml.etree` element
    :param that: an `lxml.etree` element
    :param ignore_attributes: an optional list of attributes to ignore
    :param ignore_whitespace: whether whitespace should matter
    """
    ignore_attributes = ignore_attributes or []

    # compare tags
    if this.tag != that.tag:
        if logger is not None:
            logger.debug("Element tags do not match: {} != {}".format(this.tag, that.tag))
        return False

    # compare attributes
    def _get_attributes(attributes):
        return {key: value for key, value in attributes.iteritems() if key not in ignore_attributes}

    these_attributes = _get_attributes(this.attrib)
    those_attributes = _get_attributes(that.attrib)
    if these_attributes != those_attributes:
        if logger is not None:
            logger.debug("Element attributes do not match: {} != {}".format(these_attributes,
                                                                            those_attributes))
        return False

    # compare text
    def _strip(tail):
        if tail is None:
            return None
        return tail.strip() or None

    this_text = _strip(this.text) if ignore_whitespace else this.text
    that_text = _strip(that.text) if ignore_whitespace else that.text

    if this_text != that_text:
        if logger is not None:
            logger.debug("Element text does not match: {} != {}".format(this_text,
                                                                        that_text))
        return False

    this_tail = _strip(this.tail) if ignore_whitespace else this.tail
    that_tail = _strip(that.tail) if ignore_whitespace else that.tail

    if this_tail != that_tail:
        if logger is not None:
            logger.debug("Element tails do not match: {} != {}".format(this_tail,
                                                                       that_tail))
        return False

    # evaluate children
    these_children = sorted(this.getchildren(), key=lambda element: element.tag)
    those_children = sorted(that.getchildren(), key=lambda element: element.tag)
    if len(these_children) != len(those_children):
        if logger is not None:
            logger.debug("Element children length does not match: {} != {}".format(len(these_children),
                                                                                   len(those_children)))
        return False

    # recurse
    for this_child, that_child in zip(these_children, those_children):
        if not eq_xml(this_child, that_child, ignore_attributes, ignore_whitespace):
            return False
    else:
        return True
