from .forms import SourceForm, MetadataForm


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


def get_forms_from_schema(schema, source=False):
    if source:
        forms = iter_source_schema(schema['properties'])
    else:
        forms = MetadataForm(schema=schema, key="Metadata")

    return forms
