from datetime import datetime

import requests
import json
import os


class DLB:

    """
    The DLB class contains the connection info and functions for directly accessing the DroneLogBook API
    """

    def __init__(self, **kwargs):

        """
        Initializes a DLB object
        :param kwargs: Unless specified in ~/.cass-keys, `api_key` and `dlb_url` need to be specified in the kwargs
        :type kwargs:
        """

        # If the
        if 'api_key' not in kwargs.keys() and 'dlb_url' not in kwargs.keys():

            try:
                cred_fn = os.path.join(os.path.expanduser("~"), ".cass-keys")
            except FileNotFoundError:
                print(f".cass-keys file not found in {os.path.expanduser('~')}")
                return

            with open(cred_fn, 'rb') as fh:
                creds = json.loads(fh.read())

            self.dlb_api_key = creds['dlb_api_key']
            self.dlb_url = creds['dlb_url']

        else:
            self.dlb_api_key = kwargs.get('api_key')
            self.dlb_url = kwargs.get('dlb_url')

        self.flights = None

        return

    def get_binary(self, guid, filename):

        """
        Downloads the original flight log binary file associated with the flight guid
        :param guid: guid of the flight
        :type guid: str
        :param filename: Name of the resulting file
        :type filename: str
        :return: requests.models.Response object from the API POST
        :rtype:
        """

        if guid is None or guid == '':
            return None

        r = requests.post("https://ou.dronelogbook.com/webservices/getOriginalLogData.php",
                          data={"apiKey": self.dlb_api_key,
                                'flightId': guid})

        if filename is not None:
            with open(filename, 'wb') as fh:
                fh.write(r.content)

        return r

    def get_drone(self, guid=None):

        """
        Retrieve and create a Drone object from the corresponding guid
        :param guid: guid of the desired Drone
        :type guid: str
        :return: Drone object
        :rtype: dronelogbook.Drone
        """

        if guid is None or guid == '':
            return None

        response = requests.get(f'https://api.dronelogbook.com/drone/{guid}', headers={"accept": "application/json",
                                                                                       "ApiKey": self.dlb_api_key,
                                                                                       "DlbUrl": self.dlb_url})
        return Drone(response.json()['data'][0])

    def get_equipment(self, guid=None):

        """
        Retrieve and create a Equipment object from the corresponding guid
        :param guid: guid of the desired Equipemnt
        :type guid: str
        :return: Equipment object
        :rtype: dronelogbook.Equipment
        """

        if guid is None or guid == '':
            return None

        response = requests.get(f'https://api.dronelogbook.com/equipment/{guid}', headers={"accept": "application/json",
                                                                                           "ApiKey": self.dlb_api_key,
                                                                                           "DlbUrl": self.dlb_url})
        return Equipment(response.json()['data'][0])

    def get_flight(self, guid, recursive=False):

        """
        Retrieve and create a Flight object from the corresponding guid
        :param guid: guid of the Flight
        :type guid: str
        :param recursive: If True, use create Drone, Place, Project, and Equipment objects from the guids contained
        in the flight
        :type recursive: bool
        :return:
        :rtype:
        """

        if guid is None or guid == '':
            return None

        data = requests.get(f'https://api.dronelogbook.com/flight/{guid}', headers={"accept": "application/json",
                                                                                    "ApiKey": self.dlb_api_key,
                                                                                    "DlbUrl": self.dlb_url})

        if data.status_code == 200:
            flight = Flight(data.json()['data'][0])

            if recursive:  # Grab and store the Drone, Place, and Project objects as well
                flight.drone = self.get_drone(flight.drone_guid)
                flight.place = self.get_place(flight.place_guid)
                flight.project = self.get_project(flight.project_guid)
                flight.equipment = [self.get_equipment(guid) for guid in flight.equipment]

            return flight

        else:
            print(f"Error in get_flight API operation. Response code: {data.status_code}")
            return None

    def get_flights(self, page_num=1, recursive=False):

        """
        Get ALL the flights contained in DroneLogBook starting with page `page_num`
        :param page_num: Page to start querying
        :type page_num: int
        :param recursive: If True, use create Drone, Place, Project, and Equipment objects from the guids contained
        in the flight
        :type recursive:bool
        :return:
        :rtype:
        """

        flights = []

        data = requests.get(f'https://api.dronelogbook.com/flight?num_page={page_num}',
                            headers={"accept": "application/json",
                                     "ApiKey": self.dlb_api_key,
                                     "DlbUrl": self.dlb_url})

        data = data.json()

        for flight_data in data['data']:
            flight = Flight(flight_data)

            if recursive:  # Grab and store the Drone, Place, and Project objects as well
                flight.drone = self.get_drone(flight.drone_guid)
                flight.place = self.get_place(flight.place_guid)
                flight.project = self.get_project(flight.project_guid)
                flight.equiement = [self.get_equipment(guid) for guid in flight.equipment]

            flights.append(flight)

        # If there are more pages of flights, keep going through them
        if data['has_more']:
            flights += self.get_flights(page_num=page_num+1, recursive=recursive)

        return flights

    def get_place(self, guid):

        """
        Retrieve and create a Place object from the corresponding guid
        :param guid: guid of the desired Place
        :type guid: str
        :return: Equipment object
        :rtype: dronelogbook.Place
        """

        response = requests.get(f'https://api.dronelogbook.com/place/{guid}', headers={"accept": "application/json",
                                                                                       "ApiKey": self.dlb_api_key,
                                                                                       "DlbUrl": self.dlb_url})
        return Place(response.json()['data'][0])

    def get_project(self, guid):

        if guid is None or guid == '':
            return None

        return


class Flight:

    def __init__(self, data):
        """

        :param data:
        :type data:
        """

        self.raw_data = data
        self.guid = data['guid']
        self.personnel = data['personnel']
        self.weather = data['weather_detail']
        self.duration = data['duration_seconds']
        self.place_name = data['place_name']

        self.drone_guid = data['drone_guid']
        self.place_guid = data['place_guid']
        self.project_guid = data['project_guid']
        self.equipment = data['equipments']

        self.drone = None
        self.place = None
        self.project = None

        try:
            self.flight_time = datetime.strptime(data['flight_date_utc'], '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            print(f"Error decoding time in flight {data['guid']}")
            self.flight_time = datetime(1970, 1, 1)

        return

    def __str__(self):

        if self.drone is not None:
            return f"Flight launched on {self.flight_time} at location {self.place_name} for project {self.project} using {self.drone}"

        else:
            return f"Flight launched on {self.flight_time} at location {self.place_name} for project {self.project}"

    def __gt__(self, other):
        return self.flight_time > other.flight_time

    def __lt__(self, other):
        return self.flight_time < other.flight_time

    def __eq__(self, other):
        return self.flight_time == self.flight_time


class Drone:

    def __init__(self, data):
        """
        Drone initilization

        Drone objects contain:
        - The raw json data (self.raw_data)
        - The drone guid (self.guid)
        - Brand (self.brand)
        - Model (self.model)
        - ID Number (self.id_number)
        - Notes on the drone (self.notes)


        :param data: Dictionary from API request
        :type data: dict
        """

        self.raw_data = data
        self.guid = data['guid']
        self.brand = data['brand']
        self.model = data['model']
        self.id_number = data['identification_number']
        self.notes = data['notes'].split('\r\n')

        return

    def __str__(self):
        return f"{self.brand} {self.model} {self.id_number}"


class Place:

    def __init__(self, data):

        self.raw_data = data
        self.guid = data['guid']

        self.altitude = float(data['altitude'])
        self.latitude = float(data['latitude'])
        self.longitude = float(data['longitude'])

        self.name = data['name']
        self.address = data['address']

        return

    def get_usgs_alt(self):

        url = f'https://nationalmap.gov/epqs/pqs.php?x={self.longitude}&y={self.latitude}&units=Meters&output=json'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']

            self.altitude = data['Elevation']

        else:
            print("Error in querying USGS")

        return self.altitude


class Project:

    def __init__(self, data):

        self.raw_data = data

        return


class Equipment:

    def __init__(self, data):

        self.raw_data = data
        self.name = data['name']
        self.type = data['equipment_type']
        self.notes = data['notes'].split('\r\n')

        if 'scoop' in self.name.lower():
            self.scoop = self.name.split(' ')[-1]

        for note in self.notes:

            if 'imet' in note.lower():
                split = note.split(',')[1:]

                self.imet_sn = [id for id in split if id != ' ']

            if 'hyt' in note.lower():
                split = note.split(',')[1:]

                self.hyt_sn = [id for id in split if id != ' ']

        return

    def is_scoop(self):
        if self.scoop is not None:
            return True
        else:
            return False


