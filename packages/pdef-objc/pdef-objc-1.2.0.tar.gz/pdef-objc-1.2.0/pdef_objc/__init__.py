# encoding: utf-8
from pdefc.lang import TypeEnum
from pdefc.generators import Generator, Templates, GeneratorCli, PrefixMapper


ENCODING = 'utf8'
HEADER_TEMPLATE = 'header.jinja2'
IMPL_TEMPLATE = 'impl.jinja2'
PACKAGE_TEMPLATE = 'package.jinja2'


class ObjectiveCGeneratorCli(GeneratorCli):
    def build_parser(self, parser):
        self._add_prefix_args(parser)

    def create_generator(self, out, args):
        prefixes = self._parse_prefix_args(args)
        return ObjectiveCGenerator(out, prefixes)


class ObjectiveCGenerator(Generator):
    '''Objective-C code generator.'''

    @classmethod
    def create_cli(cls):
        return ObjectiveCGeneratorCli()

    def __init__(self, out, prefixes=None):
        '''Create a new generator.'''
        super(ObjectiveCGenerator, self).__init__(out)

        self.prefix_mapper = PrefixMapper(prefixes)
        self.filters = _ObjectiveCFilters(self.prefix_mapper)
        self.templates = Templates(__file__, filters=self.filters)

    def generate(self, package):
        '''Generate a package source code.'''
        for module in package.modules:
            for definition in module.definitions:
                self._generate_header(definition)
                self._generate_impl(definition)

        self._generate_package(package)

    def _generate_header(self, definition):
        '''Generate a definition header file.'''
        code = self.templates.render(HEADER_TEMPLATE, definition=definition)
        filename = '%s.h' % self.filters.objc_name(definition)
        self.write_file(filename, code)
        return code

    def _generate_impl(self, definition):
        '''Generate a definition implementation file.'''
        code = self.templates.render(IMPL_TEMPLATE, definition=definition)
        filename = '%s.m' % self.filters.objc_name(definition)
        self.write_file(filename, code)
        return code

    def _generate_package(self, package):
        '''Generate a package file which groups all headers.'''
        code = self.templates.render(PACKAGE_TEMPLATE, package=package)

        names = set()
        for module in package.modules:
            for definition in module.definitions:
                names.add(self.filters.objc_name(definition).lower())

        # Generate a unique package file name.
        name = package.name
        while name in names:
            name += '_package'

        # Convert it into a CamelCase string.
        name = name.title().replace('_', '')

        # Write the package header file.
        filename = '%s.h' % name
        self.write_file(filename, code)
        return code


class _ObjectiveCFilters(object):
    '''Objective-C jinja filters.'''
    def __init__(self, prefix_mapper):
        self.prefix_mapper = prefix_mapper

    def objc_name(self, def0):
        name = def0.name
        prefix = self.prefix_mapper.get_prefix(def0.namespace) or ''
        return prefix + name

    def objc_bool(self, expression):
        return 'YES' if expression else 'NO'

    def objc_base(self, message):
        return self.objc_name(message.base) if message.base else 'PDMessage'

    def objc_isprimitive(self, type0):
        pointers = TypeEnum.COLLECTION_TYPES \
                + (TypeEnum.MESSAGE, TypeEnum.INTERFACE, TypeEnum.STRING, TypeEnum.DATETIME)
        return type0.type not in pointers

    def objc_type(self, type0):
        t = type0.type
        if t in NATIVE_TYPES:
            return NATIVE_TYPES[t]
        elif t == TypeEnum.ENUM_VALUE:
            return '%s_%s ' % (self.objc_name(type0.enum), type0.name)
        elif t == TypeEnum.ENUM:
            return '%s ' % self.objc_name(type0)
        elif t == TypeEnum.INTERFACE:
            return 'id<%s> ' % self.objc_name(type0)
        elif t == TypeEnum.MESSAGE:
            return '%s *' % self.objc_name(type0)
        raise ValueError('Unsupported type %r' % type0)

    def objc_descriptor(self, type0):
        t = type0.type
        if t in NATIVE_DESCRIPTORS:
            return NATIVE_DESCRIPTORS[t]
        elif t == TypeEnum.ENUM:
            return '%sDescriptor()' % self.objc_name(type0)
        elif t == TypeEnum.LIST:
            return '[PDDescriptors listWithElement:%s]' % self.objc_descriptor(type0.element)
        elif t == TypeEnum.SET:
            return '[PDDescriptors setWithElement:%s]' % self.objc_descriptor(type0.element)
        elif t == TypeEnum.MAP:
            return '[PDDescriptors mapWithKey:%s value:%s]' % (
                self.objc_descriptor(type0.key),
                self.objc_descriptor(type0.value))
        elif t == TypeEnum.INTERFACE:
            return '%sDescriptor()' % self.objc_name(type0)
        elif t == TypeEnum.MESSAGE:
            return '[%s typeDescriptor]' % self.objc_name(type0)
        raise ValueError('Unsupported type %r' % type0)

    def objc_default(self, type0):
        t = type0.type
        value = NATIVE_DEFAULTS.get(t)
        if value:
            return value

        if t == TypeEnum.ENUM:
            return '0'

        return 'nil'

    def objc_result(self, type0):
        if type0.is_interface:
            return 'id<%s> ' % self.objc_name(type0)
        return 'NSOperation *'


NATIVE_TYPES = {
    TypeEnum.BOOL: 'BOOL ',
    TypeEnum.INT16: 'int16_t ',
    TypeEnum.INT32: 'int32_t ',
    TypeEnum.INT64: 'int64_t ',
    TypeEnum.FLOAT: 'float ',
    TypeEnum.DOUBLE: 'double ',

    TypeEnum.STRING: 'NSString *',
    TypeEnum.DATETIME: 'NSDate *',

    TypeEnum.VOID: 'id',

    TypeEnum.LIST: 'NSArray *',
    TypeEnum.SET: 'NSSet *',
    TypeEnum.MAP: 'NSDictionary *'
}

NATIVE_DESCRIPTORS = {
    TypeEnum.BOOL: '[PDDescriptors bool0]',
    TypeEnum.INT16: '[PDDescriptors int16]',
    TypeEnum.INT32: '[PDDescriptors int32]',
    TypeEnum.INT64: '[PDDescriptors int64]',
    TypeEnum.FLOAT: '[PDDescriptors float0]',
    TypeEnum.DOUBLE: '[PDDescriptors double0]',

    TypeEnum.STRING: '[PDDescriptors string]',
    TypeEnum.DATETIME: '[PDDescriptors datetime]',

    TypeEnum.VOID: '[PDDescriptors void0]',
}

NATIVE_DEFAULTS = {
    TypeEnum.BOOL: 'NO',
    TypeEnum.INT16: '0',
    TypeEnum.INT32: '0',
    TypeEnum.INT64: '0L',
    TypeEnum.FLOAT: '0.0f',
    TypeEnum.DOUBLE: '0.0'
}
