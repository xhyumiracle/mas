
from mas.message import Message, pprint_messages
import json

def test_message():
    m1 = Message(role="user", content="Query: What is this?")
    m2 = Message(role="assistant", content="This is a sample test case.")

    # print(json.dumps([x.to_dict() for x in [m1,m2]], indent=2))
    pprint_messages([m1,m2])