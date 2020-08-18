import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from pathlib import Path
import json
from .converter_classes import SingleForm, CompositeForm


def iter_metadata(metadata_json, default_schema, parent_app, parent_name=None, forms = []):

    for k, v in metadata_json.items():
        if k in default_schema.keys():
            if k in ['NWBFile', 'Subject']:
                form = SingleForm(v, default_schema[k], parent_app, k)
                forms.append(form)
            else:
                form = CompositeForm(v, k, default_schema[k], parent_app, parent_name)
                forms.append(form)
        else:
            iter_metadata(v, default_schema, parent_app, parent_name=k, forms=forms)

    return forms


def get_form_from_metadata(metadata_json, parent_app):

    default_schema_path = Path.cwd() / 'apps' / 'uploads' / 'metadata' / 'schema_catalog_reduced.json'

    with open(default_schema_path, 'r') as inp:
        default_schema = json.load(inp)

    forms = iter_metadata(metadata_json, default_schema, parent_app, forms=[])

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
