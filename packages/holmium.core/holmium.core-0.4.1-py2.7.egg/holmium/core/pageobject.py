import inspect
import weakref
import types
import threading
import contextlib
import collections
from functools import wraps

import selenium.webdriver.common.by
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoSuchFrameException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.remote.webelement import WebElement
from ordereddict import OrderedDict

import holmium

from holmium.core.facets import Faceted, ElementFacet


class Locators(selenium.webdriver.common.by.By):
    """
    proxy class to access locator types
    """
    pass


def enhanced(web_element):
    """
    incase a higher level abstraction for a WebElement is available
    we will use that in Pages. (e.g. a select element is converted into
    :class:`selenium.webdriver.support.ui.Select`)
    """
    abstraction_mapping = {'select': Select}
    if web_element.tag_name in abstraction_mapping.keys():
        return abstraction_mapping[web_element.tag_name](web_element)
    return web_element


class ElementList(list):
    """
    proxy to a standard list which would be stored in
    a :class:`holmium.core.Page`.
    """

    def __init__(self, instance, *args, **kwargs):
        self.instance = weakref.ref(instance)
        list.__init__(self, *args, **kwargs)

    def __getitem__(self, index):
        return list.__getitem__(self, index).__get__(self.instance(),
                                                     self.instance().__class__)


class ElementDict(dict):
    """
    proxy to a standard dict which would be stored in
    a :class:`holmium.core.Page`.
    """

    def __init__(self, instance, *args, **kwargs):
        self.instance = weakref.ref(instance)
        dict.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        return dict.__getitem__(self, key).__get__(self.instance(),
                                                   self.instance().__class__)

class Registry(type):
    """
    simple meta class to keep track of all page objects registered
    """
    pages = {}
    def __new__(cls, *args, **kwargs):
        page = super(Registry, cls).__new__(cls, *args, **kwargs)
        Registry.pages[args[0]] = page
        return page



class Page(Faceted):
    """
    Base class for all page objects to extend from.
    void Instance methods implemented by subclasses are provisioned
    with fluent wrappers to facilitate with writing code such as::

        class Google(Page):
            def enter_query(self):
                ....

            def submit_search(self):
                ....

            def get_results(self):
                ....

        assert len(Google().enter_query("page objects").submit_search().get_results()) > 0

    """
    __metaclass__ = Registry
    local = threading.local()

    def __init__(self, driver, url=None, iframe=None):
        super(Page, self).__init__()
        self.driver = driver
        self.touched = False
        self.initialized = False
        if url:
            self.home = url
        elif driver.current_url:
            self.home = driver.current_url
        else:
            self.home = None

        self.iframe = iframe
        for el in inspect.getmembers(self.__class__):
            def update_element(el, name):
                if issubclass(el.__class__, ElementGetter):
                    el.iframe = self.iframe
                    if el.is_facet:
                        facet = ElementFacet(el, name, debug=el.is_debug_facet)
                        facet.register(self)

            if issubclass(el[1].__class__, list):
                for item in el[1]:
                    update_element(item, el[0])
                self.__setattr__(el[0], ElementList(self, el[1]))
            elif issubclass(el[1].__class__, dict):
                for item in el[1].values():
                    update_element(item, el[0])
                self.__setattr__(el[0], ElementDict(self, el[1]))
            else:
                update_element(el[1], el[0])

        if url:
            self.driver.get(url)
        self.initialized = True

    @contextlib.contextmanager
    def scope(self):
        Page.local.driver = object.__getattribute__(self, "driver")
        yield

    @staticmethod
    def get_driver():
        return Page.local.driver

    def go_home(self):
        """
        returns the page object to the url it was initialized with
        """
        self.driver.get(self.home)

    def __getattribute__(self, key):
        """
        to enable fluent access to page objects, instance methods that
        don't return a value, instead return the page object instance.
        """

        attr_getter = lambda key: object.__getattribute__(self, key)
        attr_setter = lambda key, value: object.__setattr__(self, key, value)

        with attr_getter("scope")():
            if not attr_getter("touched") and attr_getter("initialized"):
                driver = attr_getter("driver")
                attr_getter("evaluate")()
                attr_setter("touched", True)
            attr = attr_getter(key)
            # check if home url is set, else update.
            if not attr_getter("home"):
                holmium.core.log.debug(
                    "home url not set, attempting to update.")
                attr_setter("home", attr_getter("driver").current_url)

            if isinstance(attr, types.MethodType):
                @wraps(attr)
                def wrap(*args, **kwargs):
                    resp = attr(*args, **kwargs)
                    if None == resp:
                        holmium.core.log.debug(
                            "method %s returned None, using fluent response" % attr.func_name)
                        resp = self
                    return resp

                return wrap
            return attr



class ElementGetter(object):
    """
    internal class to encapsulate the logic used by
    :class:`holmium.core.Element`
    & :class:`holmium.core.Elements`
    """

    def __init__(self, locator_type,
                 query_string,
                 base_element=None,
                 timeout=1,
                 value=lambda el: el,
                 facet=False):
        """
        :param holmium.core.Locators locator_type: selenium locator to use when locating the element
        :param str query_string: the value to pass to the locator
        :param holmium.core.Element base_element: a reference to another element under which to locate this element.
        :param int timeout: time to implicitely wait for the element
        :param lambda value: transform function for the value of the element.
         The located :class:`selenium.webdriver.remote.webelement.WebElement` instance is passed as the only argument to the function.
        :param bool facet: flag to  treat this element as a facet.
        """
        self.query_string = query_string
        self.locator_type = locator_type
        self.timeout = timeout
        self.driver = None
        self.iframe = None
        self.base_element = base_element
        self.value_mapper = value
        self.root_fn = lambda: Page.get_driver()
        holmium.core.log.debug("locator:%s, query_string:%s, timeout:%d" %
                               (locator_type, query_string, timeout))
        self.is_facet = facet
        self.is_debug_facet = False

    @property
    def root(self):
        return self.root_fn()

    @root.setter
    def root(self, root_fn):
        self.root_fn = root_fn

    def get_element(self, method=None):

        if self.base_element:
            if isinstance(self.base_element, types.LambdaType):
                el = self.base_element()
                _meth = getattr(el, method.im_func.func_name)
            elif isinstance(self.base_element, Element):
                _meth = getattr(self.base_element.__get__(self, self.__class__),
                                method.im_func.func_name)
            elif isinstance(self.base_element, WebElement):
                _meth = getattr(self.base_element, "find_element")
            else:
                raise TypeError("invalid base_element type (%s) used" % (
                    type(self.base_element)))
        else:
            _meth = method
        holmium.core.log.debug(
            "looking up locator:%s, query_string:%s, timeout:%d" %
            (self.locator_type, self.query_string, self.timeout))

        if self.iframe:
            Page.local.driver.switch_to_default_content()
            Page.local.driver.switch_to_frame(self.iframe)

        if self.timeout:
            try:
                WebDriverWait(self.root, self.timeout).until(
                    lambda _: _meth(self.locator_type, self.query_string))
            except TimeoutException:
                holmium.core.log.debug(
                    "unable to find element %s after waiting for %d seconds" % (
                        self.query_string, self.timeout))
        return _meth(self.locator_type, self.query_string)


class Element(ElementGetter):
    """
    Utility class to get a :class:`selenium.webdriver.remote.webelement.WebElement`
    by querying via one of :class:`holmium.core.Locators`

    :param holmium.core.Locators locator_type: selenium locator to use when locating the element
    :param str query_string: the value to pass to the locator
    :param holmium.core.Element base_element: a reference to another element under which to locate this element.
    :param int timeout: time to implicitely wait for the element
    :param lambda value: transform function for the value of the element.
     The located :class:`selenium.webdriver.remote.webelement.WebElement` instance is passed as the only argument to the function.
    :param bool facet: flag to  treat this element as a facet.
    """

    def __get__(self, instance, owner):
        if not instance:
            return self
        try:
            return self.value_mapper(
                enhanced(self.get_element(self.root.find_element))
            ) if self.root else None
        except NoSuchElementException:
            return None


class Elements(ElementGetter):
    """
    Utility class to get a collection of :class:`selenium.webdriver.remote.webelement.WebElement`
    objects by querying via one of :class:`holmium.core.Locators`

    :param holmium.core.Locators locator_type: selenium locator to use when locating the element
    :param str query_string: the value to pass to the locator
    :param holmium.core.Element base_element: a reference to another element under which to locate this element.
    :param int timeout: time to implicitely wait for the element
    :param lambda value: transform function for each element in the collection.
     The located :class:`selenium.webdriver.remote.webelement.WebElement` instance is passed as the only argument to the function.
    :param bool facet: flag to  treat this element as a facet.
    """

    def __getitem__(self, idx):
        return lambda: self.__get__(self, self.__class__)[idx]

    def __get__(self, instance, owner):
        if not instance:
            return self
        return [self.value_mapper(enhanced(el)) for el in
                self.get_element(self.root.find_elements)] if self.root else []


class ElementMap(Elements):
    """
    Used to create dynamic dictionaries based on an element locator specified by one of
    :class:`holmium.core.Locators`.

    The wrapped dictionary is an :class:`collections.OrderedDict` instance.

    :param holmium.core.Locators locator_type: selenium locator to use when locating the element
    :param str query_string: the value to pass to the locator
    :param holmium.core.Element base_element: a reference to another element under which to locate this element.
    :param int timeout: time to implicitely wait for the element
    :param bool facet: flag to  treat this element as a facet.
    :param lambda key: transform function for mapping a key to a WebElement in the collection.
     The located :class:`selenium.webdriver.remote.webelement.WebElement` instance is passed as the only argument to the function.
    :param lambda value: transform function for the value when accessed via the key.
     The located :class:`selenium.webdriver.remote.webelement.WebElement` instance is passed as the only argument to the function.
    """

    def __init__(self, locator_type,
                 query_string=None,
                 base_element=None,
                 timeout=1,
                 key=lambda el: el.text,
                 value=lambda el: el,
                 facet=False):
        super(ElementMap, self).__init__(locator_type, query_string,
                                         base_element,
                                         timeout, facet)
        self.key_mapper = key
        self.value_mapper = value

    def __get__(self, instance, owner):
        if not instance:
            return self
        return OrderedDict(
            (self.key_mapper(el), self.value_mapper(enhanced(el))) for el in
            self.get_element(self.root.find_elements)) if self.root else {}


    def __getitem__(self, key):
        return lambda: self.__get__(self, self.__class__)[key]


class Section(Faceted):
    """
    Base class to encapsulate reusable page sections::

        class MySection(Section):
            things = Elements( .... )

        class MyPage(Page):
            section_1 =  MySection(Locators.CLASS_NAME, "section")
            section_2 =  MySection(Locators.ID, "unique_section")

    """

    def __init__(self, locator_type, query_string, iframe=None):

        super(Section, self).__init__()
        self.touched = False
        self.locator_type = locator_type
        self.query_string = query_string
        self.iframe = iframe
        self.__root_val = None
        self.element_members = {}
        for element in inspect.getmembers(self.__class__):
            if issubclass(element[1].__class__, ElementGetter):
                self.element_members[element[0]] = element[1]
                if element[1].is_facet:
                    facet = ElementFacet(element[1], element[0], debug=element[1].is_debug_facet)
                    facet.register(self)

    def __get__(self, instance, owner):
        for element in self.element_members.values():
            element.root = lambda: self.root
        return self

    def __getattribute__(self, item):
        attr_getter = lambda key: super(Section, self).__getattribute__(key)
        attr_setter = lambda key, value: super(Section, self).__setattr__(key,
                                                                          value)
        members = attr_getter("element_members")
        touched = attr_getter("touched")
        if not touched and item in members:
            attr_getter("evaluate")()
            attr_setter("touched", True)
        return attr_getter(item)


    @property
    def root(self):
        if self.iframe:
            try:
                Page.get_driver().switch_to_default_content()
                Page.get_driver().switch_to_frame(self.iframe)
            except NoSuchFrameException:
                holmium.core.log.error(
                    "unable to switch to iframe %s" % self.iframe)
        try:
            return self.__root_val or Page.get_driver().find_element(
                self.locator_type, self.query_string
            )
        except NoSuchElementException:
            return None

    @root.setter
    def root(self, val):
        self.__root_val = val


class Sections(Section, collections.Sequence):
    """
    Base class for an Iterable view of a collection of :class:`holmium.core.Section`
    objects.
    """

    def __init__(self, locator_type, query_string, iframe=None, timeout=0):
        super(Sections, self).__init__(locator_type, query_string, iframe)
        self.timeout = timeout

    def __getelements__(self):
        if self.timeout:
            try:
                WebDriverWait(Page.get_driver(), self.timeout).until(
                    lambda _: Page.get_driver().find_elements(self.locator_type, self.query_string))
            except TimeoutException:
                holmium.core.log.debug(
                    "unable to find element %s after waiting for %d seconds" % (
                        self.query_string, self.timeout))
        return Page.get_driver().find_elements(self.locator_type,
                                               self.query_string)

    def __iter__(self):
        for element in self.__getelements__():
            self.root = element
            yield self

    def __len__(self):
        return len(self.__getelements__())

    def __getitem__(self, idx):
        _idx = 0
        for item in self:
            if idx == _idx:
                break
            _idx += 1
            if idx > _idx:
                raise IndexError("Sections index (%d) out of range" % idx)
        if len(self) == 0:
            raise IndexError("Sections index (%d) out of range" % idx)
        return self
