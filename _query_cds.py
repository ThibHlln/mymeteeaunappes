from mycds.store import save_meteorology


working_dir = 'examples/my-example'

save_meteorology(
    latitude=50.3, longitude=2.2, working_dir=working_dir,
    update_era5_land=True
)
