import dash_bootstrap_components as dbc
import pynwb
from .nwb_schema import get_schema_from_hdmf_class
from .converter_classes import SingleForm, CompositeForm, SourceForm
from pathlib import Path
import json


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


def iter_metadata(metadata_json, parent_app, parent_name=None, forms=[], inputs_forms=[]):

    for k, v in metadata_json.items():
        if k in map_name_to_class.keys():
            item_schema = get_schema_from_hdmf_class(hdmf_class=map_name_to_class[k])
            if k in ['NWBFile', 'Subject']:
                form = SingleForm(
                    value=v,
                    base_schema=item_schema,
                    item_name=k
                )
                forms.append(form)
            else:
                form = CompositeForm(v, k, item_schema, parent_name)
                forms.append(form)
        else:
            iter_metadata(v, parent_app, parent_name=k, forms=forms)

    return forms


def iter_source_metadata(schema, source_json, parent_name=None, source_forms=[]):

    for k, v in source_json.items():
        if k in schema.keys():
            form = SourceForm(
                value=v,
                base_schema=schema[k],
                item_name=k
            )
            source_forms.append(form)

    return source_forms


def get_form_from_metadata(metadata_json, parent_app, source=False):
    """"""
    if not source:
        forms = iter_metadata(metadata_json, parent_app, forms=[])
    else:
        schema_path = Path.cwd() / 'nwb_web_gui' / 'uploads' / 'formData' / 'source_schema.json'
        with open(schema_path, 'r') as inp:
            schema = json.load(inp)

        source_forms = iter_source_metadata(schema['properties'], metadata_json, parent_name=None, source_forms=[])
        forms = []

    if len(forms) > 0:
        tabs_dict = {}
        for f in forms:
            if isinstance(f, SingleForm):
                tabs_dict[f.id] = f
            else:
                if f.id not in tabs_dict.keys():
                    tabs_dict[f.id] = f
                else:
                    tabs_dict[f.id].children.children.extend(f.children.children)

        tabs = [dbc.Tab(v, label=k, tab_style={'background-color': '#f7f7f7', 'border':'solid', 'border-color': '#f7f7f7', 'border-width': '1px'}) for k, v in tabs_dict.items()]
        form_tabs = dbc.Tabs(tabs)
    else:
        cards = [dbc.Card([dbc.CardHeader(f.id), dbc.CardBody(f)]) for f in source_forms]
        form_tabs = cards

    return form_tabs


def edit_output_form(output_form, data_dict):

    for k, v in output_form.items():
        if isinstance(v, dict) and 'path' not in v:
            edit_output_form(v, data_dict)
        else:
            if isinstance(v, dict):
                v['path'] = data_dict[k]
            else:
                output_form[k] = data_dict[k]

    return output_form
