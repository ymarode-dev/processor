import logging

class MqttInvoker:
    _logger = logging.getLogger("MqttInvoker")
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    async def process_message(self, topic, payload):
        self._logger.info(f"Processing message on topic {topic} with payload: {payload}")