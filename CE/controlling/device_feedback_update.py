# import logging
# import time
# from Edge_Property.db.redis.cache_crud import CacheCRUD
# from Edge_Property.db.redis.cache_constants import DEVICE_KEYS
# from Edge_Property.db.redis.cache_state_update import CacheStateUpdate
# from Edge_Property.db.redis.airpurifier_timer import AirpurifierTimer
# from Edge_Property.db.hdf.database_api import DBApi
# from Edge_Property.structure.device_state.music.music import MusicFields
# class CacheDeviceFeedback(CacheCRUD):
#     def __init__(self, req_obj, mqtt_client):
#         self.req_obj = req_obj
#         self.mqtt_client = mqtt_client
#         super().__init__()
#         self.logger = logging.getLogger("CacheDeviceFeedback")
        
#     async def execute(self):
#         try:
#             dataArr = self.req_obj.get('dataArray', [])
#             for data in filter(None, dataArr):  # skips None automatically
#                 serial_id = data.get('CML_SERIAL_ID')
#                 if not serial_id:
#                     self.logger.debug("CML_SERIAL_ID missing in request.")
#                     continue

#                 device_data = await DBApi.set_prop_dict(serial_id)
#                 self.logger.debug(f"device_data: {device_data}")
#                 target = device_data[0].get('TARGET')

#                 if not target:
#                     self.logger.debug("TARGET not found in request.")
#                     continue

#                 device_type = data.get('CML_SUB_TYPE')
#                 if not device_type:
#                     self.logger.debug("CML_SUB_TYPE not found in request.")
#                     continue

#                 update_data = await self.get_mismatch_data(target, device_type, data)
#                 # if device_type == "MUSIC":
#                 #     await MusicFields.music_update_process(data, self.req_obj)
#                 # else:
#                 if not update_data:
#                     self.logger.debug("Delta matched. No need to proceed.")
#                     continue

#                 query_data = {
#                     "TARGET": target,
#                     "CML_SUB_TYPE": device_type,
#                     "CML_CONTROL_MODE": 1,
#                 }

#                 temp_req_obj = self.req_obj.copy()
#                 temp_req_obj["data"] = {
#                     'queryData': query_data,
#                     'updateData': update_data,
#                 }

#                 self.logger.debug(f"Update Data: {update_data}, Query Data: {query_data}")
#                 state_update = CacheStateUpdate(temp_req_obj, self.mqtt_client)
#                 await state_update.execute()
#         except Exception as e:
#             self.logger.error(f"Error in execute: {e}", exc_info=True)

#     async def get_mismatch_data(self, target, device_type, data):
#         try:
#             all_device_cache = await self.get_device_cache()
#             device_data = all_device_cache.get(target)

#             if not device_data:
#                 self.logger.debug(f"device {target} not found in cache in {all_device_cache}")
#                 return {}
            
#             device_states = device_data.get('device', {}).get(device_type)

#             if not device_states:
#                 self.logger.debug(f"device_states not found in cache in {all_device_cache}")
#                 return {}

#             update_data = {}
#             keys = DEVICE_KEYS.get(device_type, [])

#             self.logger.debug(f"device_states: {device_states}...................")
#             self.logger.debug(f"data: {data}...................")
#             for key in keys:
#                 if key in device_states and key in data:
#                     if device_states[key] != data[key]:
#                         update_data[key] = data[key]
#                 else:
#                     self.logger.debug(f"Key {key} missing in either device_states or data.")
#             if device_type in ["AIRPURIFIER"]:
#                 update_data = await AirpurifierTimer(self.mqtt_client).changes_for_timer(update_data,device_states,target)

#             if not update_data:
#                 update_data['CML_STATUS'] = data.get('CML_STATUS')
#             return update_data

#         except Exception as e:
#             self.logger.error(f"Error in get_mismatch_data: {e}", exc_info=True)
#             return {}
