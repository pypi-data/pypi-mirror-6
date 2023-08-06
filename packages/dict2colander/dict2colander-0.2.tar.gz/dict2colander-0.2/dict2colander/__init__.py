# Copyright (C) 2012, Peter Facka, David Nemcok
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import colander


class Default:
    """
    Empty class to indentfy default value
    """
    pass


class InheritType(colander.String):
    """
    Type definition which is used in schemas for validators and widgets.
    It states that type of clander Node is inherited from parent Node.
    """
    pass


class MaxMappingCount(object):
    """
    Validator to limit count of non-None keys in mapping schema.
    """

    def __init__(self, max_count):
        self.max_count = max_count

    def __call__(self, node, value):

        non_none_count = 0
        dict_value = dict(value)

        for key in dict_value:

            if dict_value[key] is not None:
                non_none_count += 1

            if non_none_count > self.max_count:
                raise colander.Invalid(node,
                                       'more than %i key(s) defined in %s'
                                       % (self.max_count, dict_value))


class ArgumentsTuple(colander.Tuple):
    """
    A colander.Tuple extension used for schemas for validator and deform
    widged definitions in dictionary schemas
    """
    def _validate(self, node, value):
        if not hasattr(value, '__iter__'):
            raise colander.Invalid(node, '"$s" is not iterable' % value)

        return list(value)

    def _impl(self, node, value, callback):
        value = self._validate(node, value)
        error = None
        result = []

        for num, subval in enumerate(value):
            try:
                result.append(callback(node.children[num], subval))
            except colander.Invalid as e:
                if error is None:
                    error = colander.Invalid(node)
                error.add(e, num)

        if error is not None:
            raise error

        return tuple(result)


class ArgumentsTupleSchema(colander.Schema):
    schema_type = ArgumentsTuple


class RangeArgsSchema(ArgumentsTupleSchema):
    """
    Schema for Range validator arguments
    """
    min = colander.SchemaNode(InheritType(), missing=None)
    max = colander.SchemaNode(InheritType(), missing=None)
    min_err = colander.SchemaNode(colander.String(), missing=None,
                                  default=colander.null)
    max_err = colander.SchemaNode(colander.String(), missing=None,
                                  default=colander.null)


class LengthArgsSchema(ArgumentsTupleSchema):
    """
    Schema for Length validator arguments
    """
    min = colander.SchemaNode(colander.Integer(), missing=None)
    max = colander.SchemaNode(colander.Integer(), missing=None)


class OneOfArgsSchema(ArgumentsTupleSchema):
    """
    Schema for OneOf validator arguments
    """
    choices = colander.SchemaNode(colander.Sequence(),
                                  colander.SchemaNode(InheritType()),
                                  missing=[])


class RegexArgsSchema(ArgumentsTupleSchema):
    """
    Schema for Regex validator arguments
    """
    regex = colander.SchemaNode(colander.String())
    msg = colander.SchemaNode(colander.String(), missing=None)


class EmailArgsSchema(ArgumentsTupleSchema):
    """
    Schema for Email validator arguments
    """
    msg = colander.SchemaNode(colander.String(), missing=None)


class SchemaBuilder(object):
    """
    Builds colander.Mapping schema from schema defined in dictionary while
    using types, validators, preparers and after_bind procedures assigned
    to concrete schema builder instance.

    By default you can use following types: ``Mapping``, ``Sequence``,
    ``Tuple``, ``Integer``, ``Float``, ``String``, ``Decimal``, ``Boolean``,
    ``DateTime``, ``Date`` and ``Time``

    and following validators: ``Range``, ``Length``, ``OneOf``, ``OneOf`` and
    ``Email``
    """
    def __init__(self):

        self._types = {}
        self.add_type('Mapping', colander.Mapping)
        self.add_type('Sequence', colander.Sequence)
        self.add_type('Tuple', colander.Tuple)
        self.add_type('Integer', colander.Integer)
        self.add_type('Float', colander.Float)
        self.add_type('String', colander.String)
        self.add_type('Decimal', colander.Decimal)
        self.add_type('Boolean', colander.Boolean)
        self.add_type('DateTime', colander.DateTime)
        self.add_type('Date', colander.Date)
        self.add_type('Time', colander.Time)

        self._validators = {}
        self.add_validator('Range', colander.Range, RangeArgsSchema)
        self.add_validator('Length', colander.Length, LengthArgsSchema)
        self.add_validator('OneOf', colander.OneOf, OneOfArgsSchema)
        self.add_validator('Regex', colander.Regex, RegexArgsSchema)
        self.add_validator('Email', colander.Email, EmailArgsSchema)

        self._widgets = {}

        self._preparers = {}

        self._after_bind = {}

    def add_type(self, name, cls):
        """
        Use this method to add your custom types (or override existing).

        name -- is name of type used in schema dictionaries to name a type
        cls -- is class type (not an instance) used to map this type
        """
        self._types[name] = cls

    def add_validator(self, name, cls, args_schema=None, kwargs_schema=None):
        """
        Use this method to add your custom valiator (or override existing).

        name -- is name of validator used in schema dictionaries to name a type
        cls -- is callable class type (not an instance) which will assigned
        as validator for provided ``name``.
        args_schema -- is schema for arguments of your validator
        kwargs_schema -- is schema for keyword arguments of your validator
        """
        self._validators[name] = dict(typ=cls, args=args_schema,
                                      kwargs=kwargs_schema)

    def add_widget(self, name, cls, args_schema=None, kwargs_schema=None):
        """
        This method is for adding Defrom widgets

        name -- is name of widget used in schema dictionaries to name a type
        cls -- is class type (not an instance) which will assigned
        as widget for provided ``name``.
        args_schema -- is schema for arguments of your widget
        kwargs_schema -- is schema for keyword arguments of your widget
        """
        self._widgets[name] = dict(typ=cls, args=args_schema,
                                   kwargs=kwargs_schema)

    def add_preparer(self, name, cls, args_schema=None, kwargs_schema=None):
        """
        This method is for adding colander preparers

        name -- is name of preparer used in schema dictionaries to name a type
        cls -- is class type (not an instance) which will assigned
        as preparer for provided ``name``.
        args_schema -- is schema for arguments of your preparer
        kwargs_schema -- is schema for keyword arguments of your preparer
        """
        self._preparers[name] = cls

    def add_after_bind(self, name, cls, args_schema=None, kwargs_schema=None):
        """
        This method is for adding colander after_binds

        name -- is name of after_bind used in schema dictionaries to name a type
        cls -- is class type (not an instance) which will assigned
        as after_bind for provided ``name``.
        args_schema -- is schema for arguments of your after_bind
        kwargs_schema -- is schema for keyword arguments of your after_bind
        """
        self._after_bind[name] = cls

    def dict_to_schema(self, schema_dict):
        validation_schema = self._get_validation_schema()
        schema_dict = validation_schema.deserialize(schema_dict)
        return self._build_node(schema_dict)

    def _get_validator_schema(self):
        return self._create_callable_parameter_schema(self._validators,
                                                      'validators')

    def _get_widget_schema(self):
        return self._create_callable_parameter_schema(self._widgets,
                                                      'widget')

    def _get_validation_schema(self):
        root = colander.SchemaNode(colander.Mapping())

        # typ
        root.add(colander.SchemaNode(colander.String(), name='type',
                                     validator=colander.OneOf(self._types)))

        #name
        root.add(colander.SchemaNode(colander.String(), name='name'))

        #children
        root.add(colander.SchemaNode(colander.Sequence(), root,
                                     name='subnodes', missing=None))

        #default
        root.add(colander.SchemaNode(colander.String(), name='default',
                                     default=colander.null, missing=None))

        #missing
        root.add(colander.SchemaNode(colander.String(), name='missing',
                                     default=colander.null, missing=None))

        #preparer
        root.add(colander.SchemaNode(colander.String(), name='preparer',
                                     default=colander.null, missing=None))

        #validator
        root.add(self._get_validator_schema())

        #after_bind
        root.add(colander.SchemaNode(colander.String(), name='after_bind',
                                     default=colander.null, missing=None))

        #title
        root.add(colander.SchemaNode(colander.String(), name='title',
                                     default=colander.null, missing=None))

        #description
        root.add(colander.SchemaNode(colander.String(), name='description',
                                     default=colander.null, missing=None))

        #widget
        root.add(self._get_widget_schema())

        return root


    def _create_callable_parameter_schema(self, options, node_name):
        parameter_node = colander.SchemaNode(colander.Mapping(),
                                             default=colander.null,
                                             name=node_name, missing=None)

        for key in options:
            variant_node = colander.SchemaNode(colander.Mapping(), name=key,
                                               missing=None,
                                               default=colander.null)

            args = options[key]['args']
            kwargs = options[key]['kwargs']

            if args is not None:
                variant_node.add(args(name='args', missing=None))

            if kwargs is not None:
                variant_node.add(kwargs(name='kwargs', missing=None))

            parameter_node.add(variant_node)

        return parameter_node


    def _build_node(self, schema_dict):

        schema = self._build_node_schema(schema_dict)

        # take care of children
        if schema_dict['subnodes'] is not None:

            for child_dict in schema_dict['subnodes']:
                child_schema = self._build_node(child_dict)
                schema.add(child_schema)

        return schema

    def _build_node_schema(self, schema_dict):

        typ = self._types[schema_dict['type']]
        name = schema_dict['name']

        # fake node used for conversion of default, missing fields and
        # validator arguments
        fake_node = colander.SchemaNode(typ())

        if schema_dict['default'] is None:
            default = colander.null
        else:
            default = fake_node.deserialize(schema_dict['default'])

        if schema_dict['missing'] is None:
            missing = colander.required
        else:
            missing = fake_node.deserialize(schema_dict['missing'])

        if schema_dict['validators'] is not None:
            validator = self._parse_validators(schema_dict['validators'],
                                               fake_node)
        else:
            validator = None

        kwargs = dict(name=name, default=default,
                      missing=missing, validator=validator,
                      description=schema_dict['description'])

        if schema_dict['widget'] is not None:
            kwargs['widget'] = self._parse_widget(schema_dict['widget'])

        if schema_dict['title'] is not None:
            kwargs['title'] = schema_dict['title']

        schema = colander.SchemaNode(typ(), **kwargs)
        return schema

    def _parse_validators(self, validators_node, parent_typ):

        descriptions = {}

        for key in validators_node:
            descr = validators_node[key]

            if descr is not None:
                descriptions[key] = descr

        descriptions_len = len(descriptions)

        if descriptions_len == 1:
            key = next(iter(descriptions.keys()))
            return self._build_validator(descriptions[key], key, parent_typ)

        elif descriptions_len > 1:
            validators = []
            for key in descriptions:
                validators.append(self._build_validator(descriptions[key], key,
                                  parent_typ))
            return colander.All(validators)

        else:
            #FIXME
            return self._validators[validator_name]['typ']()

    def _build_validator(self, description, validator_name, parent_node):
        arguments_descr = description['args']

        args_schema = self._validators[validator_name]['args']
        validator_cls = self._validators[validator_name]['typ']

        converted_args = []

        for i, arg in enumerate(arguments_descr):
            #TODO: find better way to get to children nodes list
            if isinstance(args_schema.__all_schema_nodes__[i].typ,
                          InheritType):
                v = parent_node.deserialize(arg)
            else:
                v = arg
            converted_args.append(v)

        return validator_cls(*converted_args)

    def _parse_widget(self, widget_dict):
        for key in widget_dict:
            descr = widget_dict[key]

            if descr is not None:
                widget = self._widgets[key]['typ']
                args = widget_dict[key].get('args', [])
                kwargs = widget_dict[key].get('kwargs', {})
                kwargs = self._remove_defaults_from_dict(kwargs)
                return widget(*args, **kwargs)

    def _remove_defaults_from_dict(self, d):
        new_d = {}
        for key in d:
            if d[key] != Default:
                new_d[key] = d[key]

        return new_d


def dict2colander(schema_dict, builder=SchemaBuilder()):
    """
    Shortcut function for dictionary to colander scheme conversion.
    Argument ``schema_dict`` is schema defined in python dictionary and
    with argument ``builder`` you can provide customized instance of
    SchemaBuilder with custom validators or types added.

    Function returns instace of colander.MappingSchema build with
    default or provided SchemaBuilder from provided dictionary.
    """
    return builder.dict_to_schema(schema_dict)
