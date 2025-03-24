import redis
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from mas.graph.types import NodeId
from mas.storage.base import Storage  # assuming the interface class exists in agent_storage.py

class RedisStorage(Storage):
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    def add_entry(self, entry: Dict[str, Any]) -> None:
        entry_id = f"{entry['caller']}:{entry['callee']}:{entry['action']}:{entry['timestamp']}"

        # Store entry data
        self.r.set(entry_id, json.dumps(entry))

        # Index by caller (sorted by timestamp)
        caller_key = f"caller:{entry['caller']}"
        self.r.zadd(caller_key, {entry_id: datetime.fromisoformat(entry['timestamp']).timestamp()})

        # Index by callee
        callee_key = f"callee:{entry['callee']}"
        self.r.zadd(callee_key, {entry_id: datetime.fromisoformat(entry['timestamp']).timestamp()})

        # Direct lookup by (caller, callee, action)
        direct_key = f"entry:{entry['caller']}:{entry['callee']}:{entry['action']}"
        self.r.set(direct_key, entry_id)

    def get_entries_by_caller(self, caller: NodeId) -> List[Dict[str, Any]]:
        caller_key = f"caller:{caller}"
        entry_ids = self.r.zrange(caller_key, 0, -1)
        return [json.loads(self.r.get(entry_id)) for entry_id in entry_ids]

    def get_entries_by_callee(self, callee: NodeId) -> List[Dict[str, Any]]:
        callee_key = f"callee:{callee}"
        entry_ids = self.r.zrange(callee_key, 0, -1)
        return [json.loads(self.r.get(entry_id)) for entry_id in entry_ids]

    def get_entry(self, caller: NodeId, callee: NodeId, action: str) -> Optional[Dict[str, Any]]:
        direct_key = f"entry:{caller}:{callee}:{action}"
        entry_id = self.r.get(direct_key)
        if entry_id:
            return json.loads(self.r.get(entry_id))
        return None

    # def get_latest_entry_by_caller(self, caller: str) -> Optional[Dict[str, Any]]:
    #     caller_key = f"caller:{caller}"
    #     entry_ids = self.r.zrevrange(caller_key, 0, 0)  # reverse range to get latest
    #     if entry_ids:
    #         return json.loads(self.r.get(entry_ids[0]))
    #     return None

# TODO: validate this