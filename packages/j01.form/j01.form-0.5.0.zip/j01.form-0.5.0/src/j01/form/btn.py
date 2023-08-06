###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH
# All Rights Reserved.
#
###############################################################################
"""Buttons
$Id: btn.py 3942 2014-03-24 08:59:21Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys

import zope.schema
import zope.interface
import zope.component
import zope.location
import zope.interface.adapter

from zope.schema.fieldproperty import FieldProperty

import z3c.form.interfaces
import z3c.form.button
import z3c.form.action
import z3c.form.widget
import z3c.form.util
import z3c.form.browser.widget

import j01.jsonrpc.jsform
import j01.jsonrpc.jsbutton

from j01.form import layer
from j01.form import interfaces

try:
    unicode
except NameError:
    # Py3: Define unicode.
    unicode = str


###############################################################################
#
# decorators

def handler(btnOrName):
    """A decorator for defining a success handler."""
    if isinstance(btnOrName, basestring):
        __name__ = btnOrName
    else:
        __name__ = btnOrName.__name__
    def createHandler(func):
        handler = Handler(func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('handlers', Handlers())
        handlers.addHandler(__name__, handler)
        return handler
    return createHandler


def buttonAndHandler(btnOrTitle, *args, **kwargs):
    """Button and handler setup decorator"""
    if isinstance(btnOrTitle, basestring):
        # add the title to button constructor keyword arguments
        kwargs['title'] = btnOrTitle
        # create button and add it to the button manager
        button = Button(**kwargs)
    else:
        button = btnOrTitle
    if args:
        __name__ = args[0]
    else:
        __name__ = kwargs.get('name', button.__name__)
    for k, v in kwargs.items():
        if k == 'name':
            continue
        # apply additional attributes
        setattr(button, k, v)
    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())
    if provides:
        zope.interface.alsoProvides(button, provides)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)
    # return create handler method
    return handler(button and button or __name__)


###############################################################################
#
# action and handler concept

# IButtons
@zope.interface.implementer(interfaces.IButtons)
class Buttons(z3c.form.button.Buttons):
    """Button manager."""

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter java script code if the inputEnterActionName
        name defines a button and the button condition is True.
        """
        # find and return the form submit javascript
        btnName = getattr(form, 'inputEnterActionName', None)
        if btnName is not None:
            button = self.get(form.inputEnterActionName)
            # note button AND condition could be None
            if button is not None:
                if button.condition is None or (
                    button.condition is not None and button.condition(form)):
                    return button.getInputEnterJavaScript(form, request)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self._data.keys())


@zope.interface.implementer(interfaces.IButtonHandlers)
class Handlers(object):
    """Action Handlers for a Button-based form."""

    def __init__(self):
        # setup name, handler container
        self._data = {}

    def addHandler(self, name, handler):
        self._data[name] = handler

    def getHandler(self, name, default=None):
        return self._data.get(name, default)

    def copy(self):
        handlers = Handlers()
        for name, handler in self._data.items():
            handlers.addHandler(name, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IButtonHandlers"""
        if not isinstance(other, Handlers):
            raise NotImplementedError
        handlers = self.copy()
        for name, handler in other._data.items():
            handlers.addHandler(name, handler)
        return handlers

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return
        return handler(self.form, self.action)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self._data.keys())


@zope.interface.implementer(interfaces.IButtonHandler)
class Handler(object):
    """Handler handler."""

    def __init__(self, func):
        self.func = func

    def __call__(self, form, action):
        return self.func(form, action)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.func.__name__)


class ActionHandler(object):
    """Button handler executer.

    This adapter makes it possible to execute button handler.
    """

    zope.interface.implements(interfaces.IActionHandler)
    zope.component.adapts(
        interfaces.IForm,
        zope.interface.Interface,
        zope.interface.Interface,
        z3c.form.interfaces.IButtonAction)

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.__name__)
        if handler is None:
            return
        return handler(self.form, self.action)


###############################################################################
#
# browser request button supporting css

class Button(zope.schema.Field):
    """A button with a custom css class attribute"""

    zope.interface.implements(interfaces.IButton)

    accessKey = FieldProperty(interfaces.IButton['accessKey'])
    actionFactory = FieldProperty(interfaces.IButton['actionFactory'])
    css = FieldProperty(interfaces.IButton['css'])

    def __init__(self, *args, **kwargs):
        # Provide some shortcut ways to specify the name
        if args:
            kwargs['__name__'] = args[0]
            args = args[1:]
        if 'name' in kwargs:
            kwargs['__name__'] = kwargs['name']
            del kwargs['name']
        # apply optional css, which get added in front of other classes
        if 'css' in kwargs:
            self.css = kwargs['css']
            del kwargs['css']
        # Extract button-specific arguments
        self.accessKey = kwargs.pop('accessKey', None)
        self.condition = kwargs.pop('condition', None)
        # Initialize the button
        super(Button, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.__name__, self.title)


@zope.interface.implementer_only(interfaces.IButtonWidget)
class ButtonWidget(z3c.form.browser.widget.HTMLInputWidget,
    z3c.form.widget.Widget):
    """Button which prepends and not appends css classes
    
    This button widget also uses the css attribute defined in buttons.

    """

    klass = u'button-widget'

    def addClass(self, klass):
        """We will prepend css classes and not append like z3c.form"""
        if not self.klass:
            # just a single class
            self.klass = unicode(klass)
        else:
            # prepend and not append new classes
            classes = klass.split() + self.klass.split()
            seen = {}
            unique = []
            for item in classes:
                if item in seen:
                    continue
                seen[item]=1
                unique.append(item)
            self.klass = u' '.join(unique)

    def update(self):
        # We do not need to use the widget's update method, because it is
        # mostly about ectracting the value, which we do not need to do.
        # get all css classes
        if not self.klass:
            self.klass = ''
        classes = self.klass.split()
        if self.required and 'required' not in classes:
            # append required at the end
            classes.apend('required')
        if self.field.css:
            # make sure items are not repeated and prepend css classes
            classes = self.field.css.split() + classes
        # make sure every class is unique
        seen = {}
        unique = []
        for item in classes:
            if item in seen:
                continue
            seen[item]=1
            unique.append(item)
        self.klass = u' '.join(unique)


@zope.interface.implementer(interfaces.IButtonAction)
class ButtonAction(z3c.form.action.Action, ButtonWidget, zope.location.Location):
    """A button action specifically for JS buttons."""

    zope.component.adapts(layer.IFormLayer, interfaces.IButton)

    def __init__(self, request, field):
        z3c.form.action.Action.__init__(self, request, field.title)
        ButtonWidget.__init__(self, request)
        self.field = field

    @property
    def accesskey(self):
        return self.field.accessKey

    @property
    def value(self):
        return self.title

    @property
    def id(self):
        return self.name.replace('.', '-')

    # access css from button
    @property
    def css(self):
        return self.field.css


###############################################################################
#
# jsonrpc request buttons

# buttons
JSButton = j01.jsonrpc.jsbutton.JSButton
JSONRPCButton = j01.jsonrpc.jsbutton.JSONRPCButton
JSONRPCClickButton = j01.jsonrpc.jsbutton.JSONRPCClickButton
JSONRPCContentButton = j01.jsonrpc.jsbutton.JSONRPCContentButton

