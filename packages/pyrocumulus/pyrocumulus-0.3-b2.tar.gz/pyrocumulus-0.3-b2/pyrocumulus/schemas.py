# Copyright 2013 Juca Crispim <jucacrispim@gmail.com>

# This file is part of pyrocumulus.

# pyrocumulus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyrocumulus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyrocumulus.  If not, see <http://www.gnu.org/licenses/>.

import colander
import mongoengine.fields
from pyrocumulus.parsers import get_parser


translate_table = {mongoengine.fields.StringField: colander.String,
                   mongoengine.fields.IntField: colander.Int,
                   mongoengine.fields.EmailField: colander.String,
                   mongoengine.fields.FloatField: colander.Float,
                   mongoengine.fields.BooleanField: colander.Boolean}


class MetaDocumentSchema(type(colander.MappingSchema)):
    def __init__(cls, name, bases, kwargs):

        meta = kwargs.get('meta')
        if not meta or not meta.get('model'):
            super(MetaDocumentSchema, cls).__init__(
                name, bases, kwargs)
        else:
            model = meta.get('model')
            depth = kwargs.get('depth') or 0
            parsed = get_parser(model).parse()
            schema_kwargs = cls._get_schema_kwargs(parsed, kwargs)
            cls._set_attributes(schema_kwargs)
            super(MetaDocumentSchema, cls).__init__(
                name, bases, schema_kwargs)

    def _set_attributes(cls, schema_kwargs):
        # colander._SchemaMeta will delete
        # these attributes on super()
        # dummy method

        for key, value in schema_kwargs.items():
            if isinstance(value, colander._SchemaNode):
                setattr(cls, key, value)

    def _get_schema_kwargs(cls, parsed, kwargs):
        schema_kwargs = {}
        for key, value in parsed.items():
            if key in ('list_fields', 'embedded_documents',
                       'reference_fields', 'meta'):
                continue
            try:
                type_class = translate_table[value]
            except KeyError:
                type_class = colander.String

            schema_value = colander.SchemaNode(type_class())
            schema_kwargs[key] = schema_value

        schema_kwargs.update(kwargs)
        return schema_kwargs


class DocumentSchema(colander.MappingSchema, metaclass=MetaDocumentSchema):
    pass
