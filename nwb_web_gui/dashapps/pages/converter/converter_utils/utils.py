from .forms import SourceForm
from .forms import MetadataForms, MetadataForm


def iter_source_schema(schema, parent_name=None, forms=[]):

    for k, v in schema.items():
        if isinstance(v, dict):
            if 'required' in v.keys():
                required = v['required']
            else:
                required = []
            fields = v['properties']
            form = SourceForm(required, fields, k)
            forms.append(form)

    return forms


def get_forms_from_schema(schema, definitions=None, source=False):
    if source:
        forms = iter_source_schema(schema['properties'])
    else:
        # forms, name = iter_metadata_schema(schema['properties'], definitions)
        forms = MetadataForm(schema=schema)

    return forms
