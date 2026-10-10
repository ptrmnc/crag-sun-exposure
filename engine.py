import pandas as pd
import pvlib
import datetime as dt
import numpy as np
from tzfpy import get_tz
import argparse

def is_sun_on_wall(sun_azimuth, sun_zenith, wall_aspect):
# This functions takes three numbers as inputs and returns a boolean.
# The inputs are the sun azimuth, the sun zhenith and the wall aspect.
# The output is True if the sun azimuth is within 90° form the wall aspect and the sun zenith is grather then 0,
# meaning that the sun is up and the wall is hit by sun,
# it is False otherwise.

# Now we compute the angular distance between the wall aspect and the sun azimuth.
# We want this distance to be included in [0,180], ingnoring the relative positions of the two angles.
# To do that we subtract the sun azimuth from the wall aspect, we then teporarly add 180, we take the modulo 360
# and we subtract back 180, so that we have an angle equivalent to the difference of the two but included in [-180,180].
# We than take the absolute value of that angle and we check if it is less then 90.
    angular_distance = abs((wall_aspect - sun_azimuth + 180)%360-180)

# If it is the angles are less the 90° apart and the sun is up, it will hit the wall. (assuming a vertical wall)
    if angular_distance<90 and sun_zenith<90:
        return(True)
    else: return(False)

def sun_exposure(lon, lat, date, wall_aspect):
    # This function gets as inputs a position (longitude and latitude), a date and a wall aspect.
    # It returnes a tuple where the firt argument is the time the wall gets in the sun and the second argument is 
    # the time the wall gets in the shade.

    # Firts from the date we construct a pd dataframe containing all the times of that specific day.
    # The timezone is obtained with a specific library.
    startTime = date
    endTime = date + pd.Timedelta(days=1)
    timezone = get_tz(lon, lat)
    timesDf = pd.date_range(
        startTime,
        endTime,
        freq="1min",
        tz=timezone,
        inclusive="left"
        )
    
    # Now that we have our times we contruct via pclib the dataframe of solar positions.
    SolarPositionsDf = pvlib.solarposition.get_solarposition(
        time = timesDf,
        latitude = lat,
        longitude = lon
        )

    # We then build via apply a new column of our dataframe of boolean values: True if the sun hits our wall,
    # False if it dose not.
    SolarPositionsDf["is_sun_on_wall"]=SolarPositionsDf.apply(
        lambda row:is_sun_on_wall(row["azimuth"], row["zenith"], wall_aspect),
        axis=1
    )

    # Now we filter out all the indexes for witch the value of our new column is false.
    TimesOfExposition = SolarPositionsDf.index[SolarPositionsDf['is_sun_on_wall'] == True]

    # Then we return the first and last indexes, those are the time in witch the wall gets the in the sun
    # and the time in witch the wall gets in the shade.
    if not TimesOfExposition.empty:
        return( [TimesOfExposition[0], TimesOfExposition[-1]])
    else: return([])


# Now we make the code runnable from comand line.
# We want this to be done only if the code is executed directly, so we add the flollowing guard.
if __name__ == "__main__":

# We inizialize the parser.
    parser = argparse.ArgumentParser(
        description="Calculates when the wall gets in the sun and when it gets in the shade"
        )
# We add the arguments: date, longitude, latitude, wall_aspect
    parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="The latitude of the crag"
        )
    
    parser.add_argument(
        "--lon",
        type=float,
        required=True,
        help="The longitude of the crag"
        )
    
    parser.add_argument(
        "--date",
        type=str,
        required=True,
        help="The day you want to go to the crag (in YYYY-MM-DD format)"
        )
    
    parser.add_argument(
        "--aspect",
        type=float,
        required=True,
        help="The aspect of the crag"
        )
    
    # Now we make the arguments reachable
    args = parser.parse_args()

    # Then we compute the exposure of the crag and we print it
    date = pd.to_datetime(args.date)
    results = sun_exposure(args.lon, args.lat, date, args.aspect)
    if results:
        print(f"Sun hits wall: {results[0].strftime('%H:%M')} -> {results[1].strftime('%H:%M')} ({results[0].tz})")
    else:
        print("No direct sunlight on the wall for this date.")