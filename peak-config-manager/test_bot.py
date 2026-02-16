import urllib.request
import json

url = "http://localhost:5003/message"

payload = {
    "input": "change chat maxUser to 50"
}

headers = {
    'Content-Type': 'application/json'
}

print(f"Requesting: {url}")
print(f"Payload: {json.dumps(payload)}")

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        response_body = response.read().decode('utf-8')
        result = json.loads(response_body)
        
        print("\n" + "="*40)
        print("SUCCESS! Bot Response:")
        print("="*40)
        print(json.dumps(result, indent=2))
        print("="*40)

except urllib.error.HTTPError as e:
    print(f"\nServer Error (HTTP {e.code}):")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"\nConnection Error: {e}")