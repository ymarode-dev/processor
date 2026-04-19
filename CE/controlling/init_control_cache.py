# import logging
# import Edge_Property.controller.constants.constants as c
# import json, os
# from collections import defaultdict
# import copy
# import time
# from Edge_Property.db.redis.cache_crud import CacheCRUD
# from Edge_Property.repository.devices import DevicesRepository
# from sqlmodel import select, and_

# class Init_redis_cache(CacheCRUD):
#     def __init__(self, db_name):
#         super().__init__()
#         self.db_name = db_name
#         self.logger = logging.getLogger("Init_redis_cache")

#         self.existing_device_cache = {}
#         self.existing_room_cache = {}
#         self.existing_floor_cache = {}
#         self.existing_property_cache = {}

#         self.MUSIC_GROUP_ACTIONS = {
#             "CAN_LOAD_PLAYLIST": 0,
#             "CAN_SET_VOLUME": 1,
#             "CAN_CHANGE_MODE": 0,
#             "CAN_GET_SEEK_POS": 0,
#             "CAN_SET_SEEK_POS": 0,
#             "CAN_PLAY_SPECIFIC_SONG": 0,
#             "CAN_PLAY_PAUSE_SONG": 1,
#             "CAN_GET_PLAYLISTS": 0,
#             "CAN_GET_SONGS_BY_PLAYLIST": 0,
#             "SUPPORTS_DEFAULT_PLAYLIST": 0,
#             "CAN_NEXT_PREV_SONG": 1,
#             "CAN_MUTE_UNMUTE": 1
#         }

        
#     async def build_radis_tree(self):
#         try:
#             self.existing_device_cache = await self.get_device_cache()
#             self.existing_room_cache = await self.get_room_cache()
#             self.existing_floor_cache = await self.get_floor_cache()
#             self.existing_property_cache = await self.get_property_cache()

#             self.logger.debug(f"existing_device_cache: {self.existing_device_cache}, existing_room_cache: {self.existing_room_cache}, existing_floor_cache: {self.existing_floor_cache}, existing_property_cache: {self.existing_property_cache}")

#             repo = DevicesRepository(portal_action=True)
#             stmt = select(repo.model).where(
#                 and_(
#                     repo.model.STRUCTURE_ID != -2,
#                     repo.model.CML_TYPE != "DEFAULT",
#                 )
#             )

#             devices = await repo.fetch_data_manual(stmt, True)
#             self.logger.debug(f"Devices fetched: {devices}")

#             device_objs = [item for item in devices if item["TARGET"].count('/') >= 3]

#             redis_data = {
#                 "Property": defaultdict(dict),
#                 "Floor": defaultdict(dict),
#                 "Room": defaultdict(dict),
#                 "Device": defaultdict(dict)
#             }

#             for entry in device_objs:
#                 self.logger.debug(f"entry : {entry}")
#                 path_parts = entry['TARGET'].strip('/').split('/')
#                 if len(path_parts) < 4:
#                     continue

#                 property_path = f"/{path_parts[0]}"
#                 floor_path = f"{property_path}/{path_parts[1]}"
#                 room_path = f"{floor_path}/{path_parts[2]}"
#                 device_path = f"{room_path}/{path_parts[3]}"

#                 level_map = {
#                     "Property": property_path,
#                     "Floor": floor_path,
#                     "Room": room_path,
#                     "Device": device_path,
#                 }

#                 subtype = entry['CML_SUB_TYPE']
#                 device_key = subtype

#                 if subtype == "MUSIC":
#                     state = {"_id": 0, c.SCENE_ID: -1, c.OVERRIDE: 0, c.STATE: 1, c.SETPOINT: 1, c.MODE: 1, c.MUTE: 0, "NEXT_TRACK_TITLE":"", "NEXT_TRACK_ALBUM":"", "NEXT_TRACK_ARTIST":"", "NEXT_TRACK_IMAGEURL":"","PLAY_LIST_ID":"", "PLAY_LIST_NAME":"", "TRACK_COUNT":-1, "CURRENT_TRACK_TITLE":"", "CURRENT_TRACK_ALBUM":"", "CURRENT_TRACK_ARTIST":"", "CURRENT_TRACK_IMAGEURL":"", "CURRENT_TRACK_URI":"",
#                              "CML_POSITION_MS": -1, "CURRENT_TRACK_DURATION": -1, "NEXT_TRACK_DURATION": -1,"changeTrack" : 0,"PLAYLIST_LOADED" : 0,
#                              c.STATUS: 1, "UPDATED_POSITION_TIME": -1, c.MIX_LOAD: 0, "ELEM_TYPE": "MUSIC"}
#                 elif subtype == "AIRPURIFIER":
#                     state = {"_id": 0, "CML_RUNNING": 0, "CML_PAUSED": 0, "CML_TIMER": -1, "CML_TOGGLE": 0,
#                              "CML_FAN_SPEED": 4, "CML_STATUS": 1, "CML_STATE": 1, "CML_MODE": 0,
#                              "CML_SCENE_ID": -1, c.MIX_LOAD: 0, "CML_AUTO": 0, "CML_TIMER_END": -1,
#                              "CML_BACKTOAUTO": -1, "CML_AUTO_TIMER": -1, "CML_AUTO_TIMER_END": -1,
#                              "VACATION_START": -1, "VACATION_END": -1, "VACATION_DAYS": -1,
#                              "VACATION_END_DAY": -1, "VACATION_END_MONTH": -1, "offStartTimer": -1,
#                              "offEndTimer": -1, "two_hour_timer": -1, "CML_FILTER": 0, "ELEM_TYPE": "AIRPURIFIER"}
#                 elif subtype == "LIGHT":
#                     state = {"_id": 0, c.SCENE_ID: -1, c.OVERRIDE: 0, c.STATE: 0, c.SETPOINT: 0,
#                              c.TEMPERATURE: 0, c.STATUS: 1, c.HUE: -1, c.SATURATION: -1, c.LIGHTNESS: -1,
#                              c.COLOR_SUPPORTED: 1, c.MIX_LOAD: 0, c.NONSMART_MIX_LOAD: 0, "ELEM_TYPE": "LIGHT"}
#                 elif subtype == "SWITCH":
#                     state = {"_id":0,c.SCENE_ID:-1,c.STATE:1,c.OVERRIDE:0,c.SETPOINT:0,
#                              c.STATUS:1,"ledBlink":0,c.MIX_LOAD:0, "ELEM_TYPE": "SWITCH"}
#                 elif subtype == "SENSOR":
#                     state = {"AQI_SCORE": -1, "AVG_AQI_SCORE": -1, "RESPONSIBLE_POLLUTANT": "", "AQI_CAT": "", "AQI_CAT_COLOR": "", "CML_STATUS": 1,
#                             "TVOC_AQI": -1, "PM25_AQI": -1, "PM10_AQI": -1, "CO2_AQI": -1, "CO_AQI": -1,"TEMPERATURE": -1, "HUMIDITY": -1, "PM25": -1, 
#                             "PM10": -1, "TVOC": -1, "CO2": -1, "CO": -1, "NO2": -1, "SO2": -1,"CML_OAQI_AQI":-1,
#                             "coConcentration":-1,"pm10Concentration":-1,"pm25Concentration":-1,"CML_TEMPERATURE":-1,"CML_RELATIVE_HUMIDITY":-1,
#                             "CML_WIND_MPH":-1,"LOCATION_NAME":"","CML_WEATHER_TEXT":"","CML_WIND_DIRECTION":-1,"CML_TEMPERATURE_CELCIUS":-1,"CML_WIND":-1,
#                             "CML_PRESSURE":-1,"CML_WIND_DIR":"",
#                             "O3": -1, "AVG_TEMPERATURE": -1, "AVG_HUMIDITY": -1, "AVG_TVOC": -1, "AVG_CO2": -1, "AVG_PM25": -1, 
#                             "AVG_PM10": -1, "PM1": -1, "TIMESTAMP": -1, "LAST_SYNC_TIME": int(time.time() * 1000), "ELEM_TYPE": "AQI","Fan_Speed":0}
#                 elif subtype == "SHADE":
#                     state = {"_id":0, c.SCENE_ID:-1, c.OVERRIDE:0, c.STATE:0, c.SETPOINT:0, c.STATUS:1, c.MIX_LOAD: 0, "CML_MODE": 0, "ELEM_TYPE": "SHADE"}
#                 elif subtype == "SLEEPSENSOR":
#                     state = {"sleep_duration": -1,"light_sleep_duration": -1,"deep_sleep_duration": -1,"rem_sleep_duration": -1, "sleep_start_time": -1,"sleep_end_time": -1,c.STATE:1,
#                              "snoring": -1,"snoring_episode_count": -1,"wake_up_count": -1,"wake_up_duration": -1,"date":'',"avg_heart_rate": -1,"avg_resp_rate": -1,c.STATUS:1,
#                              "sleep_score": -1,"total_time_in_bed": -1,"LAST_SYNC_TIME": int(time.time() * 1000),"ELEM_TYPE": "SLEEPSENSOR","TIMESTAMP": -1,"durationtosleep":0,"durationtowakeup":0
#                             }
#                 elif subtype == "HVAC":
#                     state = {"_id":0,"CML_MAX_TEMP": 90, "CML_MIN_TEMP": 50,"CML_TEMP_UNITS": "FAHRENHEIT","CML_LOWER_POINT": -1,"CML_PREVIOUS_MODE":1,
#                     "CML_HIGHEST_POINT": -1,"CML_HEAT_TO": -1,"CML_COOL_TO": -1,"CML_ROOM_TEMPERATURE": -1,"CML_SET_POINT": -1,"CML_COOL_HOLD_TEMP":-1,
#                     "CML_MODE": 0, "CML_STATUS": 1,"CML_INDOOR_HUMIDITY": -1,"CML_FAN_SPEED": 0,"CML_PURIFICATION_STATE":1,"CML_SETPOINT":-1,"CML_HEAT_HOLD_TEMP":-1,
#                     "CML_STATE": 1,"CML_SET_POINT_LIMIT": 5,"MIN_HEAT_SETPOINT": -1,
#                     "MAX_HEAT_SETPOINT": -1, "MIN_COOL_SETPOINT": -1,"MAX_COOL_SETPOINT": -1,c.OVERRIDE: 0,
#                     c.SCENE_ID:-1,c.MIX_LOAD:0,"ELEM_TYPE":"HVAC"}
#                 else:
#                     state = {"_id": 0}

#                 actions = {}
#                 properties = {}
#                 try:
#                     action_props = json.loads(entry.get('ACTIONS_PROPERTIES', '[]'))
#                     for item in action_props:
#                         actions[subtype] = item.get("actions", {})
#                         properties[subtype] = item.get("properties", {})
#                 except Exception as e:
#                     self.logger.debug(f"Error parsing ACTIONS_PROPERTIES: {e}", exc_info=True)


#                 for level, path in level_map.items():
#                     self.logger.debug(f"level:  {level}")
#                     self.logger.debug(f"path : {path}")
#                     entry_data = redis_data[level][path]

#                     if "device" not in entry_data:
#                         entry_data["device"] = {}
#                     if "actions" not in entry_data:
#                         entry_data["actions"] = {}
#                     if "properties" not in entry_data :
#                         entry_data["properties"] = {}
#                     entry_data["device"][device_key] = copy.deepcopy(state)
#                     device_actions = actions.get(device_key, {})
#                     device_properties = properties.get(device_key, {})
#                     if device_key in entry_data["actions"]: 
#                         await self.get_common_action(entry_data, device_actions, device_key)
#                     else:
#                         entry_data["actions"].setdefault(device_key, {}).update(actions.get(device_key, {}))
#                     if device_key in entry_data["properties"]:
#                         await self.get_properties_action(entry_data, device_properties, device_key)
#                     else:
#                         entry_data["properties"].setdefault(device_key, {}).update(properties.get(device_key, {}))
#                     if subtype == "MUSIC" and level in ["Property","Floor"] :
#                         entry_data["actions"]["MUSIC"] = self.MUSIC_GROUP_ACTIONS.copy()
#             update_redis_data = await self.fill_existing_states(redis_data)

#             is_redis_data_set = await self.set_updated_redis_data(update_redis_data)

#             if is_redis_data_set:
#                 await self.set_updated_redis_data_json(update_redis_data)
#             else:
#                 self.logger.debug("Failed to set updated Redis data.")

#         except Exception as e:
#             self.logger.debug(f"In build_radis_tree: {e}", exc_info=True)
        
#     async def get_common_action(self, entry_data, device_actions, device_key):
#         try:
#             aggregated_actions = entry_data.get("actions", {}).get(device_key, {})
#             data ={k: v for k, v in aggregated_actions.items() if k in device_actions and device_actions[k] == v}
#             for key in list(aggregated_actions.keys()):
#                 if key in data:
#                     aggregated_actions[key] = min(aggregated_actions[key], data[key])
#                 else:
#                     aggregated_actions.pop(key, None)

#             self.logger.debug(f"aggregated_actions: {aggregated_actions}")
#         except Exception as e:
#             self.logger.debug(f"Error in get_common_action: {e}", exc_info=True)
                
#     async def get_properties_action(self, entry_data, device_properties, device_key):
#         try:
#             aggregated_props = entry_data["properties"][device_key]
#             data ={k: v for k, v in aggregated_props.items() if k in device_properties and device_properties[k] == v}
#             for key, values in device_properties.items():
#                 if key in aggregated_props :
#                     self.logger.debug(f"values props: {values}")
#                     if key.startswith("CML_MIN"):
#                         aggregated_props[key] = max(aggregated_props[key], values)
#                     elif key.startswith("CML_MAX"):
#                         aggregated_props[key] = min(aggregated_props[key], values)
#                 else:
#                     del aggregated_props[key]
#             self.logger.debug(f"aggregated_props: {aggregated_props}")
#         except Exception as e:
#             self.logger.debug(f"Error in get_properties_action: {e}", exc_info=True)

    
#     async def set_updated_redis_data(self, update_redis_data):
#         try:
#             for key in ["Property", "Floor", "Room", "Device"]:
#                 value = {k: v for k, v in update_redis_data[key].items()}
#                 await self.set_data(key, value)
#                 self.logger.debug(f"Stored in Redis -> {key} ({len(value)} entries)")
            
#             return True
#         except Exception as e:
#             self.logger.debug(f"Error in set_updated_redis_data: {e}", exc_info=True)
#             return False

#     async def set_updated_redis_data_json(
#         self,
#         update_redis_data,
#         file_path=os.path.join(c.FILES_FOLDER_PATH, "device_cache.json"),
#     ):
#         return True


#     async def fill_existing_states(self, redis_data):
#         try:
#             self.logger.debug(f"Initial redis_data: {redis_data}")
            
#             hierarchy_cache_map = {
#                 "Property": self.existing_property_cache,
#                 "Floor": self.existing_floor_cache,
#                 "Room": self.existing_room_cache,
#                 "Device": self.existing_device_cache,
#             }

#             if not all(hierarchy_cache_map.values()):
#                 self.logger.debug("One or more hierarchy caches are empty. Skipping update.")
#                 return redis_data

#             for hierarchy, old_cache in hierarchy_cache_map.items():
#                 new_cache = redis_data.get(hierarchy, {})

#                 for path, data in old_cache.items():
#                     if path in new_cache:
#                         if 'device' in data and 'device' in new_cache[path]:
#                             self.logger.debug(f"Updating devices for {path} in {hierarchy}")
#                             for device, device_data in new_cache[path]['device'].items():
#                                 if device in data['device']:
#                                     device_data.update(data['device'][device])
#                                     self.logger.debug(f"→ Merged device '{device}' in '{path}' with existing state.")
#                                 else:
#                                     self.logger.debug(f"→ Device '{device}' not in existing cache for '{path}'.")
#                         else:
#                             self.logger.debug(f"→ 'device' key missing in old or new cache for '{path}' in '{hierarchy}'")
#                     else:
#                         self.logger.debug(f"→ Path '{path}' missing in new_cache for hierarchy '{hierarchy}'")

#                 redis_data[hierarchy] = new_cache

#             self.logger.debug(f"Final updated redis_data: {redis_data}")
#             return redis_data

#         except Exception as e:
#             self.logger.exception("Exception in fill_existing_states")
#             return redis_data


