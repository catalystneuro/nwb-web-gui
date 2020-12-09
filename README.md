# NWB Web GUI

[![PyPI version](https://badge.fury.io/py/nwb-web-gui.svg)](https://badge.fury.io/py/nwb-web-gui)

Web graphical user interface for NWB conversion and visualization.

## 1. Installation
From PyPI:
```
$ pip install nwb-web-gui
```

From a local copy of the repository:
```
$ git clone https://github.com/catalystneuro/nwb-web-gui.git
$ cd nwb-web-gui
$ pip install .
```

## 2. Running

From command line shortcut:
```
$ nwbgui
```

From repository local copy:
```
$ python wsgi.py
```

NWB Web GUI by default runs on `localhost:5000`.

## 3. Running on docker container (referencing a local folder)

- Change on config.ini file the NWB_GUI_ROOT_PATH to /usr/src/nwb_web_gui/files  
- build docker with:
```
$ docker build -t latest .
```
- run the docker with:
```
$ docker run -it -p 5000:5000 -p 8866:8866 -v /host/path/to/filesFolder:/usr/src/nwb_web_gui/files <image_id>
```

## 4. Run NWB Web GUI for a specific NWB Converter
NWB Web GUI can be set to run with any specific NWB converter:

```python
from nwb_web_gui import init_app
import os


# Set ENV variables for app
# Set root path from where to run the GUI
data_path = '/source_path'
os.environ['NWB_GUI_ROOT_PATH'] = data_path

# Set which NWB GUI pages should be displayed
os.environ['NWB_GUI_RENDER_CONVERTER'] = 'True'
os.environ['NWB_GUI_RENDER_VIEWER'] = 'True'
os.environ['NWB_GUI_RENDER_DASHBOARD'] = 'False'

# Choose NWB converter to be used
os.environ['NWB_GUI_NWB_CONVERTER_MODULE'] = 'my_lab_to_nwb'
os.environ['NWB_GUI_NWB_CONVERTER_CLASS'] = 'MylabNWBConverter'

# Choose port where the GUI will run. Default is 5000
port = 5000

print(f'NWB GUI running on localhost:{port}')
print(f'Data path: {data_path}')

# Initialize app
app = init_app()

# Run app
app.run(
    host='0.0.0.0',
    port=port,
    debug=False,
    use_reloader=False
)
```

## 5. Documentation

[Documentation](https://github.com/catalystneuro/nwb-web-gui/tree/master/documentation)
