from .forms import SourceForm
from .forms import MetadataForms
import pynwb
import dash_bootstrap_components as dbc

map_name_to_class = {
    "NWBFile": pynwb.file.NWBFile,
    "Subject": pynwb.file.Subject,
    #"Device": pynwb.device.Device,
    # Ecephys
    "ElectrodeGroups": pynwb.ecephys.ElectrodeGroup,
    "ElectricalSeries": pynwb.ecephys.ElectricalSeries,
    # Ophys
    "OpticalChannel": pynwb.ophys.OpticalChannel,
    "ImagingPlane": pynwb.ophys.ImagingPlane,
    "TwoPhotonSeries": pynwb.ophys.TwoPhotonSeries,
    "PlaneSegmentation": pynwb.ophys.PlaneSegmentation
}

nwb_composite_forms = ['Ophys', 'Ecephys', 'Behavior']
nwb_single_forms = ['NWBFile', 'Subject']


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
        if k in nwb_single_forms:
            form = MetadataForms(v, k, form_style='single')
            forms.append(form)
        elif k in nwb_composite_forms:
            form = MetadataForms(v, k, form_style='composite', definitions=definitions)
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
