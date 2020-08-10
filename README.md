# NWB Web GUI

Web graphical user interface for NWB

Developed using a Flask API backend and React Frontend

## 1. Installation 

### Backend
Inside backend folder run:
```
pip install -r requirements.txt
```

### Frontend
Inside frontend folder run:
```
npm install
//or
yarn install
```

## 2. Running
### Backend
```
python wsgi.py
```  
### Frotnend
```
npm start
//or
yarn start
```


## 3. Usage

* Input Metadata: JSON Schema for basic inputs form fields  
You can find a template [here](https://github.com/Tauffer-Consulting/nwb-web-gui/blob/master/inputsSchema.json)  
  
* Metadata: JSON Schema for NWB form fields  
You can find a template [here](https://github.com/Tauffer-Consulting/nwb-web-gui/blob/master/metadataSchema.json)  

#### Usage Steps:
##### Metadata/Conversion
1. Load metadata and submit to load forms on frontend
2. Fill forms and submit to save with new data

##### NWB Explorer
1. Pass NWB file path and submit to render Widgets

##### Custom Dashboards
todo

#### Usage example GIF
![Gif Example](https://github.com/Tauffer-Consulting/nwb-web-gui/blob/master/usage.gif?raw=true)
