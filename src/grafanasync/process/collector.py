#!/usr/bin/env python

from time import sleep

class Collector:
    def __init__(self, grafanadbhandler, grafanaapihandler, git, registry,gitregistry,grafanaregistry):
        self._gdbh=grafanadbhandler
        self._gapih=grafanaapihandler
        self._git=git
        self._registry=registry
        self._gitregistry=gitregistry
        self._grafanaregistry=grafanaregistry
        self._grafana_delete_actions={"folders":[],"dashboards":[]}
        self._git_delete_actions={"folders":[],"dashboards":[]}
        self._grafana_create_actions={"folders":[],"dashboards":[]}
        self._git_create_actions={"folders":[],"dashboards":[]}
        self._grafana_update_actions={"folders":[],"dashboards":[]}
        self._git_update_actions={"folders":[],"dashboards":[]}
        #self._changes={'git':{'folders':{'create':[],'update':[],'delete':[]},'dashboards':{'create':[],'update':[],'delete':[]}},'grafana':{'folders':{'create':[],'update':[],'delete':[]},'dashboards':{'create':[],'update':[],'delete':[]}}}

    @property
    def git_delete_actions(self):
        return self._git_delete_actions
    
    @property
    def git_create_actions(self):
        return self._git_create_actions
    
    @property
    def git_update_actions(self):
        return self._git_update_actions
    
    @property
    def grafana_delete_actions(self):
        return self._grafana_delete_actions
    
    @property
    def grafana_create_actions(self):
        return self._grafana_create_actions
    
    @property
    def grafana_update_actions(self):
        return self._grafana_update_actions
    
    def collectChanges(self):
        #dump grafana registry
        self._grafanaregistry.persist_folders(self._gdbh.get_all_folders())
        self._grafanaregistry.persist_dashboards(self._gdbh.get_all_dashboards())
        #load git registry
        self._gitregistry.rehydrate()
        #load registry
        self._registry.rehydrate()
        
        print("_gitregistry.folders - len: ", len(self._gitregistry.folders))
        print("_gitregistry.dashboards - len: ",len(self._gitregistry.dashboards))
        print("_registry.folders - len",len(self._registry.folders))
        print("_registry.dashboards - len",len(self._registry.dashboards))
        print("_grafanaregistry.folders - len",len(self._grafanaregistry.folders))
        print("_grafanaregistry.dashboards - len",len(self._grafanaregistry.dashboards))

        self.process_git_deletes_over_grafana()
        self.process_grafana_deletes_over_git()
        self.process_folder_creates_and_updates()
        self.process_dashboards_creates_and_updates()
        ###################################
        #TODO: Lets do rogue git stuff
        ###################################

    def process_git_deletes_over_grafana(self):
        for f in self._registry.folders:
            index = -1
            i=0
            for folder in self._gitregistry.folders:
                i=i+1
                if folder.uid == f.uid:
                    index=i
                    break
            if index == -1:
                print('folder to delete in grafana: %s',f.uid )
                self.grafana_delete_actions["folders"].append(f)
                self.remove_git_dashboards_associated_to_deleted_folder(f.uid)
                self._grafanaregistry.remove_folder(f.uid)
                self._registry.remove_folder(f.uid)
                
        for d in self._registry.dashboards:
            index = -1
            i=0
            for dashboard in self._gitregistry.dashboards:
                i=i+1
                if dashboard.uid == d.uid:
                    index=i
                    break
            if index == -1:
                print('dashboard to delete in grafana: %s',d.uid )
                self.grafana_delete_actions["dashboards"].append(d)
                self._grafanaregistry.remove_dashboard(d.uid)
                self._registry.remove_dashboard(d.uid)

    def remove_git_dashboards_associated_to_deleted_folder(self,fuid):
        git_dashboards=self._gitregistry.dashboards
        print("remove_git_dashboards_associated_to_deleted_folder: git_dashboards - len: ",len(git_dashboards))
        print("remove_git_dashboards_associated_to_deleted_folder: _gitregistry.dashboards - len: ",len(self._gitregistry.dashboards))
        for dashboard in git_dashboards:
            print(dashboard)
            if dashboard.folder_uid == fuid:
                print('folder removed -> dashboard to delete in git: %s',dashboard.uid )
                self._git_delete_actions["dashboards"].append(dashboard)
                self._gitregistry.remove_dashboard(dashboard.uid)
                self._registry.remove_dashboard(dashboard.uid)
    
    def process_grafana_deletes_over_git(self):
        for f in self._registry.folders:
            index = -1
            i=0
            for folder in self._grafanaregistry.folders:
                i=i+1
                if folder.uid == f.uid:
                    index=i
                    break
            if index == -1:
                print('folder to delete in git: %s',f.uid )
                print("process_grafana_deletes_over_git: _gitregistry.folders - len: ", len(self._gitregistry.folders))
                print("process_grafana_deletes_over_git: _gitregistry.dashboards - len: ",len(self._gitregistry.dashboards))
                print("process_grafana_deletes_over_git: _registry.folders - len",len(self._registry.folders))
                print("process_grafana_deletes_over_git: _registry.dashboards - len",len(self._registry.dashboards))
                self._git_delete_actions["folders"].append(f)
                self.remove_git_dashboards_associated_to_deleted_folder(f.uid)
                self._gitregistry.remove_folder(f.uid)
                self._registry.remove_folder(f.uid)
        for d in self._registry.dashboards:
            index = -1
            i=0
            for dashboard in self._grafanaregistry.dashboards:
                i=i+1
                if dashboard.uid == d.uid:
                    index=i
                    break
            if index == -1:
                print('dashboard to delete in git: %s',d.uid )
                self._git_delete_actions["dashboards"].append(d)
                self._gitregistry.remove_dashboard(d.uid)
                self._registry.remove_dashboard(d.uid)
    
    def process_folder_creates_and_updates(self):
        git_folders=self._gitregistry.folders
        for f in self._grafanaregistry.folders:
            index = -1
            i=0
            for folder in self._gitregistry.folders:
                i=i+1
                if folder.uid == f.uid:
                    index = i
                    if folder.updated > f.updated:
                        print('folder to update in grafana: %s',f.uid )
                        self._grafana_update_actions["folders"].append(f)
                    elif folder.updated == f.updated:
                        print('nothing to do: %s',f.uid )
                    else:
                        print('folder to update in git: %s',f.uid )
                        self._git_update_actions["folders"].append(f)
                    git_folders.remove(folder)
                    break
            if index == -1: #doesn't exist in git
                print('folder to create in git: %s',f.uid )
                self._git_create_actions["folders"].append(f)
        for f in git_folders:
            if not (any(folder.uid == f.uid for folder in self._grafanaregistry.folders)):
                print('folder to create in grafana: %s',f.uid )
                self._grafana_create_actions["folders"].append(f)
            else:
                print("why are you here:%s???",f.uid)
    
    def process_dashboards_creates_and_updates(self):
        git_dashboards=self._gitregistry.dashboards
        for d in self._grafanaregistry.dashboards:
            index = -1
            i=0
            for dashboard in self._gitregistry.dashboards:
                i=i+1
                if dashboard.uid == d.uid:
                    index = i
                    if dashboard.updated > d.updated:
                        print('dashboard to update in grafana: %s',d.uid )
                        self._grafana_update_actions["dashboards"].append(d)
                    elif dashboard.updated == d.updated:
                        print('nothing to do: %s',d.uid )
                    else:
                        print('dashboard to update in git: %s',d.uid )
                        self._git_update_actions["dashboards"].append(d)
                    git_dashboards.remove(dashboard)
                    break
            if index == -1: #doesn't exist in git
                print('dashboard to create in git: %s',d.uid )
                self._git_create_actions["dashboards"].append(d)
        for d in git_dashboards:
            if not (any(dashboard.uid == d.uid for dashboard in self._grafanaregistry.dashboards)):
                print('dashboard to create in grafana: %s',d.uid )
                self._grafana_create_actions["dashboards"].append(d)
            else:
                print("why are you here:%s",d.uid)
        
    def flush(self):
        self._grafana_delete_actions={"folders":[],"dashboards":[]}
        self._git_delete_actions={"folders":[],"dashboards":[]}
        self._grafana_create_actions={"folders":[],"dashboards":[]}
        self._git_create_actions={"folders":[],"dashboards":[]}
        self._grafana_update_actions={"folders":[],"dashboards":[]}
        self._git_update_actions={"folders":[],"dashboards":[]}