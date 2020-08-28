from .forms import SourceForm
from .forms import MetadataForms
import pynwb

map_name_to_class = {
    "NWBFile": pynwb.file.NWBFile,
    "Subject": pynwb.file.Subject,
    "Device": pynwb.device.Device,
    # Ecephys
    "ElectrodeGroup": pynwb.ecephys.ElectrodeGroup,
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

    return forms


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

    return forms


def get_forms_from_schema(schema, source=False):
    if source:
        forms = iter_source_schema(schema['properties'])
    else:
        forms = iter_metadata_schema(schema['properties'])

    return forms
