import dash_bootstrap_components as dbc
import pynwb
from .nwb_schema import get_schema_from_hdmf_class
from .converter_classes import SingleForm, CompositeForm


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


def iter_metadata(metadata_json, parent_app, parent_name=None, forms=[]):
    """"""
    for k, v in metadata_json.items():
        if k in map_name_to_class.keys():
            item_schema = get_schema_from_hdmf_class(hdmf_class=map_name_to_class[k])
            if k in ['NWBFile', 'Subject']:
                form = SingleForm(
                    value=v,
                    base_schema=item_schema,
                    parent_app=parent_app,
                    item_name=k
                )
                forms.append(form)
            else:
                form = CompositeForm(v, k, item_schema, parent_app, parent_name)
                forms.append(form)
        else:
            iter_metadata(v, parent_app, parent_name=k, forms=forms)

    return forms


def get_form_from_metadata(metadata_json, parent_app):
    """"""
    forms = iter_metadata(metadata_json, parent_app, forms=[])

    tabs_dict = {}
    for f in forms:
        if isinstance(f, SingleForm):
            tabs_dict[f.id] = f
        else:
            if f.id not in tabs_dict.keys():
                tabs_dict[f.id] = f
            else:
                tabs_dict[f.id].children.children.extend(f.children.children)

    tabs = [dbc.Tab(v, label=k) for k, v in tabs_dict.items()]
    form_tabs = dbc.Tabs(tabs)

    return form_tabs
