# encoding: utf-8
from __future__ import unicode_literals

import unittest
from pdef_java import JavaGenerator, _JavaFilters, JAVA_NATIVE_REFS
from pdefc.generators import ModuleMapper, PrefixMapper
from pdefc.lang import *


class TestJavaGenerator(unittest.TestCase):
    def test_render_enum(self):
        enum = Enum('Number', value_names=['ONE', 'TWO'])
        module = Module('test.module')
        module.add_definition(enum)
        module.link()

        generator = JavaGenerator('/dev/null')
        code = generator._render(enum)
        assert code

    def test_render_message(self):
        enum = Enum('Type')
        subtype = enum.create_value('SUBTYPE')

        base = Message('Base')
        base.create_field('type', enum, is_discriminator=True)

        msg = Message('Message', base=base, discriminator_value=subtype)
        msg.create_field('field', NativeType.BOOL)

        module = Module('test.module')
        module.add_definition(enum)
        module.add_definition(base)
        module.add_definition(msg)
        module.link()

        generator = JavaGenerator('/dev/null')
        code = generator._render(msg)
        assert code

    def test_render_interface(self):
        exc = Message('Exception', is_exception=True)

        iface = Interface('Interface', exc=exc)
        iface.create_method('method0', NativeType.INT32, [('arg', NativeType.INT32)])
        iface.create_method('method1', NativeType.STRING, [('name', NativeType.STRING)])

        module = Module('test.module')
        module.add_definition(exc)
        module.add_definition(iface)
        module.link()

        generator = JavaGenerator('/dev/null')
        code = generator._render(iface)
        assert code


class TestJavaFilters(unittest.TestCase):
    def setUp(self):
        self.filters = _JavaFilters(ModuleMapper(), PrefixMapper())

    def test_jname(self):
        self.filters.prefix_mapper = PrefixMapper([('namespace', 'Ns')])
        module = Module('module', namespace='namespace')
        msg = Message('Message')
        msg.module = module

        name = self.filters.jname(msg)
        assert name == 'NsMessage'

    def test_jpackage(self):
        self.filters.module_mapper = ModuleMapper([('service', 'com.company.service')])
        module = Module('service.client.tests')
        ref = self.filters.jpackage(module)

        assert ref == 'com.company.service.client.tests'

    def test_jref__native(self):
        for ntype in NativeType.all():
            ref = self.filters.jref(ntype)
            assert ref is JAVA_NATIVE_REFS[ntype.type]

    def test_jref__with_package(self):
        msg = Message('Message')

        module = Module('test.module', definitions=[msg])
        module.link()
        self.filters.module_mapper = ModuleMapper([('test', 'com.company.test')])

        ref = self.filters.jref(msg)
        assert ref.name == 'com.company.test.module.Message'
        assert ref.descriptor == 'com.company.test.module.Message.DESCRIPTOR'
        assert ref.default == 'new com.company.test.module.Message()'

    def test_jlist(self):
        list0 = List(NativeType.INT32)
        ref = self.filters.jref(list0)

        assert ref.name == 'java.util.List<Integer>'
        assert ref.default == 'new java.util.ArrayList<Integer>()'
        assert ref.descriptor == 'io.pdef.descriptors.Descriptors.list(' \
                                 'io.pdef.descriptors.Descriptors.int32)'

    def test_jset(self):
        set0 = Set(NativeType.BOOL)
        ref = self.filters.jref(set0)

        assert ref.name == 'java.util.Set<Boolean>'
        assert ref.default == 'new java.util.HashSet<Boolean>()'
        assert ref.descriptor == 'io.pdef.descriptors.Descriptors.set(' \
                                 'io.pdef.descriptors.Descriptors.bool)'

    def test_jmap(self):
        map0 = Map(NativeType.STRING, NativeType.FLOAT)
        ref = self.filters.jref(map0)

        assert ref.name == 'java.util.Map<String, Float>'
        assert ref.default == 'new java.util.HashMap<String, Float>()'
        assert ref.descriptor == 'io.pdef.descriptors.Descriptors.map(' \
                                 'io.pdef.descriptors.Descriptors.string, ' \
                                 'io.pdef.descriptors.Descriptors.float0)'

    def test_jenum(self):
        enum = Enum('Number')

        module = Module('test.module', definitions=[enum])
        module.link()

        ref = self.filters.jref(enum)
        assert ref.name == 'test.module.Number'
        assert ref.descriptor == 'test.module.Number.DESCRIPTOR'

    def test_jenum_value(self):
        enum = Enum('Number')
        one = enum.create_value('ONE')

        module = Module('test.module', definitions=[enum])
        module.link()

        ref = self.filters.jref(one)
        assert ref.name == 'test.module.Number.ONE'
        assert ref.descriptor is None

    def test_jmessage(self):
        msg = Message('Message')

        module = Module('test.module', definitions=[msg])
        module.link()

        ref = self.filters.jref(msg)
        assert ref.name == 'test.module.Message'
        assert ref.default == 'new test.module.Message()'
        assert ref.descriptor == 'test.module.Message.DESCRIPTOR'

    def test_jmessage__with_prefix(self):
        msg = Message('Message')

        module = Module('test', definitions=[msg])
        module.link()

        self.filters.prefix_mapper = PrefixMapper([('test', 'Test')])
        ref = self.filters.jref(msg)
        assert ref.name == 'test.TestMessage'
        assert ref.default == 'new test.TestMessage()'
        assert ref.descriptor == 'test.TestMessage.DESCRIPTOR'

    def test_jinterface(self):
        iface = Interface('Interface')

        module = Module('test.module', definitions=[iface])
        module.link()

        ref = self.filters.jref(iface)
        assert ref.name == 'test.module.Interface'
        assert ref.descriptor == 'test.module.Interface.DESCRIPTOR'
        assert ref.default == 'null'
