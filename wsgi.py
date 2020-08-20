from nwb_web_gui import dash_app


if __name__ == '__main__':
    dash_app.server.run(host='0.0.0.0', port=8050, debug=True)
