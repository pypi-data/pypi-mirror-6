# encoding: utf-8
import shutil
import tempfile

import unittest
from pdefc.lang.packages import Package
from pdef_objc import ObjectiveCGenerator, _ObjectiveCFilters
from pdefc.generators import PrefixMapper
from pdefc.lang import *


class TestObjectiveCGenerator(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.generator = ObjectiveCGenerator(self.tempdir)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_generate_enum(self):
        enum = Enum('Number', value_names=['ONE', 'TWO'])
        module = Module('test.module')
        module.add_definition(enum)
        module.link()

        header = self.generator._generate_header(enum)
        impl = self.generator._generate_impl(enum)
        assert header
        assert impl

    def test_generate_message(self):
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

        header = self.generator._generate_header(msg)
        impl = self.generator._generate_impl(msg)
        assert header
        assert impl

    def test_generate_interface(self):
        exc = Message('Exception', is_exception=True)

        iface = Interface('Interface', exc=exc)
        iface.create_method('method0', NativeType.INT32, [('arg', NativeType.INT32)])
        iface.create_method('method1', NativeType.STRING, [('name', NativeType.STRING)])

        module = Module('test.module')
        module.add_definition(exc)
        module.add_definition(iface)
        module.link()

        header = self.generator._generate_header(iface)
        impl = self.generator._generate_impl(iface)
        assert header
        assert impl

    def test_generate_package(self):
        msg = Message('Message')
        iface = Interface('Interface')
        module0 = Module('module0', definitions=[msg])
        module1 = Module('module1', definitions=[iface])

        package = Package('test', modules=[module0, module1])
        package.compile()

        code = self.generator._generate_package(package)
        assert code


class TestObjectiveCFilters(unittest.TestCase):
    def setUp(self):
        self.filters = _ObjectiveCFilters(PrefixMapper())

    def test_list(self):
        list0 = List(NativeType.INT32)
        type0 = self.filters.objc_type(list0)
        descriptor = self.filters.objc_descriptor(list0)

        assert type0 == 'NSArray *'
        assert descriptor == '[PDDescriptors listWithElement:[PDDescriptors int32]]'

    def test_set(self):
        set0 = Set(NativeType.BOOL)
        type0 = self.filters.objc_type(set0)
        descriptor = self.filters.objc_descriptor(set0)

        assert type0 == 'NSSet *'
        assert descriptor == '[PDDescriptors setWithElement:[PDDescriptors bool0]]'

    def test_map(self):
        map0 = Map(NativeType.STRING, NativeType.FLOAT)
        type0 = self.filters.objc_type(map0)
        descriptor = self.filters.objc_descriptor(map0)

        assert type0 == 'NSDictionary *'
        assert descriptor == '[PDDescriptors mapWithKey:[PDDescriptors string] ' \
                             'value:[PDDescriptors float0]]'

    def test_enum(self):
        enum = Enum('Number')

        module = Module('test.module', definitions=[enum])
        module.link()

        type0 = self.filters.objc_type(enum)
        descriptor0 = self.filters.objc_descriptor(enum)
        assert type0 == 'Number '
        assert descriptor0 == 'NumberDescriptor()'

    def test_enum_value(self):
        enum = Enum('Number')
        one = enum.create_value('ONE')

        module = Module('test.module', definitions=[enum])
        module.link()

        type0 = self.filters.objc_type(one)
        assert type0 == 'Number_ONE '

    def test_message(self):
        msg = Message('Message')

        type0 = self.filters.objc_type(msg)
        descriptor = self.filters.objc_descriptor(msg)
        assert type0 == 'Message *'
        assert descriptor == '[Message typeDescriptor]'

    def test_message_with_prefix(self):
        self.filters.prefix_mapper = PrefixMapper([('test', 'T')])

        msg = Message('Message')
        module = Module('test.module', definitions=[msg])
        module.link()

        type0 = self.filters.objc_type(msg)
        descriptor = self.filters.objc_descriptor(msg)

        assert type0 == 'TMessage *'
        assert descriptor == '[TMessage typeDescriptor]'

    def test_interface(self):
        iface = Interface('Interface')

        module = Module('test.module', definitions=[iface])
        module.link()

        type0 = self.filters.objc_type(iface)
        descriptor = self.filters.objc_descriptor(iface)

        assert type0 == 'id<Interface> '
        assert descriptor == 'InterfaceDescriptor()'
