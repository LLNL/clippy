from clippy.serialization import encode_clippy_json, decode_clippy_json, ClippySerializable
from clippy import config
import json

class TestType(ClippySerializable):
    def __init__(self, **kwargs):
        super().__init__()
        self._state.update(kwargs)

    def __str__(self):
        return str(self._state)

class OtherType(ClippySerializable):
    def __init__(self, path):
        super().__init__()
        self._state["path"] = path
    def __str__(self):
        return str(self._state)

print(OtherType.__dict__)

config._dynamic_types["TestType"] = TestType
config._dynamic_types["OtherType"] = OtherType

o1 = TestType(hello="world",testing=123)
o2 = OtherType("/some/path/for/testing")

print("o1:", o1)
print("o2:", o2)

for o in [o1,o2]:
    obj_graph = {"A":{"B": o, "C":123}, "D":[o,o]}
    j = json.dumps(obj_graph, default=encode_clippy_json)
    print(f"{o.__class__.__name__} encoded {type(j)}:",j)
    j = json.loads(j, object_hook=decode_clippy_json)
    print(f"{j.__class__.__name__} decoded {type(j)}:",j)
    print(j["A"]["B"])

