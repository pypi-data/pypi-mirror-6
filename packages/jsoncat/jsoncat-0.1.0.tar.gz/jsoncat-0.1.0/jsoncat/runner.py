import sys
import json

def execute_from_cli():
  for line in sys.stdin.readlines():
    parsed = json.loads(line)
    print json.dumps(parsed, indent=2, sort_keys=True)
