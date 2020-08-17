import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash


class Home(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        
        self.parent_app = parent_app

        self.children = [
            html.H1('Home', className='header')
        ]

        