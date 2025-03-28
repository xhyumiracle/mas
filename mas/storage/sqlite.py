import json
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Any, Dict, List, Tuple, Optional
from mas.graph.types import NodeId
from mas.storage.base import Storage

Base = declarative_base()

class Entry(Base):
    __tablename__ = 'agent_sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    caller = Column(String)
    callee = Column(String)
    action = Column(String)
    data = Column(Text)  # Store as JSON
    timestamp = Column(String)

class SqliteStorage(Storage):
    def __init__(self, table_name: str = "agent_sessions", db_file: str = "tmp/agent_storage.db"):
        self.engine = create_engine(f"sqlite:///{db_file}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_entry(self, entry: Dict[str, Any]) -> None:
        session = self.Session()
        entry_row = Entry(
            caller=entry["caller"],
            callee=entry["callee"],
            action=entry["action"],
            data=json.dumps(entry["data"]),
            timestamp=entry["timestamp"]
        )
        session.add(entry_row)
        session.commit()
        session.close()

    def get_entries_by_caller(self, caller: NodeId) -> List[Dict[str, Any]]:
        session = self.Session()
        entries = session.query(Entry).filter_by(caller=caller).all()
        session.close()
        return [self._row_to_dict(e) for e in entries]

    def get_entries_by_callee(self, callee: NodeId) -> List[Dict[str, Any]]:
        session = self.Session()
        entries = session.query(Entry).filter_by(callee=callee).all()
        session.close()
        return [self._row_to_dict(e) for e in entries]

    def get_entry(self, caller: NodeId, callee: NodeId, action: str) -> Optional[Dict[str, Any]]:
        session = self.Session()
        entry = session.query(Entry).filter_by(caller=caller, callee=callee, action=action).first()
        session.close()
        return self._row_to_dict(entry) if entry else None

    def _row_to_dict(self, entry: Entry) -> Dict[str, Any]:
        return {
            "caller": entry.caller,
            "callee": entry.callee,
            "action": entry.action,
            "data": json.loads(entry.data),
            "timestamp": entry.timestamp
        }
