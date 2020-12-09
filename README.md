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

- Change on config.ini file the DATA_PATH to /usr/src/nwb_web_gui/files  
- build docker with:
```
$ docker build -t latest .
```
- run the docker with:
```
$ docker run -it -p 5000:5000 -p 8866:8866 -v /host/path/to/filesFolder:/usr/src/nwb_web_gui/files <image_id>
```


## 3. Documentation

[Documentation](https://github.com/catalystneuro/nwb-web-gui/tree/master/documentation)
