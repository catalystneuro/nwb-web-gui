from .forms import SourceForm
from .forms import MetadataForms
import pynwb
import dash_bootstrap_components as dbc

map_name_to_class = {
    "NWBFile": pynwb.file.NWBFile,
    "Subject": pynwb.file.Subject,
    "Device": pynwb.device.Device,
    # Ecephys
    "ElectrodeGroups": pynwb.ecephys.ElectrodeGroup,
    "ElectricalSeries": pynwb.ecephys.ElectricalSeries,
    # Ophys
    "OpticalChannel": pynwb.ophys.OpticalChannel,
    "ImagingPlane": pynwb.ophys.ImagingPlane,
    "TwoPhotonSeries": pynwb.ophys.TwoPhotonSeries,
    "PlaneSegmentation": pynwb.ophys.PlaneSegmentation
}


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

    return forms, 'source'


def iter_metadata_schema(schema, parent_name=None, forms=[]):

    for k, v in schema.items():
        if k in map_name_to_class.keys():
            form = MetadataForms(v, k)
            forms.append(form)
        else:
            if isinstance(v, dict):
                iter_metadata_schema(v, parent_name=k, forms=forms)
            else:
                pass

    return forms, 'metadata'


def get_forms_from_schema(schema, source=False):
    if source:
        forms, name = iter_source_schema(schema['properties'])
    else:
        forms, name = iter_metadata_schema(schema['properties'])

    if name == 'source':
        output_form = forms
    else:
        tabs = [dbc.Tab(f, label=f.parent_name) for f in forms]
        output_form = dbc.Tabs(tabs)

    return output_form
