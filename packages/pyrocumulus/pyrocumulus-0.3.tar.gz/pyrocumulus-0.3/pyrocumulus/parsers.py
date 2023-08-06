#-*- coding: utf-8 -*-

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


from mongoengine.fields import ReferenceField, ListField, EmbeddedDocumentField


def get_parser(model):
    return DocumentParser(model)


class DocumentParser:
    """
    Parse a Document and return a dict with {'field_name': field_type}.
    ReferenceFields, EmbeddedDocumentFields and ListFields are returned
    in repareted keys.
    """

    def __init__(self, model):
        self.model = model

    def _get_model_fields(self):
        fields_names = [i for i in dir(self.model) if not i.startswith('_')
                        and not i == 'objects']
        for name in fields_names:
            field = getattr(self.model, name)
            if callable(field):
                continue
            yield name, field

    def _get_model_reference_fields(self):
        """
        Creates a dict with {'field_name': ReferecedClass}
        for all ReferenceFields in the model
        """
        reference_fields = {}
        for name, field in self._get_model_fields():
            is_reference = isinstance(field, ReferenceField) or \
                (isinstance(field, ListField) and
                 isinstance(field.field, ReferenceField))
            if is_reference:
                try:
                    reference_fields[name] = field.document_type
                except AttributeError:
                    reference_fields[name] = field.field.document_type
        return reference_fields

    def _get_model_embedded_documents(self):
        embedded_documents = {}
        for name, field in self._get_model_fields():
            is_embed = isinstance(field, EmbeddedDocumentField) or \
                (isinstance(field, ListField) and
                 isinstance(field.field, EmbeddedDocumentField))
            if is_embed:
                try:
                    embedded_documents[name] = field.document_type
                except AttributeError:
                    # embedded on ListField
                    embedded_documents[name] = field.field.document_type
        return embedded_documents

    def _get_model_list_fields(self):
        list_fields = {}
        for name, field in self._get_model_fields():
            is_list = isinstance(field, ListField)
            if is_list:
                try:
                    list_fields[name] = field.field.document_type
                except AttributeError:
                    # its not a ReferenceField
                    list_fields[name] = type(field.field)
        return list_fields

    def _get_fields(self):
        lists = list(self._get_model_list_fields().keys())
        embedded_documents = list(self._get_model_embedded_documents().keys())
        references = list(self._get_model_reference_fields().keys())
        excluded = set(lists + embedded_documents + references)
        excluded.add('pk')
        fields = {}
        for name, field in self._get_model_fields():
            if name in excluded:
                continue
            fields[name] = type(field)
        return fields

    def parse(self):
        parsed_obj = self._get_fields()
        parsed_obj['list_fields'] = self._get_model_list_fields()
        # todo: must change this key name
        parsed_obj['embedded_documents'] = self._get_model_embedded_documents()
        parsed_obj['reference_fields'] = self._get_model_reference_fields()
        return parsed_obj
