from netcdf_parser import parse_netcdf
from prompt_generator import generate_prompt

def main():
    file_path = '/workspaces/NcDashboard_Initial/test_data/gom_t007.nc'
    metadata = parse_netcdf(file_path)
    print(metadata)

    user_query = "generate the vorticity field"
    prompt = generate_prompt(user_query, metadata)
    print(prompt)

if __name__ == "__main__":
    main()
