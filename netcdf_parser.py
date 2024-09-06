import xarray as xr

def parse_netcdf(file_path):
    # Load netCDF data using xarray without decoding time units
    ds = xr.open_dataset(file_path, decode_times=False)
    
    # Extract metadata
    variables = {}
    for var in ds.data_vars:
        variables[var] = {
            'dims': ds[var].dims,
            'shape': ds[var].shape,
            'units': ds[var].attrs.get('units', 'unknown')
        }

    return variables