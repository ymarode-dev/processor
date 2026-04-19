import asyncio
import json
import redis.asyncio as redis

# ---------------- REDIS CLIENT ----------------
class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host="localhost", port=6379, decode_responses=True, db=1)

    async def hset(self, name, key, value):
        await self.client.hset(name, key, json.dumps(value))

    async def hget(self, name, key):
        val = await self.client.hget(name, key)
        return json.loads(val) if val else None

    async def hgetall(self, name):
        data = await self.client.hgetall(name)
        return {k: json.loads(v) for k, v in data.items()}

    async def hdel(self, name, key):
        await self.client.hdel(name, key)

# ---------------- CACHE BUILDER ----------------
class InitRedisCache(RedisClient):
    def __init__(self):
        super().__init__()

    async def get_node(self, level, path):
        return await self.hget(level, path)

    async def set_node(self, level, path, value):
        await self.hset(level, path, value)

    async def delete_node(self, level, path):
        await self.hdel(level, path)

    # -------- Node Enrichment --------
    def enrich_node(self, node, parent=None):
        node.setdefault("device", {})
        node.setdefault("children", [])
        if parent is not None:
            node["parent"] = parent
        else:
            node.setdefault("parent", None)
        return node

    # -------- Add Child + Parent Link --------
    async def add_child(self, parent_level, parent_path, child_level, child_path):
        parent = await self.get_node(parent_level, parent_path) or {}
        parent = self.enrich_node(parent)

        if child_path not in parent["children"]:
            parent["children"].append(child_path)

        await self.set_node(parent_level, parent_path, parent)

        child = await self.get_node(child_level, child_path) or {}
        child = self.enrich_node(child, parent=parent_path)

        await self.set_node(child_level, child_path, child)

    # -------- Remove Child --------
    async def remove_child(self, parent_level, parent_path, child_path):
        parent = await self.get_node(parent_level, parent_path)
        if not parent:
            return

        if child_path in parent.get("children", []):
            parent["children"].remove(child_path)
            await self.set_node(parent_level, parent_path, parent)

    # -------- Dummy State Builder --------
    def build_state(self, subtype):
        import time
        # ---- Default States (simplified but extensible) ----
        if subtype == "LIGHT":
            return {
                "_id": 0,
                "STATE": 0,
                "SETPOINT": 0,
                "STATUS": 1,
                "BRIGHTNESS": 0,
                "HUE": -1,
                "SATURATION": -1,
                "LIGHTNESS": -1,
                "ELEM_TYPE": "LIGHT"
            }

        elif subtype == "SWITCH":
            return {
                "_id": 0,
                "STATE": 1,
                "STATUS": 1,
                "SETPOINT": 0,
                "ledBlink": 0,
                "ELEM_TYPE": "SWITCH"
            }

        elif subtype == "MUSIC":
            return {
                "_id": 0,
                "STATE": 1,
                "STATUS": 1,
                "MUTE": 0,
                "TRACK_COUNT": -1,
                "CURRENT_TRACK_TITLE": "",
                "NEXT_TRACK_TITLE": "",
                "ELEM_TYPE": "MUSIC"
            }

        elif subtype == "SENSOR":
            return {
                "AQI_SCORE": -1,
                "TEMPERATURE": -1,
                "HUMIDITY": -1,
                "LAST_SYNC_TIME": int(time.time() * 1000),
                "STATUS": 1,
                "ELEM_TYPE": "AQI"
            }

        elif subtype == "HVAC":
            return {
                "_id": 0,
                "CML_STATE": 1,
                "CML_STATUS": 1,
                "CML_MODE": 0,
                "CML_SET_POINT": -1,
                "ELEM_TYPE": "HVAC"
            }

        else:
            return {"_id": 0}

    # -------- Insert Device --------
    async def upsert_device(self, entry):
        path_parts = entry['TARGET'].strip('/').split('/')

        property_path = f"/{path_parts[0]}"
        floor_path = f"{property_path}/{path_parts[1]}"
        room_path = f"{floor_path}/{path_parts[2]}"
        device_path = f"{room_path}/{path_parts[3]}"

        subtype = entry["CML_SUB_TYPE"]
        state = self.build_state(subtype)

        device_node = await self.get_node("Device", device_path) or {}
        device_node = self.enrich_node(device_node, parent=room_path)
        device_node["device"][subtype] = state
        await self.set_node("Device", device_path, device_node)

        await self.add_child("Property", property_path, "Floor", floor_path)
        await self.add_child("Floor", floor_path, "Room", room_path)
        await self.add_child("Room", room_path, "Device", device_path)
        await self.recompute_upwards(device_path, subtype)

    # -------- Delete Device --------
    async def delete_device(self, target):
        parts = target.strip("/").split("/")

        property_path = f"/{parts[0]}"
        floor_path = f"{property_path}/{parts[1]}"
        room_path = f"{floor_path}/{parts[2]}"
        device_path = f"{room_path}/{parts[3]}"

        # Remove from Room children
        await self.remove_child("Room", room_path, device_path)

        # Delete device node
        await self.delete_node("Device", device_path)

# ---------------- DUMMY DATA ----------------
devices = [
    {"TARGET": "/P1/F1/R1/D1", "CML_SUB_TYPE": "LIGHT"},
    {"TARGET": "/P1/F1/R1/D2", "CML_SUB_TYPE": "LIGHT"},
]

# ---------------- RUN SCRIPT ----------------
async def main():
    cache = InitRedisCache()

    print("\n=== STEP 1: Initial Structure ===")
    for d in devices:
        await cache.upsert_device(d)

    print(await cache.hgetall("Room"))

    print("\n=== STEP 2: Add New Device ===")
    await cache.upsert_device({"TARGET": "/P1/F1/R1/D3", "CML_SUB_TYPE": "LIGHT"})
    print(await cache.hget("Room", "/P1/F1/R1"))

    print("\n=== STEP 3: Delete Device D2 ===")
    await cache.delete_device("/P1/F1/R1/D2")
    print(await cache.hget("Room", "/P1/F1/R1"))

    print("\n=== FINAL STATE ===")
    print("Device:", await cache.hgetall("Device"))
    print("Room:", await cache.hgetall("Room"))

if __name__ == "__main__":
    asyncio.run(main())
