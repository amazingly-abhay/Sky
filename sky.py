import numpy as np
from astropy.coordinates import SkyCoord, AltAz, get_sun, get_moon, EarthLocation
from astropy.time import Time
from astropy import units as u
import datetime
import sys
import math

def get_user_location():
    try:
        lat = float(input("Enter your latitude (e.g., 51.4769 for Greenwich): "))
        lon = float(input("Enter your longitude (e.g., -0.0005 for Greenwich): "))
        return EarthLocation(lat=lat*u.deg, lon=lon*u.deg)
    except ValueError:
        print("Invalid input. Using default location: Greenwich Observatory.")
        return EarthLocation(lat=51.4769*u.deg, lon=-0.0005*u.deg)

def get_user_datetime():
    user_input = input("Enter date and time in YYYY-MM-DD HH:MM format (leave blank for current time): ")
    if user_input.strip() == '':
        return Time.now()
    try:
        dt = datetime.datetime.strptime(user_input, "%Y-%m-%d %H:%M")
        return Time(dt)
    except ValueError:
        print("Invalid date/time format. Using current time.")
        return Time.now()

def generate_star_map(grid_size=50, save_to_file=False, color_output=True):
    location = get_user_location()
    observing_time = get_user_datetime()
    
    # Sample star catalog (can be expanded or replaced with real catalogs)
    star_data = [
        {"name": "Sirius", "ra": "06h45m08.917s", "dec": "-16d42m58.02s"},
        {"name": "Betelgeuse", "ra": "05h55m10.3053s", "dec": "07d24m25.430s"},
        {"name": "Rigel", "ra": "05h14m32.27210s", "dec": "-08d12m05.8981s"},
        {"name": "Vega", "ra": "18h36m56.33635s", "dec": "38d47m01.2802s"},
        {"name": "Altair", "ra": "19h50m47.00483s", "dec": "08d52m05.9566s"},
        {"name": "Polaris", "ra": "02h31m49.09456s", "dec": "89d15m50.7923s"},
        {"name": "Capella", "ra": "05h16m41.3587s", "dec": "45d59m52.768s"},
        {"name": "Aldebaran", "ra": "04h35m55.239s", "dec": "16d30m33.49s"},
        {"name": "Antares", "ra": "16h29m24.45970s", "dec": "-26d25m55.2094s"},
        {"name": "Spica", "ra": "13h25m11.579s", "dec": "-11d09m40.75s"},
        {"name": "Procyon", "ra": "07h39m18.1195s", "dec": "05d13m29.955s"},
        {"name": "Deneb", "ra": "20h41m25.91513s", "dec": "45d16m49.2197s"},
        {"name": "Canopus", "ra": "06h23m57.10988s", "dec": "-52d41m44.3810s"},
        {"name": "Arcturus", "ra": "14h15m39.67207s", "dec": "19d10m56.673s"},
        {"name": "Regulus", "ra": "10h08m22.3110s", "dec": "11d58m01.95s"}
    ]
    
    # Add Sun and Moon positions
    sun = get_sun(observing_time).transform_to(AltAz(obstime=observing_time, location=location))
    moon = get_moon(observing_time).transform_to(AltAz(obstime=observing_time, location=location))
    
    objects = []
    for star in star_data:
        coord = SkyCoord(ra=star['ra'], dec=star['dec'])
        altaz = coord.transform_to(AltAz(obstime=observing_time, location=location))
        if altaz.alt.deg > 0:
            objects.append({
                "name": star['name'],
                "az": altaz.az.deg,
                "alt": altaz.alt.deg,
                "symbol": '✦'
            })
    # Add Sun and Moon if above horizon
    if sun.alt.deg > -18:  # Sunlight can affect visibility even below horizon
        objects.append({
            "name": "Sun",
            "az": sun.az.deg,
            "alt": sun.alt.deg,
            "symbol": '🌞'
        })
    if moon.alt.deg > 0:
        objects.append({
            "name": "Moon",
            "az": moon.az.deg,
            "alt": moon.alt.deg,
            "symbol": '🌕'
        })
    
    # Initialize empty grid
    sky = np.full((grid_size, grid_size), ' ')
    
    for obj in objects:
        # Convert azimuth and altitude to x, y coordinates
        az_rad = math.radians(obj['az'])
        alt_rad = math.radians(obj['alt'])
        
        # Polar to Cartesian conversion
        r = (90 - obj['alt']) / 90 * (grid_size / 2)
        x = grid_size / 2 + r * math.sin(az_rad)
        y = grid_size / 2 - r * math.cos(az_rad)
        
        x = int(round(x))
        y = int(round(y))
        
        if 0 <= x < grid_size and 0 <= y < grid_size:
            sky[y, x] = obj['symbol']
    
    # Prepare the sky map as string
    border = '+' + '-' * grid_size + '+'
    sky_rows = [border]
    for row in sky:
        sky_rows.append('|' + ''.join(row) + '|')
    sky_rows.append(border)
    
    sky_map = '\n'.join(sky_rows)
    
    # Add color if enabled and terminal supports it
    if color_output and sys.stdout.isatty():
        sky_map = sky_map.replace('*', '\033[93m*\033[0m')  # Yellow stars
        sky_map = sky_map.replace('☼', '\033[91m☼\033[0m')  # Red sun
        sky_map = sky_map.replace('◑', '\033[96m◑\033[0m')  # Cyan moon
    
    # Print the sky map
    print("\nStar Map:")
    print(f"Location: {location.lat.deg:.4f}° N, {location.lon.deg:.4f}° E")
    print(f"Date and Time (UTC): {observing_time.utc.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(sky_map)
    
    # Print legend
    print("\nVisible Objects:")
    for obj in objects:
        print(f"- {obj['name']} at Azimuth: {obj['az']:.2f}°, Altitude: {obj['alt']:.2f}°")
    
    # Save to file if requested
    if save_to_file:
        filename = f"star_map_{observing_time.utc.datetime.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as file:
            file.write("\\033[1mStar Map:\\033[0m\n")
            file.write(f"Location: {location.lat.deg:.4f}° N, {location.lon.deg:.4f}° E\n")
            file.write(f"Date and Time (UTC): {observing_time.utc.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write(sky_map + '\n\n')
            file.write("Visible Objects:\n")
            for obj in objects:
                file.write(f"- {obj['name']} at Azimuth: {obj['az']:.2f}°, Altitude: {obj['alt']:.2f}°\n")
        print(f"\nStar map saved to {filename}")

if __name__ == "__main__":
    try:
        grid_input = input("Enter grid size (recommended between 20 and 100, default 50): ")
        grid_size = int(grid_input) if grid_input.strip() != '' else 50
        save_input = input("Do you want to save the star map to a file? (y/n, default n): ").strip().lower()
        color_input = input("Do you want colored output? (y/n, default y): ").strip().lower()
        save_to_file = save_input == 'y'
        color_output = color_input != 'n'
        generate_star_map(grid_size=grid_size, save_to_file=save_to_file, color_output=color_output)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
