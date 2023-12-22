from mycds.collect import update_era5_database
from mycds.store import (
    save_total_precipitation, save_potential_evaporation,
    save_2m_air_temperature
)


working_dir = 'examples/my-example'

update_era5_database()

save_total_precipitation(
    latitude=50.3, longitude=2.2, working_dir=working_dir
)

save_potential_evaporation(
    latitude=50.3, longitude=2.2, working_dir=working_dir
)

save_2m_air_temperature(
    latitude=50.3, longitude=2.2, working_dir=working_dir
)
