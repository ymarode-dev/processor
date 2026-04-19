# import asyncio
# import logging
# import time
# import pytz, uuid
# from datetime import datetime
# from Edge_Property.db.redis.cache_crud import CacheCRUD
# from Edge_Property.db.redis.cache_constants import DEVICE_KEYS
# from Edge_Property.structure.device_state.processors.transform_update_values import TransformUpdateValues
# from Edge_Property.structure.device_state.processors.broadcast import broadcast_response
# from Edge_Property.db.hdf.database_api import DBApi
# from Edge_Property.structure.device_state.music.music import MusicFields
# from Edge_Property.repository.repo_mapping import RepoMapping

# class CacheStateUpdate(CacheCRUD):
#     _lock = asyncio.Lock()
#     def __init__(self, req_obj, mqtt_client):
#         self.req_obj = req_obj
#         self.mqtt_client = mqtt_client
#         super().__init__()
#         #self.background_tasks = set()
#         self.logger = logging.getLogger("CacheStateUpdate")

#     def get_target(self, path: str, level: int):
#         try:
#             parts = path.strip("/").split("/")
#             if 0 <= level < len(parts):
#                 target = "/" + "/".join(parts[:level + 1])
#                 self.logger.debug(f"get_target: {target}")
#                 return target
#             else:
#                 self.logger.debug(f"Invalid level {level} for path with {len(parts)} segments.")
#                 return None
#         except Exception as e:
#             self.logger.error(f"Error in get_target: {e}", exc_info=True)
#             return None
        
#     def get_level_index(self, level: str) -> int:
#         try:
#             hierarchy = {
#                 "Device": 2,
#                 "Room": 1,
#                 "Floor": 0
#             }
#             index = hierarchy.get(level, -1)
#             self.logger.debug(f"get_level_index: {index}")
#             return index
#         except Exception as e:
#             self.logger.error(f"Error in get_level_index: {e}", exc_info=True)
    
#     def get_level_hierarchy(self, current_level: str) -> str:
#         try:
#             level_hierarchy = {
#                 "Device": "Room",
#                 "Room": "Floor",
#                 "Floor": "Property"
#             }
#             hierarchy = level_hierarchy.get(current_level)
#             self.logger.debug(f"get_level_hierarchy: {hierarchy}")
#             return hierarchy
#         except Exception as e:
#             self.logger.error(f"Error in get_level_hierarchy: {e}", exc_info=True)

#     def get_current_level(self, control_mode):
#         try:
#             current_level = {
#                 1: "Device",
#                 4: "Room",
#                 8: "Floor",
#                 12: "Property",
#             }

#             return current_level.get(control_mode)
#         except Exception as e:
#             self.logger.error(f"Error in get_level_index: {e}", exc_info=True)
        
#     def get_next_lower_level(self, current_level: str) -> str:
#         try:
#             next_level = {
#                 "Property": "Floor",
#                 "Floor": "Room",
#                 "Room": "Device"
#             }
#             return next_level.get(current_level)
#         except Exception as e:
#             self.logger.error(f"Error in get_next_lower_level: {e}", exc_info=True)

#     async def execute(self):
#         async with self._lock:
#             try:
#                 start_time = int(time.time() * 1000)
#                 self.logger.info(f"SCENE execute() in main= Start time : {start_time} ms for slot")
#                 self.logger.debug(f"Executing CacheStateUpdate: {self.req_obj}")
#                 query_data = self.req_obj.get("data", {}).get("queryData", None)
#                 if not query_data:
#                     self.logger.debug("No query data provided in request object")
#                     return

#                 current_target = query_data.get("TARGET")
#                 device_type = query_data.get("CML_SUB_TYPE")
#                 control_mode = query_data.get("CML_CONTROL_MODE")

#                 if not current_target or not control_mode or not device_type:
#                     self.logger.debug("Missing required fields in request object")
#                     return
                
#                 transformed_update_data = await TransformUpdateValues.manipulate_update_data(self.req_obj)
#                 self.logger.debug(f"transformed_update_data: {transformed_update_data}")

#                 if not transformed_update_data:
#                     self.logger.debug("Missing transformed_update_data so skipping..............")
                
#                 if transformed_update_data:
#                     if control_mode in [1, 4, 8, 12]:
#                         current_hierarchy = self.get_current_level(control_mode)
#                         self.logger.debug(f"{current_hierarchy} Level Call....................")
#                         await self.generic_forward_propagate(current_hierarchy, current_target, device_type, transformed_update_data)

#                         if current_hierarchy != "Property":
#                             await self.generic_backward_propagate(current_target, device_type, current_hierarchy)
#                     else:
#                         self.logger.debug("Unknown Level Call....................")
#                 self.logger.info(f"SCENE execute() in main= Time taken for slot : {int(time.time() * 1000) - start_time} ms")

#                 start_time = int(time.time() * 1000)
#                 self.logger.info(f"SCENE broadcast_response()= Start time : {start_time} ms for slot")
#                 await self.broadcast_response(device_type, current_target)
#                 self.logger.info(f"SCENE broadcast_response()= Time taken for slot : {int(time.time() * 1000) - start_time} ms")
#             except Exception as e:
#                 self.logger.error(f"Error executing execute: {e}", exc_info=True)

#     async def cache_getters(self, next_level):
#         try:
#             cache_getters = {
#                 "Property": self.get_property_cache,
#                 "Floor": self.get_floor_cache,
#                 "Room": self.get_room_cache,
#                 "Device": self.get_device_cache,
#             }

#             return await cache_getters[next_level]()
#         except Exception as e:
#             self.logger.error(f"Error executing cache_getters: {e}", exc_info=True)

#     async def cache_setters(self, next_level, cache):
#         try:
#             cache_setters = {
#                 "Property": lambda data: self.set_data("Property", data),
#                 "Floor": lambda data: self.set_data("Floor", data),
#                 "Room": lambda data: self.set_data("Room", data),
#                 "Device": lambda data: self.set_data("Device", data),
#             }

#             return await cache_setters[next_level](cache)
#         except Exception as e:
#             self.logger.error(f"Error executing cache_setters: {e}", exc_info=True) 
        
#     async def generic_forward_propagate(self, current_hierarchy: str, current_target: str, device_type: str, update_data: dict):
#         try:
#             self.logger.debug(f"[Forward] Propagation at level {current_hierarchy} for {current_target} with {update_data}")

#             await self.update_cache(current_hierarchy, current_target, device_type, update_data)

#             next_hierarchy = self.get_next_lower_level(current_hierarchy)
#             if next_hierarchy:
#                 await self.generic_forward_propagate(next_hierarchy, current_target, device_type, update_data)
#             else:
#                 self.logger.debug(f"[Forward] Reached Device level")

#         except Exception as e:
#             self.logger.error(f"Error in generic_forward_propagate at level {current_hierarchy}: {e}", exc_info=True)

#     async def update_cache(self, current_hierarchy, current_target, device_type, update_data):
#         try:
#             cache = await self.cache_getters(current_hierarchy)

#             for path, data in cache.items():
#                 if path.startswith(current_target):
#                     devices = data.get("device", {})
#                     if device_type in devices:
#                         devices[device_type].update(update_data)
#                         self.logger.debug(f"[Forward] Updated {device_type} at {path} with {update_data}")
#                     else:
#                         self.logger.debug(f"[Forward] Skipped {path} as it does not contain {device_type}")
#             self.logger.debug(f"update_cache: {cache}, current_hierarchy: {current_hierarchy}")
#             await self.cache_setters(current_hierarchy, cache)

#         except Exception as e:
#             self.logger.error(f"Error in update_cache: {e}", exc_info=True)

#     async def generic_backward_propagate(self, current_target: str, device_type: str, current_hierarchy: str):
#         try:
#             next_hierarchy = self.get_level_hierarchy(current_hierarchy)
#             if not next_hierarchy:
#                 self.logger.debug(f"No further propagation required from level: {current_hierarchy}")
#                 return

#             current_hierarchy_ind = self.get_level_index(current_hierarchy)
#             if current_hierarchy_ind < 0:
#                 self.logger.debug(f"Could not find current_hierarchy_ind from {current_target} at level {current_hierarchy}")
#                 return
            
#             parent_target_id = self.get_target(current_target, current_hierarchy_ind)
#             if not parent_target_id:
#                 self.logger.debug(f"Could not find parent target_id from {current_target} at level {current_hierarchy}")
#                 return

#             self.logger.debug(f"parent_target_id: {parent_target_id}, current_hierarchy: {current_hierarchy}")
#             update_data = await self.get_update_data(parent_target_id, device_type, current_hierarchy)
#             if not update_data:
#                 self.logger.debug(f"Update data is empty for {next_hierarchy} from {current_hierarchy}, skipping propagation")
#                 return

#             self.logger.debug(f"update_data: {update_data}")
#             await self.update_cache(next_hierarchy, parent_target_id, device_type, update_data)

#             await self.generic_backward_propagate(parent_target_id, device_type, next_hierarchy)

#         except Exception as e:
#             self.logger.error(f"Error during generic_backward_propagate at level {current_hierarchy}: {e}", exc_info=True)

#     async def get_update_data(self, target_id, device_type, cache_table):
#         try:
#             all_cache = await self.get_data(cache_table)
#             self.logger.debug(f"Get {device_type} Device Data for target: {target_id} and cache {all_cache}")
#             return await self.get_device_update_data(target_id, device_type, all_cache)
#         except Exception as e:
#             self.logger.error(f"Error executing get_update_data: {e}", exc_info=True)
#             return {}
    
#     async def get_device_update_data(self, target_id, device_type, all_cache):
#         try:
#             update_data = {}
#             keys = DEVICE_KEYS.get(device_type, [])

#             if device_type == "SENSOR":
#                 return await self.get_update_sensor_data(target_id, all_cache, device_type, "AQI_SCORE")

#             for key in keys:
#                 if key in ["CML_STATE", "CML_STATUS"]:
#                     val = await self.check_device_state_status(target_id, all_cache, device_type, key)
#                 else:
#                     val = await self.check_generic_params(target_id, all_cache, device_type, key)

#                 if val is not None:
#                     update_data[key] = val

#             return update_data
#         except Exception as e:
#             self.logger.error(f"Error in get_device_update_data: {e}", exc_info=True)
#             return {}

#     async def check_device_state_status(self, target_id, all_cache, device_type, key):
#         try:
#             for path, data in all_cache.items():
#                 if path.startswith(target_id):
#                     if "device" in data and device_type in data["device"] and key in data["device"][device_type]:
#                         val = data["device"][device_type][key]
#                         if val == 1:
#                             self.logger.debug(f"Device at {path} has {key} = {val}")
#                             return 1
#             return 0
#         except Exception as e:
#             self.logger.error(f"Error in check_device_state_status: {e}", exc_info=True)
#             return None
        
#     async def check_generic_params(self, target_id, all_cache, device_type, key):
#         try:
#             value = set()
#             for path, data in all_cache.items():
#                 if path.startswith(target_id):
#                     if "device" in data and device_type in data["device"] and key in data["device"][device_type]:
#                         val = data["device"][device_type][key]
#                         self.logger.debug(f"Device at {path} is {key} = {val}")
#                         if isinstance(val, list):
#                             continue
#                         else:
#                             value.add(val)

#             if len(value) > 1:
#                 self.logger.debug(f"Inconsistent values for {key}, skipping update")
#                 return None

#             return value.pop() if value else None
#         except Exception as e:
#             self.logger.error(f"Error in check_generic_params: {e}", exc_info=True)
#             return None
        
#     async def get_update_sensor_data(self, target_id, all_cache, device_type, key):
#         try:
#             update_data = {}
#             max_aqi_score = float('-inf')
#             for path, data in all_cache.items():
#                 if not path.startswith(target_id):
#                     continue

#                 device_data = data.get("device", {}).get(device_type, {})
#                 val = device_data.get(key)
#                 if isinstance(val, (int, float)): 
#                     if val >= max_aqi_score:
#                         max_aqi_score = val
#                         update_data = device_data 

#             return update_data
#         except Exception as e:
#             self.logger.debug(f"Error in get_update_sensor_data: {e}", exc_info=True)
#             return {}

#     async def broadcast_response(self, device_type, current_target):
#         try:
#             timestamp = await self.get_current_timestamp()

#             tasks = [
#                 self.generate_level_response(level, device_type, current_target, timestamp)
#                 for level in ["Device", "Room", "Floor", "Property"]
#             ]
#             await asyncio.gather(*tasks)

#         except Exception as e:
#             self.logger.error(f"Error in broadcast_response: {e}", exc_info=True)

#     async def generate_level_response(self, level_type, device_type, current_target, timestamp):
#         res = []
#         try:
#             start_time = int(time.time() * 1000)
#             self.logger.info(f"SCENE generate_level_response= Start time : {start_time} ms for slot")
            
#             music_fields_data = {}

#             # ---- MUSIC special handling ----
#             if device_type == "MUSIC" and level_type == "Room":
#                 device_count_obj = await self.find_devicess_count()
#                 music_fields_data["device_count"] = device_count_obj
#                 self.logger.debug(f"retrieve_state - device_count_obj - {device_count_obj}")

#             # ---- Get cache ----
#             cache = await self.get_data(level_type)

#             for path, data in cache.items():
#                 if await self.is_valid_for_response(current_target, path):
#                     devices = data.get("device", {})

#                     if device_type in devices:
#                         valid_entries = devices[device_type]
#                         #valid_entries.append((path, devices[device_type]))
                        
#                         db_data = await DBApi.get_static_tables(path, level_type)

#                         if device_type == "MUSIC" and level_type == "Device" and self.req_obj["type"] != "set_mode":
#                             db_data = await MusicFields.change_music_obj(db_data)
                        
#                         id_obj = {"ID": f"ID_{uuid.uuid4()}"}

#                         complete_device_data = {
#                             **db_data,
#                             **valid_entries,
#                             **music_fields_data,
#                             **timestamp,
#                             **id_obj
#                         }

#                         res.append(complete_device_data)

#             self.logger.debug(f"generate_{level_type.lower()}_response, res: {res}")
#             self.logger.info(f"SCENE generate_level_response= Time taken for slot : {int(time.time() * 1000) - start_time} ms")

#             # ---- Broadcast ----
#             if len(res)>0:
#                 start_time = int(time.time() * 1000)
#                 self.logger.info(f"SCENE broadcast_response in broadcast.py= Start time : {start_time} ms for slot")
#                 await broadcast_response(self.req_obj, res, level_type.lower(), self.mqtt_client)
#                 self.logger.info(f"SCENE broadcast_response in broadcast.py= Time taken for slot : {int(time.time() * 1000) - start_time} ms")

#                 if level_type == "Device" and self.req_obj.get('type') == "set_properties_device":
#                     # await DBDeviceData.insert_device_data_in_db(res, device_type)
#                     pass

#         except Exception as e:
#             self.logger.error(f"Error in generate_level_response for {level_type}: {e}", exc_info=True)

#     async def is_valid_for_response(self, req_target, control_target) -> bool:
#         try:
#             req_target_parts = req_target.strip("/").split("/")
#             control_target_parts = control_target.strip("/").split("/")

#             if req_target_parts == control_target_parts:
#                 return req_target == control_target
            
#             elif req_target_parts < control_target_parts:
#                 return req_target in control_target
            
#             elif req_target_parts > control_target_parts:
#                 return control_target in req_target
            
#             else:
#                 self.logger.debug(f"Unknown scenario for req_target: {req_target}, control_target: {control_target}")
#                 return True
#         except Exception as e:
#             self.logger.error(f"Error in is_valid_for_response for req_target: {req_target}, control_target: {control_target}: {e}", exc_info=True)  
#             return True

#     async def get_current_timestamp(self):
#         default_obj = {'TIMESTAMP': -1, 'MONTH': -1, 'YEAR': -1, 'SYNC_TIME': -1}

#         try:
#             repo = await RepoMapping.get_repository('location', False)
#             all_locations = await repo.get_all_locations()

#             if not all_locations:
#                 self.logger.error("No locations found")
#                 return default_obj

#             primary_location = all_locations[0]
#             timezone = primary_location.get('CML_TIMEZONE')

#             if not timezone:
#                 self.logger.error("Timezone not found in location")
#                 return default_obj

#             try:
#                 tz = pytz.timezone(timezone)
#             except Exception:
#                 self.logger.error(f"Invalid timezone: {timezone}")
#                 return default_obj

#             now_tz = datetime.now(tz)

#             now_tz = now_tz.replace(second=0, microsecond=0)

#             epoch_ms = int(now_tz.timestamp() * 1000)

#             result = {
#                 "TIMESTAMP": epoch_ms,
#                 "MONTH": now_tz.month, 
#                 "YEAR": now_tz.year,
#                 "SYNC_TIME": -1,
#             }

#             self.logger.info(f"Timestamp generated: {result}")
#             return result
#         except Exception as e:
#             self.logger.error(f"Error in get_current_timestamp: {e}", exc_info=True)
#             return default_obj