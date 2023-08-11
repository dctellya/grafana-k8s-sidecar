#!/usr/bin/env python
from grafana_client import GrafanaApi
import json
from json.decoder import JSONDecodeError
import sys

class GrafanaAPIHandler:
    
    def __init__(self, grafana_base_url, grafana_user, grafana_pass):
        self._grafana_base_url=grafana_base_url
        self._grafana_user=grafana_user
        self._grafana_pass=grafana_pass

        self._client=GrafanaApi.from_url(
            url=grafana_base_url,
            credential=(grafana_user,grafana_pass)
            )
    
    @property
    def client(self):
        return self._client
  
    def get_all_folders(self):
        print("## All folders on grafana", file=sys.stderr)
        folders = self.client.folder.get_all_folders()
        return folders

    def create_folder(self, title, uid=None):
        json_data = dict(title=title)
        if uid is not None:
            json_data["uid"] = uid
        return self.client.client.POST("/folders", json=json_data)

    def update_folder(self, uid, title=None, overwrite=False, new_uid=None):
        body = {}
        if new_uid:
            body["uid"] = new_uid
        if title:
            body["title"] = title
        if overwrite:
            body["overwrite"] = True

        path = "/folders/%s" % uid
        r = self.client.client.PUT(path, json=body)
        return r

    def delete_folder(self, uid):
        print("uid:",uid)
        try:
            r=self.client.folder.delete_folder(uid)
        except JSONDecodeError as e:
            pass

    def get_folder(self, uid):
        return self.client.folder.get_folder(uid)
    
    def get_all_dashboards(self):
        print("## All Dashboards on grafana", file=sys.stderr)
        dashboards = self.client.search.search_dashboards(
            type_="dash-db",
        )
        #print(json.dumps(dashboards, indent=2))
        return dashboards
    
    def get_dashboard(self, uid):
        return self.client.dashboard.get_dashboard(uid)
    
    def delete_dashboard(self, uid):
        return self.client.dashboard.delete_dashboard(uid)
    
    def create_dashboard(self, dashboard,uid,title,folder_id=None,folder_uid=None,message=None,overwrite=False):
        body = {}
        if folder_id:
            body["folderId"] = folder_id
        if folder_uid:
            body["folderUid"] = folder_uid
        if overwrite:
            body["overwrite"] = True
        if message:
            body["message"] = message
        body["uid"] = uid      
        print("dashboard", dashboard["dashboard"])
        dashboard["dashboard"]["id"]=None
        body["dashboard"]=dashboard["dashboard"]

        #print(body)
        #headers = {
        #  'Accept': 'application/json',
        #  'Content-Type': 'application/json',
        #}
        r = self.client.client.POST("/dashboards/db", json=body)
        print(r)
        return r
        
    