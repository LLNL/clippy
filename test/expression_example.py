from clippy.expression import Selector
from clippy.serialization import encode_clippy_json
import json

nodes = Selector(None, "nodes")
edges = Selector(None, "edges")

exp = nodes.kcore > 10
print(json.dumps(exp, default=encode_clippy_json))

exp = nodes.age > 10, (edges.distance > 0.20) & (edges.distance < 0.8), nodes.likes == "stuff"
print(json.dumps(exp, default=encode_clippy_json))