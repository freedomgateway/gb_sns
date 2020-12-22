## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

"""Alphanumeric ID Generator for Transaction IDs

:author: Caden Koscinski
:see: https://docs.google.com/document/d/1xUzexyPlPzPKF-AyD4YANaQXwQlG5O7qDk0kZdyZ9us/edit
:see: settings.json
"""

from file_manager import file_manager


class id_manager:

    __characters = ['0','1','2','3','4','5','6','7','8','9',
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v','w','x','y','z']

    __query_id_cache_path = None
    __query_id_cache_file = None

    __settings_path = None
    __settings_file = None

    def __init__(self, query_name, id_cache_path="generic_id_cache.json", settings_path="settings.json"):
        self.__query_name = query_name
        self.__id_cache_path = id_cache_path
        self.__id_cache_file = file_manager(self.__id_cache_path)
        self.__settings_path = settings_path
        self.__settings_file = file_manager(self.__settings_path)
        self.__id_string = ""
        if not self.__id_cache_file.is_functional():
            self.__id_cache_file.write_json({})
        self.__functional = self.__id_cache_file.is_functional() and self.__settings_file.is_functional()

    def get_truncated_id_string(self):
        return self.__id_string

    def get_full_id_string(self):
        return self.get_standard_id_sections() + "-" + self.__id_string

    def get_standard_id_sections(self):
        settings_json = self.__settings_file.read_json()
        organization = settings_json["organization"]
        server = settings_json["server"]
        machine_brand = settings_json["machine_brand"]
        return organization + "-" + server + "-" + machine_brand

    # gb_terminal_json will need to be queried from the gbDB and populated
    def issue_id(self, observation_json, observation_reference, meta_json=None):
        cache_json = self.__id_cache_file.read_json()
        if meta_json is not None:
            meta_id = observation_json[observation_reference]
            gb_serial = meta_json[str(meta_id)]

            obs_id = None
            query_id = None
            query_name = self.__query_name
            if gb_serial in cache_json[query_name]:
                obs_id = cache_json[query_name][gb_serial][observation_reference]
                query_id = self.__increment_id(cache_json[query_name][gb_serial][f"last_{query_name}_id"])
                cache_json[query_name][gb_serial][f"last_{query_name}_id"] = query_id
            else:
                # Adds new entry to the cache for each identified machine
                if len(cache_json[query_name]) != 0:
                    obs_id = self.__increment_id(cache_json[f"last_{obs_id}"])
                else:
                    obs_id = cache_json[f"last_{obs_id}"]
                cache_json[f"last_{obs_id}"] = obs_id
                cache_json[query_name][gb_serial] = {}
                # cache_json[query_name][gb_serial]["brand"] = machine_brand
                cache_json[query_name][gb_serial][observation_reference] = cache_json[f"last_{obs_id}"]
                query_id = "000000"
                cache_json[query_name][gb_serial][f"last_{query_name}_id"] = query_id
        else:
            pass

        # Update cache
        self.__id_cache_file.write_json(cache_json)
        self.__id_string = obs_id + "-" + query_id
        return self.get_full_id_string()


    def __increment_id(self, current_id):

        current_id = list(current_id)

        id_length = len(current_id)
        characters_length = len(self.__characters)

        is_at_max = True
        for id_digit in current_id:
            if id_digit is not self.__characters[-1]:
                is_at_max = False

        if is_at_max:
            return "Overflow"

        scanned_index = id_length - 1;

        while scanned_index >= 0:
            current_character = current_id[scanned_index]

            if current_character != self.__characters[characters_length - 1]:
                current_id[scanned_index] = self.__characters[self.__characters.index(current_character) + 1]
                # Break Outer Loop - No need to continue scanning
                scanned_index = -1
            else:
                current_id[scanned_index] = self.__characters[0]
                scanned_index -= 1

        return "".join(current_id)
