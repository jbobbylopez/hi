import subprocess
import datetime
import requests
import json
import os
import time

CACHE_FILE = '/tmp/ubuntu_eol_cache.json'
CACHE_DURATION = 7 * 24 * 60 * 60  # One week in seconds

def get_ubuntu_version():
    ''' Retrieves the current Ubuntu version '''
    result = subprocess.run(['lsb_release', '-si', '-sr'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip().split()
    return output[0], output[1]  # Returns OS name and version

def fetch_eol_dates(url):
    ''' Fetches the EOL dates data from the endoflife.date API '''
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the response is not OK
    data = response.json()
    return data

def get_eol_dates(url):
    ''' Gets the EOL dates data, using a cache to avoid frequent requests '''
    if os.path.exists(CACHE_FILE):
        cache_mtime = os.path.getmtime(CACHE_FILE)
        current_time = time.time()
        if current_time - cache_mtime < CACHE_DURATION:
            # Cache is still valid, read from cache
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    
    # Cache is outdated or doesn't exist, fetch new data
    data = fetch_eol_dates(url)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)
    return data

def calculate_time_until_eol(eol_date):
    ''' Calculates the time remaining until EOL in years, months, weeks, and days '''
    eol_date = datetime.datetime.strptime(eol_date, '%Y-%m-%d')
    current_date = datetime.datetime.now()
    delta = eol_date - current_date

    years = delta.days // 365
    months = (delta.days % 365) // 30
    weeks = (delta.days % 365 % 30) // 7
    days = delta.days % 365 % 30 % 7

    return years, months, weeks, days

def main():
    os_name, version = get_ubuntu_version()
    url = 'https://endoflife.date/api/ubuntu.json'

    try:
        data = get_eol_dates(url)

        # Find the version's EOL date in the JSON data
        eol_date = None
        for entry in data:
            if entry['cycle'] == version:
                eol_date = entry['eol']
                break

        if eol_date:
            years, months, weeks, days = calculate_time_until_eol(eol_date)
            print(f"Operating System: {os_name} {version} | End of Life: {eol_date} ({years} years, {months} months, {weeks} weeks, and {days} days remaining)")
        else:
            print(f"End of Life date not found for {os_name} version {version}.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the EOL data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
