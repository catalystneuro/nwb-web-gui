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

map_input_form_schema = {
    "source_data": {
        "required": [],
        "type": "object",
        "additionalProperties": True,
        "title": "Source data",
        "description": "Source data to be converted",
        "properties": {}
    },
    "conversion_options": {
        "required": [],
        "type": "object",
        "additionalProperties": True,
        "title": "Conversion options",
        "description": "Conversion options",
        "properties": {}
    }
}


def get_inputs_additional_properties(value, base_schema, item_name):

    for k, v in value.items():
        if isinstance(v, str):
            v_type = 'string'
        elif isinstance(v, bool):
            v_type = 'boolean'
        base_schema['properties'][k] = {'type': v_type, 'default': v}

    schema = {item_name: base_schema}
    return schema


def iter_metadata(metadata_json, parent_app, parent_name=None, forms=[], inputs_forms=[]):

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
        elif k in map_input_form_schema.keys():
            item_schema = map_input_form_schema[k]
            schema = get_inputs_additional_properties(v, item_schema, k)
            form = SingleForm(
                value=v,
                base_schema=schema[k],
                parent_app=parent_app,
                item_name=map_input_form_schema[k]['title'])
            inputs_forms.append(form)
        else:
            iter_metadata(v, parent_app, parent_name=k, forms=forms, inputs_forms=inputs_forms)

    return forms, inputs_forms


def get_form_from_metadata(metadata_json, parent_app):
    """"""
    forms, inputs_forms = iter_metadata(metadata_json, parent_app, forms=[], inputs_forms=[])

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
        tabs = [dbc.Tab(f, label=f.id, tab_style={'background-color': '#f7f7f7', 'border':'solid', 'border-color': '#f7f7f7', 'border-width': '1px'}) for f in inputs_forms]
        form_tabs = dbc.Tabs(tabs)
        cards = [dbc.Card([dbc.CardHeader(f.id), dbc.CardBody(f)]) for f in inputs_forms]
        form_tabs = cards

    return form_tabs
