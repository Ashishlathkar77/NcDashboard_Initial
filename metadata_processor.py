import xarray as xr

def process_file(file_path, regex=''):
    try:
        dataset = xr.open_dataset(file_path, engine='netcdf4')
        metadata = {
            'variables': list(dataset.data_vars.keys()),
            'dimensions': list(dataset.dims.keys()),
            'attributes': dataset.attrs
        }
        return metadata
    except Exception as e:
        return {'error': str(e)}
