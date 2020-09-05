## Definitions

A **Form** is a [Card component](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/card/) that has as children a list of **Fields**.

A **Field** is a [FormGroup component](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/form/) that has two children in the same row: Label and Input.

Labels are strings with values corresponding to the properties names of pynwb classes. The Input of each **Field** varies according to the type of data for each property. The Input type must be defined in the incoming schema and the Input value should be provided by the data.



### String field

<table>
<tr>
<td>Schema</td>
<td>Data</td>
</tr>
<tr>
<td>
<pre lang="json">
"NWBFile": {
  "properties": {
    "identifier": {
        "type": "string"
    }
  }
}
</pre>
</td>
<td>
<pre lang="json">
"NWBFile": {
	"identifier": "ADDME"
}
</pre>
</td>
</tr>
</table>

![](nwb_web_gui/static/documentation_singlestring.JPG)


### Numeric field

<table>
<tr>
<td>Schema</td>
<td>Data</td>
</tr>
<tr>
<td>
<pre lang="json">
"ImagingPlane": {
  "properties": {
    "excitation_lambda": {
  	  "type": "number"
  }
}
</pre>
</td>
<td>
<pre lang="json">
"ImagingPlane": {
  "excitation_lambda": 588
}
</pre>
</td>
</tr>
</table>

![](nwb_web_gui/static/documentation_numeric.JPG)


### Datetime field

<table>
<tr>
<td>Schema</td>
<td>Data</td>
</tr>
<tr>
<td>
<pre lang="json">
"NWBFile": {
  "properties": {
    "session_start_time": {
      "type": "string",
      "format": "date-time"
    }
  }
}
</pre>
</td>
<td>
<pre lang="json">
"NWBFile": {
	"session_start_time": "1900-01-01T00:00:00"
}
</pre>
</td>
</tr>
</table>

![](nwb_web_gui/static/documentation_datetime.JPG)


### Tags field

<table>
<tr>
<td>Schema</td>
<td>Data</td>
</tr>
<tr>
<td>
<pre lang="json">
"NWBFile": {
  "properties": {
    "experimenter": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
</pre>
</td>
<td>
<pre lang="json">
"NWBFile": {
	"experimenter": ["Name 1", "Name 2"]
}
</pre>
</td>
</tr>
</table>

![](nwb_web_gui/static/documentation_tags.JPG)


### String choice field

<table>
<tr>
<td>Schema</td>
<td>Data</td>
</tr>
<tr>
<td>
<pre lang="json">
"Subject": {
  "properties": {
    "sex": {
      "type": "string",
      "enum": ["M", "F", "U", "O"],
      "default": "U"
    }
  }
}
</pre>
</td>
<td>
<pre lang="json">
"Subject": {
  "sex": "M"
}
</pre>
</td>
</tr>
</table>

![](nwb_web_gui/static/documentation_stringchoice.JPG)


### Link choice field

<table>
<tr>
<td>Schema</td>
<td>Data</td>
</tr>
<tr>
<td>
<pre lang="json">
"ImagingPlane": {
  "properties": {
    "device": {
      "type": "string",
      "enum": []
    }
  }
}
</pre>
</td>
<td>
<pre lang="json">
"ImagingPlane": {
  "device": "device_name"
}
</pre>
</td>
</tr>
</table>
