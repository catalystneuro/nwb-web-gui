from . import init_app
from pathlib import Path
from threading import Timer
import webbrowser
import os


def parse_arguments():
    """
    Command line shortcut to open GUI editor.
    Usage:
    $ nwb-web-gui [--converter] [--data_path] [--port] [--dev] [--render_dashboard] [--render_viewer] [--render_converter]

    converter : str
        Optional.
        The name of the specfic converter module to be used.
        If not specified will be used example converter
    data_path : str
        Optional. Base path to experimental data.
    port : int
        Optional. Port where app will be running.
    render_dashboard : bool
        Optional. Render dashboard page
    render_viewer : bool
        Optional. Render viewer page
    render_converter : bool
        Optional. Render converter page
    ci : bool
        Optional. Use for Continuous Integration testing only.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='NWB WEB GUI,',
    )

    parser.add_argument(
        "--converter",
        default='example',
        help="Converter module name to be used"
    )
    parser.add_argument(
        "--data_path",
        default='.',
        help="Path to datasets. Defaults to current working directory."
    )
    parser.add_argument(
        "--port",
        default='5000',
        help="Port where app will be running. Defaults to 5000."
    )
    parser.add_argument(
        "--dev",
        default=False,
        help="Run in development mode. Defaults to False."
    )
    parser.add_argument(
        "--render_dashboard",
        default='False',
        help="Render dashboard page"
    )
    parser.add_argument(
        "--render_viewer",
        default='False',
        help="Render viewer page"
    )
    parser.add_argument(
        "--render_converter",
        default='True',
        help="Render coverter page"
    )

    # Parse arguments
    args = parser.parse_args()

    return args


def cmd_line_shortcut():
    run_args = parse_arguments()

    # Set ENV variables for app
    data_path = str(Path(run_args.data_path))
    render_converter = run_args.render_converter
    render_viewer = run_args.render_viewer
    render_dashboard = run_args.render_dashboard
    converter = run_args.converter

    os.environ['FLASK_ENV'] = 'production'
    os.environ['NWB_GUI_ROOT_PATH'] = data_path
    os.environ['NWB_GUI_RENDER_CONVERTER'] = render_converter
    os.environ['NWB_GUI_RENDER_VIEWER'] = render_viewer
    os.environ['NWB_GUI_RENDER_DASHBOARD'] = render_dashboard

    # Choose converter
    os.environ['NWB_GUI_CONVERTER_MODULE'] = converter
    if converter == 'example':
        os.environ['NWB_GUI_CONVERTER_CLASS'] = converter

    print(f'NWB GUI running on localhost:{run_args.port}')
    print(f'Data path: {str(Path(data_path).resolve())}')
    if run_args.dev:
        os.environ['FLASK_ENV'] = 'development'
        print('Running in development mode')

    # Initialize app
    app = init_app()

    # Open browser after 1 sec
    def open_browser():
        webbrowser.open_new(f'http://localhost:{run_args.port}/')

    Timer(1, open_browser).start()

    # Run app
    app.run(
        host='0.0.0.0',
        port=run_args.port,
        debug=run_args.dev,
        use_reloader=run_args.dev
    )
