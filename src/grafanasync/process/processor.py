#!/usr/bin/env python

import os
import json
from grafanasync.util import g_logger


logger = g_logger.get_logger()

class Processor:
    def __init__(self, grafanadbhandler, grafanaapihandler, git, registry,gitregistry,grafanaregistry):
        self._gdbh=grafanadbhandler
        self._gapih=grafanaapihandler
        self._git=git
        self._registry=registry
        self._gitregistry=gitregistry
        self._grafanaregistry=grafanaregistry

    def processChanges(self, collector):
        self.processGitDeleteActions(collector.git_delete_actions)
        self.processGrafanaDeleteActions(collector.grafana_delete_actions)
        self.processGitActions(collector.git_create_actions)
        self.processGrafanaActions(collector.grafana_create_actions,False)
        self.processGitActions(collector.git_update_actions)
        self.processGrafanaActions(collector.grafana_update_actions,True)

    def write_file(self, uid,directory,json_item):
        f = os.path.join(directory, uid + ".json")
        fp=open(f,'w')
        json.dump(json_item,fp=fp)
        fp.close()

    def remove_file(self, uid, directory):
        for filename in os.listdir(directory):
            if uid in filename: 
                f = os.path.join(directory, filename)
                os.remove(f)

    def check_dir(self,directory):
        if not os.path.isdir(directory):
            mode = 0o777
            os.makedirs(directory, mode,exist_ok=True)

    def store_folder_in_grafana(self,folders_directory,uid):
        filepath = os.path.join(folders_directory, uid + ".json")
        f = open (filepath, "r")
        data = json.loads(f.read())
        f.close() 
        resp = self._gapih.create_folder(data["title"],data["uid"])
        self._gdbh.sync_dashboard_item(data["uid"],data["created"],data["updated"])
    
    def store_dashboard_in_grafana(self,dashboards_directory,uid,title):
        filepath = os.path.join(dashboards_directory, uid + ".json")
        f = open (filepath, "r")
        data = json.loads(f.read())
        f.close() 
        folder_id=None
        folder_uid=data["meta"]["folderUid"]
        resp1=self._gapih.get_folder(folder_uid)
        if resp1:
            folder_id=resp1["id"]
        resp = self._gapih.create_dashboard(data,uid,title,folder_id,folder_uid)
        self._gdbh.sync_dashboard_item(data["dashboard"]["uid"],data["meta"]["created"],data["meta"]["updated"])

    def processGitDeleteActions(self, gitDeleteActions):
        folders_directory=os.path.join(self._git.repo_dir,"folders")
        dashboards_directory=os.path.join(self._git.repo_dir,"dashboards")
        if os.path.exists(folders_directory) == True :
            for fda in gitDeleteActions["folders"]:
                self.remove_file(fda.uid,folders_directory)
        if os.path.exists(dashboards_directory) == True :    
            for dda in gitDeleteActions["dashboards"]:
                self.remove_file(dda.uid,dashboards_directory)

    def processGitActions(self, gitActions):
        folders_directory=os.path.join(self._git.repo_dir,"folders")
        dashboards_directory=os.path.join(self._git.repo_dir,"dashboards")
        self.check_dir(folders_directory)
        self.check_dir(dashboards_directory)
        for fda in gitActions["folders"]:
            folder=self._gapih.get_folder(fda.uid)
            print("folders_directory:",folders_directory)
            self.write_file(fda.uid,folders_directory,folder)
        for dda in gitActions["dashboards"]:
            dashboard=self._gapih.get_dashboard(dda.uid)
            self.write_file(dda.uid,dashboards_directory,dashboard)

    def processGrafanaDeleteActions(self, grafanaDeleteActions):
        for fda in grafanaDeleteActions["folders"]:
            self._gapih.delete_folder(fda.uid)
        for dda in grafanaDeleteActions["dashboards"]:
            self._gapih.delete_dashboard(dda.uid)

    def processGrafanaActions(self, grafanaActions,update):
        folders_directory=os.path.join(self._git.repo_dir,"folders")
        dashboards_directory=os.path.join(self._git.repo_dir,"dashboards")
        for fda in grafanaActions["folders"]:
            self.store_folder_in_grafana(folders_directory, fda.uid)
        for dda in grafanaActions["dashboards"]:
            if update == True:
                self._gapih.delete_dashboard(dda.uid)
            self.store_dashboard_in_grafana(dashboards_directory, dda.uid,dda.title)

   