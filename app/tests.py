from django.test import TestCase
import requests

# Create your tests here.
import requests

import requests,json
import ast

print(ast.literal_eval("{'http': None,'https': None,}"))

url = "http://127.0.0.1:7000/opsbase/app/menu/?access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjIyMjEyOTk4LCJlbWFpbCI6IiJ9.vDJPoy8JKwI6BEeIYdo85pjkFnOWhjyCzQ5mVVywZxQ"

payload = {}
headers = {}
proxies = {
    "http": None,
    "https": None,
}

response = requests.get(url,proxies=proxies)

print(response.text)
