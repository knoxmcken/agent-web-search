import http.client
import json

conn = http.client.HTTPSConnection("google.serper.dev")
payload = json.dumps({
      "q": "apple inc"
      })
headers = {
          'X-API-KEY': 'SERPER_API_KEY' 
            'Content-Type': 'application/json'
            }
conn.request("POST", "/search", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
