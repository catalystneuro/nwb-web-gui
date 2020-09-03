from .forms import SourceForm
from .forms import MetadataForms


nwb_forms = {
    "NWBFile": 'single',
    "Subject": 'single',
    "Ophys": ["Device", "DFOverF", "Fluorescence", "ImageSegmentation", "ImagingPlane", "TwoPhotonSeries"],
    "Ecephys": ["Device", "ElectricalSeries", "ElectrodeGroups"],
    "Behavior": ["Position", "BehavioralEvents"]
}


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

    return forms, 'source'


def iter_metadata_schema(schema, definitions, parent_name=None, forms=[]):

    for k, v in schema.items():
        if k in nwb_forms and isinstance(nwb_forms[k], str):
            form = MetadataForms(v, k, form_style='single')
            forms.append(form)
        elif k in nwb_forms.keys() and isinstance(nwb_forms[k], list):
            form = MetadataForms(v, k, form_style='composite', definitions=definitions, composite_children=nwb_forms[k])
            forms.append(form)
        else:
            if isinstance(v, dict):
                iter_metadata_schema(v, parent_name=parent_name, forms=forms)

    return forms, 'metadata'


def get_forms_from_schema(schema, definitions=None, source=False):
    if source:
        forms, name = iter_source_schema(schema['properties'])
    else:
        forms, name = iter_metadata_schema(schema['properties'], definitions)

    return forms
