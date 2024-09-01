import dash
from dash import dcc, html, ctx, Input, Output, State, ALL, callback, Patch
import logging
import numpy as np
from model.TreeNode import PlotType
from model.model_utils import print_tree
from dash.exceptions import PreventUpdate
from model.dashboard import Dashboard
import dash_bootstrap_components as dbc
from metadata_processor import process_file
from prompt_generator import generate_prompt

class NcDashboard:
    def __init__(self, file_paths, regex, host='127.0.0.1', port=8050):
        self.host = host
        self.port = port
        self.path = file_paths
        self.regex = regex
        self.ncdash = Dashboard(file_paths, regex)
        
        self.app = dash.Dash(__name__, external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.5.0/font/bootstrap-icons.min.css"
        ], suppress_callback_exceptions=True)
        self.app.title = "NcDashboard"
        
        self.setup_layout()
        self.setup_callbacks()

        logging.info('Starting NcDashboard...')

    def start(self):
        self.app.run_server(debug=False, port=self.port, host=self.host)

    def setup_layout(self):
        self.app.layout = dbc.Container(
            [
                dcc.Input(id='file-path', type='text', placeholder='Enter NetCDF file path'),
                dbc.Button("Process File", id="process-file-button", color="primary"),
                dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="circle"),
                html.Div(id='metadata-output'),
                dcc.Store(id='window-size'),
                html.Div(id='output-div'),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1("NcDashboard", style={"textAlign": "center"}),
                            ],
                            width={"size": 6, "offset": 3},
                        )
                    ]
                ),
                dbc.Row(
                    self.initial_menu(),
                    id="start_menu"
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [ 
                                dbc.Button("Plot selected fields", id="but_plot_all", color="success", size='lg'),
                                dcc.Download(id="download-data"),
                                dcc.Loading(
                                    id="loading-1",
                                    children=[html.Div(id="loading-output-1")],
                                    type="circle",
                                ),
                            ], width={"size": 6, "offset": 4}),
                    ]
                ),
                dbc.Row([], id="display_area"),
            ],
            fluid=True,
            id="container",
        )

    def setup_callbacks(self):
        @self.app.callback(
            Output('metadata-output', 'children'),
            Output('loading-output-1', 'children'),
            Input('process-file-button', 'n_clicks'),
            State('file-path', 'value')
        )
        def process_and_generate_prompt(n_clicks, file_path):
            if not n_clicks:
                raise PreventUpdate

            if not file_path:
                return html.Div("Please provide a NetCDF file path."), ""

            # Process NetCDF file
            metadata = process_file(file_path)

            # Check if processing was successful
            if 'error' in metadata:
                return html.Div(f"Error processing file: {metadata['error']}"), ""

            # Generate prompt
            prompt = generate_prompt(metadata)

            # Return generated prompt
            return html.Pre(prompt), ""

        @self.app.callback(
            Output("start_menu", "children"),
            Input("but_plot_all", "n_clicks"),
        )
        def clear_selected(n_clicks):
            return self.initial_menu()

        @self.app.callback(
            Output("display_area", "children"),
            Output("loading-output-1", "children"),
            State("display_area", "children"),
            State("1D_vars", "value"),
            State("2D_vars", "value"),
            State("3D_vars", "value"),
            State("4D_vars", "value"),
            Input("but_plot_all", "n_clicks"),
            State({"type": "click_data_identifier", "index": ALL}, 'children'),
            Input({"type": "animation", "index": ALL}, "n_clicks"),
            Input({"type": "resolution", "index": ALL}, "value"),
            Input({"type": "close_figure", "index": ALL}, "n_clicks"),
            Input({"type": "download_data", "index": ALL}, "n_clicks"),
            Input({"type": "figure", "index":ALL}, 'clickData'),
            Input({"type": "figure", "index":ALL}, 'relayoutData'),
            Input({"type": "first_frame", "index":ALL}, 'n_clicks'),
            Input({"type": "prev_frame", "index":ALL}, 'n_clicks'),
            Input({"type": "next_frame", "index":ALL}, 'n_clicks'),
            Input({"type": "last_frame", "index":ALL}, 'n_clicks'),
            Input('window-size', 'data')
        )
        def display_relayout_data(prev_children, selected_1d, selected_2d, selected_3d, selected_4d, 
                                n_clicks_plot_separated, click_data_identifiers,
                                n_clicks_requestanimation, resolution_list, close_list, download_list,
                                click_data_list, selected_data_list,
                                    n_clicks_first_frame, n_clicks_prev_frame, n_clicks_next_frame, n_clicks_last_frame,
                                    window_size):
            # TODO we need to be able to separate this function, at least to call methods somewhere else 
            window_ratio = 0.8
            if window_size is None:
                print("Window size information is not available.")
            else:
                width = window_size.get('width', 'Unknown')
                height = window_size.get('height', 'Unknown')
                window_ratio = width/height
                # print width, height
                print(f"Window Width: {width}, Window Height: {height}")

            triggered_id = ctx.triggered_id
            print(f'Type: {type(triggered_id)}, Value: {triggered_id}')

            print(f'1D: {selected_1d}, 2D: {selected_2d}, 3D: {selected_3d}, 4D: {selected_4d}')
            # Check the one triggered was but_plot_all

            patch = Patch()
            plot_types = [PlotType.OneD, PlotType.TwoD, PlotType.ThreeD, PlotType.FourD]
                    
            # Initial case, do nothing
            if triggered_id is None:
                return [], []

            # First level plots, directly from the menu
            elif triggered_id == 'but_plot_all':
                for i, selected in enumerate([selected_1d, selected_2d, selected_3d, selected_4d]):
                    if selected is not None and len(selected) > 0:
                        for c_field in selected:
                            new_figure = self.ncdash.create_default_figure(c_field, plot_types[i])
                            patch.append(new_figure)

            # Closing a plot
            elif isinstance(triggered_id, dash._utils.AttributeDict) and triggered_id['type'] == 'close_figure': # type: ignore
                node_id = triggered_id['index']
                patch = self.ncdash.close_figure(node_id, prev_children, patch)

            elif isinstance(triggered_id, dash._utils.AttributeDict) and triggered_id['type'] == 'download_data': # type: ignore
                node_id = triggered_id['index']
                # patch = self.ncdash.close_figure(node_id, prev_children, patch)
                if ctx.triggered[0]['prop_id'].find('relayoutData') != -1:
                    print(f'Selected data: {selected_data_list}')

            # Next frame
            elif isinstance(triggered_id, dash._utils.AttributeDict) and (
                triggered_id['type'] in ['next_frame', 'prev_frame', 'first_frame', 'last_frame']
            ): # type: ignore
                index = triggered_id['index'].split(":")
                coord = index[0]
                node_id = index[1]
                node = self.ncdash.tree_root.locate(node_id)

                coords = node.get_animation_coords()

                coord_index = coords.index(coord)

                if triggered_id['type'] == 'next_frame':
                    if coord_index == 0: # For 4D first index 
                        node.next_time()
                    if coord_index == 1 and node.get_plot_type() == PlotType.FourD: # For 4D first index 
                        node.next_depth()
                elif triggered_id['type'] == 'prev_frame':
                    if coord_index == 0:
                        node.prev_time()
                    if coord_index == 1 and node.get_plot_type() == PlotType.FourD: # For 4D first index
                        node.prev_depth()
                elif triggered_id['type'] == 'first_frame':
                    if coord_index == 0:
                        node.set_time_idx(0)
                    if coord_index == 1:
                        node.set_depth_idx(0)
                elif triggered_id['type'] == 'last_frame':
                    if coord_index == 0:
                        node.set_time_idx(node.get_max_time_index())
                    if coord_index == 1:
                        node.set_depth_idx(node.get_max_depth_index())

                patch.append(node.get_animation_figure())

            return patch.get_elements(), "Processing..."
    
    def initial_menu(self):
        return [
            dbc.Row(
                [
                    dbc.Col(
                        [html.H4("1D Variables")],
                        width={"size": 6},
                    ),
                    dbc.Col(
                        [html.H4("2D Variables")],
                        width={"size": 6},
                    ),
                ],
                justify="between",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="1D_vars",
                            options=[{"label": "Variable 1D", "value": "1D_var"}],
                            multi=True,
                            placeholder="Select 1D Variables"
                        ),
                        width={"size": 6},
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="2D_vars",
                            options=[{"label": "Variable 2D", "value": "2D_var"}],
                            multi=True,
                            placeholder="Select 2D Variables"
                        ),
                        width={"size": 6},
                    ),
                ],
                justify="between",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="3D_vars",
                            options=[{"label": "Variable 3D", "value": "3D_var"}],
                            multi=True,
                            placeholder="Select 3D Variables"
                        ),
                        width={"size": 6},
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="4D_vars",
                            options=[{"label": "Variable 4D", "value": "4D_var"}],
                            multi=True,
                            placeholder="Select 4D Variables"
                        ),
                        width={"size": 6},
                    ),
                ],
                justify="between",
            ),
        ]

if __name__ == '__main__':
    # Example usage
    file_paths = ['/path/to/file.nc']
    regex = 'some_regex'
    dashboard = NcDashboard(file_paths, regex)
    dashboard.start()
