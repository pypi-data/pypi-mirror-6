#!/usr/bin/env python
'''
dataschema - schema validation for Python data structures

Copyright (c) 2014 Stefan Wiechula

Based on "jsonschema - JSON schema validation in Python" by Stefan Wiechula and
Chris Garland.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__version__ = '0.1'


from types import (StringTypes, IntType, FloatType, LongType, DictType,
        ListType, BooleanType)

import re



class SchemaError(Exception): pass



class Validator(object):

    def __init__(self, schema, other_schemata={}):
        self.schema = schema
        self.other_schemata = other_schemata


    def validate(self, data):
        return self._check(data, self.schema, path=())


    def _check(self, instance, schema, path):

        # schema sanity
        if not isinstance(schema, DictType):
            raise SchemaError('schema not a dictionary: %r' % schema)

        if not schema.has_key('type'):
            raise SchemaError('no type specified by schema: %r' % schema)

        errors = list()

        # type-specific checks
        if schema['type'] == 'any':
            checker = self._check_type_any
        else:
            checker = getattr(self, '_check_type_%s' % schema['type'].__name__, None)
            if checker is None:
                raise SchemaError('unknown type: %r' % schema['type'])

        errors.extend(checker(instance, schema, path))

        # type-indifferent checks
        if not errors: errors.extend(self._check_extends(instance, schema, path))
        if not errors: errors.extend(self._check_options(instance, schema, path))

        # extra validation in a callable
        extraValidation = schema.get('extraValidation', None)
        if extraValidation and not errors:
            for (_path, message) in extraValidation(instance):
                errors.append(((path + _path), message))

        return errors


    def _check_extends(self, instance, schema, path):
        #print '_check_extends(\n\t%r,\n\t%r\n)' % (instance, schema)

        def find_schema(name):
            '''Find a schema by name in self.other_schemata'''
            if name in self.other_schemata:
                return self.other_schemata[name]
            else:
                raise SchemaError('extends unknown schema: %r' % name)

        errors = []

        extends = schema.get('extends', None)
        if extends is  None:
            return []

        elif isinstance(extends, StringTypes):
            # The value of "extends" is a string reprsenting the name of
            # another schema that instance must also validate against.
            errors.extend(self._check(instance, find_schema(name=extends), path))

        elif isinstance(extends, ListType):
            # The value of "extends" is a list of strings, representing the
            # names of other schemata.  The instance must validate against at
            # least one of them.
            for name in extends:
                e = self._check(instance, find_schema(name), path)
                if not e:
                    break
            else:
                errors.append((path, 'does not match any schema in extend'))

        else:
            raise SchemaError('value of extends must be schema name string or list thereof')

        return errors


    def _check_options(self, instance, schema, path):
        #print '_check_options(\n\t%r,\n\t%r\n)' % (instance, schema)

        options = schema.get('options', None)
        if options is None:
            return []
        elif not isinstance(options, ListType):
            raise SchemaError('"options" must be a list of literals, got %r' % options)
        elif instance in options:
            return []
        else:
            return [(path, 'value not in options')]


    def _check_type_any(self, instance, schema, path):
        #print '_check_type_any(\n\t%r,\n\t%r\n)' % (instance, schema)
        return []


    def _check_type_list(self, lst, schema, path):
        #print '_check_type_list(\n\t%r,\n\t%r\n)' % (lst, schema)

        errors = list()

        maxItems = schema.get('maxItems', None)
        minItems = schema.get('minItems', None)

        if not isinstance(lst, ListType):
            errors.append((path, 'list required but %s found' % type(lst).__name__))

        elif (maxItems is not None) and (len(lst) > maxItems):
            errors.append((path, 'too many items'))

        elif (minItems is not None) and (len(lst) < minItems):
            errors.append((path, 'too few items'))

        else:

            if isinstance(schema['items'], ListType):
                # tuple typing (given a fixed-length list of schemas)

                item_schemas = schema['items']
                for index, (instance, schema) in enumerate(zip(lst, item_schemas)):
                    errors.extend(self._check(instance, schema, path + (index, )))

                if len(lst) < len(item_schemas): errors.append((path, 'too few items'))
                if len(lst) > len(item_schemas): errors.append((path, 'too many items'))

            elif isinstance(schema['items'], DictType):
                # one schema for all items

                for index, instance in enumerate(lst):
                    errors.extend(self._check(instance, schema['items'], path + (index, )))


        return errors


    def _check_type_bool(self, b, schema, path):
        #print '_check_type_bool(\n\t%r,\n\t%r\n)' % (b, schema)

        if isinstance(b, BooleanType):
            return []
        else:
            return [(path, 'bool required but %s found' % type(b).__name__)]


    def _check_type_dict(self, d, schema, path):
        #print '_check_type_dict(\n\t%r,\n\t%r\n)' % (d, schema)

        errors = list()

        if not isinstance(d, DictType):
            errors.append((path, 'dict required but %s found' % type(d).__name__))

        else:
            additional_items_schema = schema.get('additionalItems', None)

            # every item in the dict must validate against the corresponding
            # item schema or against the additionalItems schema if one is given
            for (key, value) in d.items():
                if key in schema.get('items', {}).keys():
                    errors.extend(
                            self._check(value, schema['items'][key], path + (key,))
                            )
                elif additional_items_schema is not None:
                    errors.extend(
                            self._check(value, additional_items_schema, path + (key,))
                            )
                else:
                    errors.append((path + (key,), 'not in schema'))

            # every item defined in the schema and not marked "optional" must
            # be present in the instance
            for (key, item_schema) in schema.get('items', {}).items():
                if d.has_key(key):
                    pass # already checked
                elif item_schema.get('optional', False):
                    pass
                else:
                    errors.append((path + (key,), 'missing and not optional'))

        return errors


    def _check_type_Number(self, num, schema, path):
        #print '_check_type_Number(\n\t%r,\n\t%r\n)' % (num, schema)

        errors = []

        if type(num) not in [FloatType, IntType, LongType]:
            errors.append((path, 'number required but %s found' % type(num).__name__))

        else:
            maximum = schema.get('maximum', None)
            if (maximum is not None) and (num > maximum):
                errors.append((path, 'greater than %r' % maximum))

            minimum = schema.get('minimum', None)
            if (minimum is not None) and (num < minimum):
                errors.append((path, 'less than %r'    % minimum))

        return errors


    def _check_type_int(self, num, schema, path):
        #print '_check_type_int(\n\t%r,\n\t%r\n)' % (num, schema)

        errors = []

        if type(num) not in [IntType, LongType]:
            errors.append((path, 'int required but %s found' % type(num).__name__))

        else:
            # All the number checks (minimum, maximum) apply
            errors.extend(self._check_type_Number(num, schema, path))

        return errors


    def _check_type_float(self, num, schema, path):
        #print '_check_type_float(\n\t%r,\n\t%r\n)' % (num, schema)

        errors = []

        if not isinstance(num, FloatType):
            errors.append((path, 'float required but %s found' % type(num).__name__))

        else:
            # All the number checks (minimum, maximum) apply
            errors.extend(self._check_type_Number(num, schema, path))

        return errors


    def _check_type_str(self, s, schema, path):
        #print '_check_type_str(\n\t%r,\n\t%r\n)' % (s, schema)

        errors = []

        if not isinstance(s, StringTypes):
            errors.append((path, 'str required but %s found' % type(s).__name__))

        else:
            maxLength = schema.get('maxLength', None)
            if (maxLength is not None) and (len(s) > maxLength):
                errors.append((path, 'longer than %r'  % maxLength))

            minLength = schema.get('minLength', None)
            if (minLength is not None) and (len(s) < minLength):
                errors.append((path, 'shorter than %r' % minLength))

            pattern = schema.get('pattern', None)
            if (pattern is not None) and (re.match(str(pattern), s) is None):
                errors.append((path, 'does not match pattern'))

        return errors



