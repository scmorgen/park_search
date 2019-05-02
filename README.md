## park_search

This is a python script which attempts to search all the local california sites for available campsites.
It saves those results into an availability_X.txt

It makes no attempt to book sites or be super fast. Use another script for that. 
I just wanted something to easily screen out the ADA sites on California and combine National parks with State Parks.
ReserveCalifornia is especially likely to change so you might find this breaks quickly.

### Dependencies
* OS X or *nix variant
* Python (2.7 and 3.7 tested)
* Selenium (current release)
* Chrome and Chrome Driver
* Pip (python package installer)

### Set up ###
1. Install python (see the internet). Python 3.7 or above is recommended as 2.7 (the default on mac) is being deprecated.
2. Check if you already have pip ("which pip"). If not, https://pip.pypa.io/en/stable/installing/
3. Download Chrome and the appropriate chrome driver for your chrome version (see http://chromedriver.chromium.org/downloads)
4. Get this repo:
     -- git clone https://github.com/scmorgen/park_search.git
	 -- cd park_serach
4. Note where you downloaded Chrome and change the variable CHROME_DRIVER_LOCATION in checker.py to your local location.
5. Set up your virtualenvironment
      pip install virtualenv # Always best to run things in a virtualenv
      virtualenv park_env
      park_env/bin/pip install -r requirements.txt
      park_env/bin/python checker.py
6. If the steps above worked, you are ready to run!

### Running the script
7. See all the parks supported:
	park_env/bin/python checker.py show_supported_parks

8. See all the tags supported
      park_env/bin/python checker.py show_supported_tags
9. Do a search for one day
park_env/bin/python checker.py check_one_date 05-25 --park "Big Basin"
park_env/bin/python checker.py check_one_date 05-25 --tag "yosemite"

10. Do a search for all the saturdays this summer
park_env/bin/python checker.py check_saturdays_in_range 06-01 09-15 --park "Big Basin"
park_env/bin/python checker.py check_one_date 05-25 06-01 09-15 --tag "yosemite"


### Adding more parks to the database

Find the campsite you wish to book on recreation.gov and click the site
https://www.recreation.gov/camping/campgrounds/232447/availability

Enter this into the dictionary ALL_SITES_DICT like so:
In this case I added my one tags "yosemite" and "kick_ass"
"Upper Pines2": {"url": https://www.recreation.gov/camping/campgrounds/232447/availability, "tags": ["yosemite", "kick_ass"]},


If you are grabbing a california state park, you just need the official name:
"<Official Name>": {"url": CALIFORNIA_URL, "tags": ["local", "kick_ass"]},

	Note: California abbreviates State Park as SP and State Beach as SB

