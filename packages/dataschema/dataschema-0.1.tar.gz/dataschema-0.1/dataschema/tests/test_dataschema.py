#!/usr/bin/env python
'''
unit tests for dataschema - schema validation for Python datastructures

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


import numbers
import unittest

import dataschema



class TestCase(unittest.TestCase):


    def test01(self): # an empty dict (no items)

        schema = {
            "type": dict,
            "items": { }
            }

        validator = dataschema.Validator(schema)

        for (instance, errors) in [
            ({},             []),
            ({"foo": "bar"}, [(('foo',), 'not in schema')]),
            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))



    def test02(self): # number, boolean, string, optional, min/max

        person_schema = {
                "description": "A person",
                "type": dict,
                "items":
                    {
                    "age"     : {"type": numbers.Number, "minimum":0, "maximum":125},
                    "bored"   : {"type": bool, "optional": True},
                    "nickname": {"type": str, "maxLength": 8, "minLength": 3}
                    }
            }

        validator = dataschema.Validator(person_schema)

        for (instance, errors) in [
            ({"nickname": "Sally", "bored": True, "age":20},  []),
            ({"nickname": "John Doe", "age" : 124},           []),
            ({"age" : 24},                                    [(('nickname',), 'missing and not optional')]),
            ({},                                              [(('age',), 'missing and not optional'), (('nickname',), 'missing and not optional')]),
            ({"nickname" : 1011, "age": 2},                   [(('nickname',), "str required but int found")]),
            ({"nickname": "Henry", "age" : 126},              [(('age',), 'greater than 125')]),
            ({"nickname": "Zygot", "age" : -1},               [(('age',), 'less than 0')]),
            ({"nickname": "Sally", "bored": 1, "age":20},     [(('bored',), "bool required but int found")]),
            ({"nickname": "Jo", "age":2},                     [(('nickname',), "shorter than 3")]),
            ({"nickname": "Josephine", "age":2},              [(('nickname',), "longer than 8")]),
            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))

    
    def test03(self): # fixed length list with "tuple typing"

        list_schema = {
                "type": list,
                "items": [
                    {"type": str},
                    {"type": int}
                    ]
            }

        validator = dataschema.Validator(list_schema)

        for (instance, errors) in [
            ( {},                  [((), "list required but dict found")]),
            ( ["foo", 20],         []),
            ( [20, "foo"],         [((0,), "str required but int found"), ((1,), "int required but str found")]),
            ( [20],                [((), 'too few items'), ((0,), "str required but int found")]),
            ( ["foo"],             [((), 'too few items')]),
            ( [],                  [((), 'too few items')]),
            ( ["foo", 20, 21],     [((), 'too many items')]),
            ]:
            #print 'instance', instance

            self.assertEqual(errors, sorted(validator.validate(instance)))


    def test04(self): # variable length list

        dummy_schema = {
                "type": list,
                "items": {"type": numbers.Number},
                "minItems": 1,
                "maxItems": 4
            }

        validator = dataschema.Validator(dummy_schema)

        for (instance, errors) in [
            ( {},                  [((), "list required but dict found")]),
            ( [1],                 []),
            ( [11, 22],            []),
            ( [-1, 42, 2.0, 0],    []),
            ( [],                  [((), 'too few items')]),
            ( [1, 2, 3, 4, 5],     [((), 'too many items')]),
            ( ["foo", 20],         [((0,), "number required but str found")]),
            ( [20, "bar"],         [((1,), "number required but str found")]),
            ( [20, True],          [((1,), "number required but bool found")]),
            ( [20, {}],            [((1,), "number required but dict found")]),
            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))


    def test05(self): # options (enumeration of possible, literal values)

        option_schema = {
                "type": str,
                "options": ["this", "that", "the other thing"]
            }

        validator = dataschema.Validator(option_schema)

        for (instance, errors) in [
            # wrong type
            ( {},                  [((), "str required but dict found")]),
            ( [],                  [((), "str required but list found")]),
            ( ["this", "that"],    [((), 'str required but list found')]),

            # valid
            ( "that",              []),
            ( "this",              []),
            ( "the other thing",   []),

            # right type, wrong value
            ( "",                  [((), "value not in options")]),
            ( "the",               [((), "value not in options")]),
            ( "those",             [((), "value not in options")]),
            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))


    def test06(self): # extends and id (simple schema inheritance)

        base_schema = {
                "type": dict,
                "items": {
                    "this": {"type": str},
                    "that": {"type": str}
                    }
            }

        list_of_base_schema = {
                "type": list,
                "items": {
                    "type": dict,
                    "extends": "the_base_schema",
                    "additionalItems": {"type": "any"}
                    }
            }

        validator = dataschema.Validator(list_of_base_schema, other_schemata={'the_base_schema':base_schema})

        for (instance, errors) in [
            # valid
            ( [],                          []), # no minLength on the list, so empty is valid
            ( [{"this": "", "that": ""}],  []),
            ( [{"this": "A", "that": "B"}, {"this": "x", "that": "y"}],  []),

            # wrong type
            ( {},                                  [((), 'list required but dict found')]),
            ( {'this': '', 'that': ''},            [((), 'list required but dict found')]),
            ( ['this'],                            [((0,), 'dict required but str found')]),
            ( ['what', {'this': '', 'that': ''}],  [((0,), 'dict required but str found')]),
            ( [{'this': 1, 'that': ''}],           [((0, 'this'), 'str required but int found')]),

            # additional items
            #   base_schema disallows additional items and the dict in
            #   list_of_base_schema allows additional items but doesn't specify
            #   any of its own so only "this" and "that" are acceptable.
            ( [{"this": "", "that": "", "those": []}],  [((0, 'those',), 'not in schema')]),

            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))


    def test07(self): # extends and id (selective schema inheritance)

        base_1 = {
                "type": dict,
                "items": {
                    "this": {"type": str}
                    }
            }

        base_2 = {
                "type": dict,
                "items": {
                    "that": {"type": str}
                    }
            }

        list_of_base_schema = {
                "type": list,
                "items": {
                    "type": dict,
                    "extends": ["the_first_base_schema", "the_second_base_schema"],
                    "additionalItems": {"type": "any"}
                    }
            }

        validator = dataschema.Validator(
                list_of_base_schema,
                other_schemata={
                    "the_first_base_schema" : base_1,
                    "the_second_base_schema": base_2,
                    }
                )

        for (instance, errors) in [
            # valid
            ( [],                              []), # no minLength on the list, so empty is valid
            ( [{'this': ''}],                  []),
            ( [{'that': ''}],                  []),
            ( [{'this': 'A'}, {'that': 'y'}],  []),

            # wrong type
            ( {},                                  [((), 'list required but dict found')]),
            ( {'that': ''},                        [((), 'list required but dict found')]),
            ( ['this'],                            [((0,), 'dict required but str found')]),
            ( ['what', {'this': ''}],              [((0,), 'dict required but str found')]),
            ( [{'this': 1}, {'that': ''}],         [((0,), 'does not match any schema in extend')]),

            # additional items
            #   Both base schemata disallow additional items and the dict in
            #   list_of_base_schema allows additional items but doesn't specify
            #   any of its own so only "this" and "that" are acceptable.
            ( [{'this': ''}, {'that': ''}, {'those': []}],  [((2,), 'does not match any schema in extend')]),

            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))


    def test08(self): # pattern (string matches a regular expression)

        schema = {
                "type": str,
                "pattern": "^[0-9]{0,10}$"
            }

        validator = dataschema.Validator(schema)

        for (instance, errors) in [
            # valid
            ("",           []),
            ("0",          []),
            ("9",          []),
            ("9876543210", []),
            ("4433552299", []),

            # wrong type
            (0,          [((), "str required but int found")]),
            (9,          [((), "str required but int found")]),
            (9876543210, [((), "str required but long found")]),
            (4433552299, [((), "str required but long found")]),
            (True,       [((), "str required but bool found")]),

            # does not match pattern
            ("-1",            [((), "does not match pattern")]),
            ("0x123",         [((), "does not match pattern")]),
            ("123d",          [((), "does not match pattern")]),
            ("123l",          [((), "does not match pattern")]),
            ("9876543210123", [((), "does not match pattern")]),

            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))


    def test09(self): # extraValidation (callable custom validators)

        def my_validator(x):
            if x % 2:
                return [((), 'not an even number')]
            else:
                return []

        schema = {
                "type": int,
                "extraValidation": my_validator,
                }

        validator = dataschema.Validator(schema)

        for (instance, errors) in [
            # valid
            (0,      []),
            (8,      []),
            (987654, []),
            (443356, []),

            # wrong type
            ('0',        [((), "int required but str found")]),
            ('8',        [((), "int required but str found")]),
            (True,       [((), "int required but bool found")]),

            # fails extraValidation
            (-1,    [((), "not an even number")]),
            (0x123, [((), "not an even number")]),
            (123,   [((), "not an even number")]),
            (9,     [((), "not an even number")]),

            ]:
            #print 'instance', instance

            self.assertEqual(errors, validator.validate(instance))


    def test10(self): # extraValidation with longer paths

        def my_validator(d):
            '''Check that all the keys in a dictionary start with a vowel.
            '''
            errors = []

            for key in d:
                if not key.lower().startswith(tuple('aeiou')):
                    errors.append(((key,), 'key does not start with a, e, i, o, or u'))

            return errors

        schema = {
                'type': list,
                'items': {
                    'type': dict,
                    'additionalItems': { 'type': 'any' },
                    'extraValidation': my_validator,
                    }
                }

        validator = dataschema.Validator(schema)

        instance = [
                {'asdf': None, 'oiuy': True, 'erty': False}, # 0
                {'fdsa': None, 'yuio': True, 'ytre': False}, # 1
                {'ASDF': None, 'OIUY': True, 'ERTY': False}, # 2
                {'FDSA': None, 'YUIO': True, 'YTRE': False}, # 3
                ]

        errors = [
                ((1, 'fdsa'), 'key does not start with a, e, i, o, or u'),
                ((1, 'yuio'), 'key does not start with a, e, i, o, or u'),
                ((1, 'ytre'), 'key does not start with a, e, i, o, or u'),
                ((3, 'FDSA'), 'key does not start with a, e, i, o, or u'),
                ((3, 'YUIO'), 'key does not start with a, e, i, o, or u'),
                ((3, 'YTRE'), 'key does not start with a, e, i, o, or u'),
                ]

        self.assertEqual(
                set(errors), 
                set(validator.validate(instance))
                )


if __name__ == '__main__':
    unittest.main()

