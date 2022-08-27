from time import sleep
import requests
import json
from datetime import datetime, timezone
import os

class Clockify:

    def __init__(self):
        self.url = "https://api.clockify.me/api/v1"
        self.api_key= os.environ.get("CLOCKIFY_API")
        assert(self.api_key is not None)

    def connect(self):
        self.header = {'x-api-key': self.api_key}
        r = requests.get('{}/user'.format(self.url), headers=self.header)
        r = json.loads(r.content)
        # print(r)
        
        self.wsId = r["defaultWorkspace"]
        self.userId = r["id"]

        self.projects = {}
        r = requests.get('{}/workspaces/{}/projects'.format(self.url, self.wsId), headers=self.header)
        r = json.loads(r.content)
        # print(r)
        for i in r:
            self.projects[i["id"]] = i["name"]

    def now():
        now = datetime.now(timezone.utc)
        now = now.replace(microsecond=0)
        return now

    def datetime2ISO(now):
        now = now.isoformat().replace("+00:00", "Z")
        return now

    def ISO2datetime(dt_str):
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def getActiveEntries(self):
        r = requests.get('{}/workspaces/{}/user/{}/time-entries?in-progress=1'.format(self.url, self.wsId, self.userId), headers=self.header)
        r = json.loads(r.content)
        return r
    
    def getAllEntries(self):
        r = requests.get('{}/workspaces/{}/user/{}/time-entries'.format(self.url, self.wsId, self.userId), headers=self.header)
        r = json.loads(r.content)
        return r

    def startEntry(self, id=None):
        body = {"start": Clockify.datetime2ISO(Clockify.now()) }
        if id is not None:
            body["projectId"] = id
        r = requests.post('{}/workspaces/{}/time-entries'.format(self.url, self.wsId), headers=self.header, json=body)
        print(r.content)

    def stopActiveEntry(self):
        body = {"end": Clockify.datetime2ISO(Clockify.now()) }
        r = requests.patch('{}/workspaces/{}/user/{}/time-entries'.format(self.url, self.wsId, self.userId), headers=self.header, json=body)
        print(r.content)
        