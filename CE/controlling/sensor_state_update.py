# import logging
# from Edge_Property.db.redis.cache_crud import CacheCRUD
# from Edge_Property.db.redis.cache_constants import DEVICE_KEYS
# from Edge_Property.db.hdf.database_api import DBApi
# from Edge_Property.db.redis.cache_state_update import CacheStateUpdate
# from Edge_Property.structure.device_state.processors.broadcast import broadcast_response
# from Edge_Property.structure.sensors.environmental.insert_reset_sensor_data import InsertResetSensorData
# from IOT_Devices.notifications.sensor_notification import SensorNotification


# class CacheSensorData(CacheCRUD):
#     __aqi_cat_list = [{"min":0,"max":50,"AQI_CAT":"Good","AQI_CAT_COLOR":"Green"},
#                       {"min":51,"max":100,"AQI_CAT":"Moderate","AQI_CAT_COLOR":"Yellow"},
#                       {"min":101,"max":150,"AQI_CAT":"Poor","AQI_CAT_COLOR":"Red"},
#                       {"min":151,"max":200,"AQI_CAT":"Unhealthy","AQI_CAT_COLOR":"Red"},
#                       {"min":201,"max":300,"AQI_CAT":"Very Unhealthy","AQI_CAT_COLOR":"Purple"},
#                       {"min":301,"max":500,"AQI_CAT":"Hazardous","AQI_CAT_COLOR":"Maroon"}]
    
#     def __init__(self, req_obj, mqtt_client):
#         super().__init__()
#         self.req_obj = req_obj
#         self.mqtt_client = mqtt_client
#         self.logger = logging.getLogger("CacheSensorData")
    
#     async def execute(self):
#         try:
#             sensor_cache = CacheStateUpdate(self.req_obj, self.mqtt_client)

#             cache_data = await self.get_device_cache() 
#             provision_device_cache = []
            
#             self.logger.debug(f"req_obj: {self.req_obj}")
#             dataArr = self.req_obj.get('data', [])

#             for data in dataArr:
#                 serial_id = data.get('CML_SERIAL_ID')
#                 if not serial_id:
#                     self.logger.debug("CML_SERIAL_ID in request.")
#                     return

#                 device_data = await DBApi.set_prop_dict(serial_id)
#                 self.logger.debug(f"device_data: {device_data}")

#                 if not device_data:
#                     return
                
#                 target = device_data[0].get('TARGET')

#                 if not target:
#                     self.logger.debug("TARGET not found in request.")
#                     return

#                 device_type = data.get('CML_SUB_TYPE')

#                 if not device_type == "SENSOR":
#                     self.logger.debug("CML_SUB_TYPE not found in request.")
#                     continue

#                 provision_device_cache.append(device_data[0])
#                 self.logger.info("provision_device_cache### : " + str(provision_device_cache))

#                 keys = DEVICE_KEYS.get(device_type, [])
#                 aqi_score = await self.get_aqi_score(data)
#                 aqi_cat_dict = await self.get_aqi_cat_dict(aqi_score)

#                 update_data = {
#                     "RESPONSIBLE_POLLUTANT": "", #self.get_responsible_pollutant(aqi_score),
#                     "AQI_CAT": aqi_cat_dict.get("AQI_CAT", ""),
#                     "AQI_CAT_COLOR": aqi_cat_dict.get("AQI_CAT_COLOR", ""),
#                 }

#                 for key in keys:
#                     if key in data:
#                         update_data[key] = data[key]

#                 await sensor_cache.generic_forward_propagate("Device", target, device_type, update_data)

#                 await sensor_cache.generic_backward_propagate(target, device_type, "Device")

#             await self.broadcast_sensor_response(device_type)
#             await SensorNotification.sensor_without_apf_notification(cache_data,provision_device_cache,dataArr)
#             await self.process_sensor_data()
#         except Exception as e:
#             self.logger.error(f"Error executing execute: {e}", exc_info=True)

#     async def process_sensor_data(self):
#         try:
#             property_level = await self.get_devices_by_level("Property", "SENSOR")
#             floor_level = await self.get_devices_by_level("Floor", "SENSOR")
#             room_level = await self.get_devices_by_level("Room", "SENSOR")
#             device_level = await self.get_devices_by_level("Device", "SENSOR")
#             final_data =[property_level,floor_level,room_level,device_level]
#             self.logger.log(12,f"final_data : {final_data}")
#             if final_data == []:
#                 return
#             for data in final_data:
#                 for item in data:
#                     # await Store_Graph_data.process(item)
#                     await InsertResetSensorData.insert_data_into_db(item)

#         except Exception as e:
#             self.logger.error(f"Error in process_sensor_data: {e}", exc_info=True)
        
#     async def broadcast_sensor_response(self, device_type):
#         try:
#             for level in ["Device", "Room", "Floor", "Property"]:
#                 await self.generate_level_response(level, device_type)
#         except Exception as e:
#             self.logger.error(f"Error in execute: {e}", exc_info=True)
            

#     async def generate_level_response(self, level_type, device_type):
#         res = []
#         try:
#             cache = await self.get_data(level_type)
#             for path, data in cache.items():
#                 devices = data.get("device", {})
#                 if device_type in devices:
#                     cache_device_data = devices[device_type]
#                     manipuated_cache_data = await self.manipulate_sensor_data(cache_device_data)
#                     db_device_data = await DBApi.get_static_tables(path, level_type)
#                     complete_device_data = {**db_device_data, **manipuated_cache_data}
#                     if complete_device_data:
#                         res.append(complete_device_data)
#             self.logger.debug(f"generate_{level_type.lower()}_response, res: {res}")
#             if res != []:
#                 await self.brodcast_senor_data(level_type, res)
#         except Exception as e:
#             self.logger.error(f"Error in generate_level_response for {level_type}: {e}", exc_info=True)
            
#     async def brodcast_senor_data(self,level_type,res):
#         try:
#             if level_type == "Device":
#                 await broadcast_response(self.req_obj, res, level_type.lower(), self.mqtt_client, "set_properties_device_hub")
#             else:
#                 await broadcast_response(self.req_obj, res, level_type.lower(), self.mqtt_client, "aqi_score")
#         except Exception as e:
#             self.logger.error(f"Error in brodcast_senor_data: {e}", exc_info=True)

    
#     async def manipulate_sensor_data(self, cache_device_data):
#         try:
#             self.logger.debug(f"cache_device_data: {cache_device_data}")

#             KEYS = {
#                 "TVOC_AQI", "PM25_AQI", "PM10_AQI", "CO2_AQI", "CO_AQI",
#                 "TEMPERATURE", "HUMIDITY", "PM25", "PM10", "TVOC", "CO2", "CO",
#                 "NO2", "SO2", "O3", "AVG_TEMPERATURE", "AVG_HUMIDITY",
#                 "AVG_TVOC", "AVG_CO2", "AVG_PM25", "AVG_PM10", "PM1","CML_OAQI_AQI",
#                 "coConcentration","pm10Concentration","pm25Concentration","CML_TEMPERATURE","CML_RELATIVE_HUMIDITY",
#                 "CML_WIND_MPH","LOCATION_NAME","CML_WEATHER_TEXT","CML_WIND_DIRECTION","CML_TEMPERATURE_CELCIUS","CML_WIND",
#                 "CML_PRESSURE","CML_WIND_DIR"
#             }

#             concentrations = {
#                 key: cache_device_data.pop(key)
#                 for key in KEYS
#                 if key in cache_device_data
#             }

#             cache_device_data["CONCENTRATIONS"] = concentrations
#             return cache_device_data
#         except Exception as e:
#             self.logger.error("Error in manipulate_sensor_data {e}", exc_info=True)

#     async def get_aqi_score(self, data):
#         try:
#             aqi_score = data.get("AQI_SCORE")
#             if aqi_score is None:
#                 self.logger.debug("AQI_SCORE not found in request.")
#                 return -1 
#             return aqi_score
#         except Exception as e:
#             self.logger.error(f"Error in get_aqi_score: {e}", exc_info=True)
#             return -1

#     async def get_aqi_cat_dict(self, aqi_score):
#         try:
#             for aqi_dict in CacheSensorData.__aqi_cat_list:
#                 if aqi_score >= aqi_dict["min"]-0.5 and aqi_score < aqi_dict["max"] + 0.5:
#                     return aqi_dict
#                 else:
#                     continue
#         except Exception as e:
#             self.logger.error("Error in get_aqi_cat_dict {e}", exc_info=True)
#             return {}
        