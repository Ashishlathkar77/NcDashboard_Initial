"""NcDashboard Options

Usage:
  ncdashboard.py <path> [--regex <regex>] [--port <port>] [--host <host>]
  ncdashboard.py (-h | --help)
  ncdashboard.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  <path>        NetCDF file or regular expression to explore.
  --regex <regex>  Optional regular expression for file matching.
  --port <port>   Optional port number for the Dash app.
  --host <host>   Optional host address for the Dash app.
"""
import logging
from docopt import docopt
from controller import NcDashboard

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

if __name__ == "__main__":
    args = docopt(__doc__, version='NcDashboard 0.0.1')
    print(args)
    
    path = args['<path>']
    regex = args.get('--regex', '')  # Use get() to handle missing optional arguments
    port = args.get('--port')  # Use get() to handle missing optional arguments
    host = args.get('--host')  # Use get() to handle missing optional arguments
    
    if port:
        port = int(port)
    else:
        port = 8050

    if not host:
        host = '127.0.0.1'

    ncdashboard = NcDashboard(path, regex, port=port, host=host)
    ncdashboard.start()
