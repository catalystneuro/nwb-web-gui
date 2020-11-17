# NWB Web GUI

Web graphical user interface for NWB conversion and visualization.

## 1. Installation
```
pip install -e .
```

## 2. Running
```
python wsgi.py
```

The app should be running on `localhost:5000`

## 3. Running on docker container (referencing a local folder)

- Change on config.ini file the DATA_PATH to /usr/src/nwb_web_gui/files  
- build docker with:
```
docker build -t latest . 
```
- run the docker with:
```
docker run -it -p 5000:5000 -p 8866:8866 -v /host/path/to/filesFolder:/usr/src/nwb_web_gui/files <image_id>
```


## 3. Documentation

[Documentation](https://github.com/catalystneuro/nwb-web-gui/tree/master/documentation)
