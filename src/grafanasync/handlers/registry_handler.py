#!/usr/bin/env python

import os
import json
import datetime
from grafanasync.handlers import alchemyencoder, dashboardItemDecoder


class Registry:
    def __init__(self,workdir):
        self._registry_dir=workdir
        if not os.path.isdir(self._registry_dir):
            mode = 0o777
            os.makedirs(workdir, mode,exist_ok=True)
        self._datefile=os.path.join(self._registry_dir,"date.json")
        self._commitfile=os.path.join(self._registry_dir,"commit_sha.json")
        self._foldersfile=os.path.join(self._registry_dir,"folders.json")
        self._dashboardsfile=os.path.join(self._registry_dir,"dashboards.json")
        self._date=None
        self._commit_sha=None
        self._folders=[]
        self._dashboards=[]
    
    @property
    def registry_dir(self):
        return self._registry_dir
    
    @property
    def date(self):
        return self._date
    
    @property
    def commit_sha(self):
        return self._commit_sha
    
    @property
    def folders(self):
        return self._folders
    
    @property
    def dashboards(self):
        return self._dashboards
    
    def persist_folders(self,folders):
        if type(folders) is list:
            #if os.path.isfile(self._foldersfile):
            #    os.remove(self._foldersfile)
            fp=open(self._foldersfile,'w')
            json.dump([f.toDict() for f in folders],fp=fp,default=alchemyencoder)
            fp.close()
            self._folders=self.get_folders()
        else:
            print("wtf")
    
    def persist_commit(self,commitsha):
        jsonstr={"register_commit_sha": commitsha}
        #if os.path.isfile(self._commitfile):
        #    os.remove(self._commitfile)
        fp=open(self._commitfile,'w')
        json.dump(jsonstr,fp)
        fp.close()
        self._commit_sha=self.get_commit()
    
    def persist_date(self, date):
        jsonstr={"register_date": datetime.datetime.strftime(date, "%Y-%m-%d %X")}
        #if os.path.isfile(self._datefile):
        #    os.remove(self._datefile)
        fp=open(self._datefile,'w')
        json.dump(jsonstr,fp)
        fp.close()
        self._date=self.get_date()
    
    def persist_dashboards(self,dashboards):
        if type(dashboards) is list:
            #if os.path.isfile(self._dashboardsfile):
            #    os.remove(self._dashboardsfile)
            fp=open(self._dashboardsfile,'w')
            json.dump([d.toDict() for d in dashboards],fp=fp,default=alchemyencoder)
            fp.close()
            self._dashboards=self.get_dashboards()
        else:
            print("wtf")
    
    def rehydrate(self):
        self._date=self.get_date()
        self._commit_sha=self.get_commit()
        self._folders=self.get_folders()
        self._dashboards=self.get_dashboards()
    
    def get_commit(self):
        if os.path.isfile(self._commitfile):
            # JSON file
            f = open (self._commitfile, "r")
            data = json.loads(f.read())
            commitstr=data['register_commit_sha']
            f.close()
            if not commitstr is None and commitstr != "":
                return commitstr
        return None
    
    def get_date(self):
        if os.path.isfile(self._datefile):
            # JSON file
            f = open (self._datefile, "r")
            data = json.loads(f.read())
            datestr=data['register_date']
            f.close()
            if not datestr is None and datestr != "":
                date=datetime.datetime.strptime(datestr, "%Y-%m-%d %X")
                return date
        return None
    
    def get_folders(self):
        folders=[]
        if os.path.isfile(self._foldersfile):
            # JSON file
            f = open (self._foldersfile, "r")
            data = json.loads(f.read())
            f.close()
            for folder in data:
                folders.append(dashboardItemDecoder(folder))
        return folders
    
    def get_dashboards(self):
        dashboards=[]
        if os.path.isfile(self._dashboardsfile):
            # JSON file
            f = open (self._dashboardsfile, "r")
            data = json.loads(f.read())
            f.close()            
            for dashboard in data:
                dashboards.append(dashboardItemDecoder(dashboard))
        return dashboards
    
    def remove_folder(self, uid):
        for f in list(self._folders):
            if f.uid == uid:
                self.remove_dashboard_in_folder(uid)
                self._folders.remove(f)
    
    def remove_dashboard(self, uid): 
        for d in list(self._dashboards):
            if d.uid == uid:
                self._dashboards.remove(d)
    
    def remove_dashboard_in_folder(self, uid): 
        for d in list(self._dashboards):
            if d.folder_uid == uid:
                self._dashboards.remove(d)

    def print(self):
        print([f for f in self._folders])
        print([d for d in self._dashboards])
        print(self._date)
        print(self._commit_sha)