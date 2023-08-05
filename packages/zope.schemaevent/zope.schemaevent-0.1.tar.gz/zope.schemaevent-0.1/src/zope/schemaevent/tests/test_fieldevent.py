# -*- coding: utf-8 -*-
import unittest2
from zope import interface
from zope import component
from zope import schema
from zope.schemaevent.testing import ZC_LAYER


class FieldEventNotify(unittest2.TestCase):
    layer = ZC_LAYER

    def _makeOne(self, field=None, name=None):
        from zope.schema import Text
        if field is None:
            field = Text(__name__='testing')
        if name is None:
            return self._getTargetClass()(field)
        return self._getTargetClass()(field, name)

    def _getTargetClass(self):
        from zope.schema.fieldproperty import FieldProperty
        return FieldProperty

    def test_subscriber(self):
        from zope.schema import Text
        from zope.schema._compat import u
        field = Text(
            __name__='testing',
            description=u('DESCRIPTION'),
            default=u('DEFAULT'),
            required=True,
        )
        prop = self._makeOne(field=field)

        class Foo(object):
            testing = prop
        foo = Foo()

        logs = []

        @component.adapter(schema.interfaces.IFieldUpdatedEvent)
        def add_field_event(event):
            logs.append(event)

        component.provideHandler(add_field_event)

        self.assertEqual(len(logs), 0)
        foo.testing = u'Bla'
        self.assertEqual(len(logs), 1)
        event = logs[0]
        self.assertEqual(event.field, field)
        self.assertEqual(event.inst, foo)

    def test_filtered_handler(self):
        from zope.schema import Text
        from zope.schema._compat import u
        field = Text(
            __name__='testing',
            description=u('DESCRIPTION'),
            default=u('DEFAULT'),
            required=True,
        )
        prop = self._makeOne(field=field)

        class IFoo(interface.Interface):
            """
            """

        class Foo(object):
            interface.implements(IFoo)
            testing = prop
        foo = Foo()

        logs = []

        @component.adapter(IFoo, schema.Text, schema.interfaces.IFieldUpdatedEvent)
        def add_field_events(obj, field, event):
            logs.append((obj, field, event))

        component.provideHandler(add_field_events)

        self.assertEqual(len(logs), 0)
        foo.testing = u'Bla'
        self.assertEqual(len(logs), 1)
        event_inst, event_field, event = logs[0]
        self.assertEqual(event_inst, foo)
        self.assertEqual(event_field, field)
