from .forms import SourceForm


def iter_source_schema(schema, parent_name=None, forms=[]):

    for k, v in schema.items():
        if isinstance(v, dict):
            if 'items' in v.keys():
                iter_source_schema(v['items'], parent_name=k, forms=forms)
            else:
                required = schema['required']
                fields = schema['properties']
                form = SourceForm(required, fields, parent_name)
                forms.append(form)

    return forms


def iter_metadata_schema(schema):
    pass


def get_forms_from_schema(schema, source=False):
    if source:
        forms = iter_source_schema(schema['properties'])
    else:
        iter_metadata_schema(schema)

    return forms
