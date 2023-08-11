import unittest
from unittest.mock import patch,MagicMock
import os
import shutil
import datetime
import json


from grafanasync import __main__
from grafanasync.util import GracefulKiller
from grafanasync.config import ConfigLoader
from grafanasync.handlers import Git
from grafanasync.handlers import Registry
from grafanasync.handlers import GrafanaAPIHandler
from grafanasync.handlers import GrafanaDBHandler
from grafanasync.process import Collector
from grafanasync.process import Processor
from grafanasync.process import Lock
from grafanasync.handlers import alchemyencoder, dashboardItemDecoder

class TestGrafanaSync(unittest.TestCase):
    
    def setWorkdir(self,testname):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",testname)
        if not os.path.isdir(workdir):
            mode = 0o777
            os.makedirs(workdir, mode,exist_ok=True)
        if not os.path.isdir(os.path.join(workdir,"registry")):
            mode = 0o777
            os.makedirs(os.path.join(workdir,"registry"), mode,exist_ok=True)
        if not os.path.isdir(os.path.join(workdir,"grafana_registry")):
            mode = 0o777
            os.makedirs(os.path.join(workdir,"grafana_registry"), mode,exist_ok=True)
        
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        if not os.path.isdir(os.path.join(repo_dir,"registry")):
            mode = 0o777
            os.makedirs(os.path.join(repo_dir,"registry"), mode,exist_ok=True)
        if not os.path.isdir(os.path.join(repo_dir,"dashboards")):
            mode = 0o777
            os.makedirs(os.path.join(repo_dir,"dashboards"), mode,exist_ok=True)
        if not os.path.isdir(os.path.join(repo_dir,"folders")):
            mode = 0o777
            os.makedirs(os.path.join(repo_dir,"folders"), mode,exist_ok=True)
        

        return workdir
        
    def tearDown(self):
        print("tearDown - In method", self._testMethodName)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        if os.path.isdir(workdir):
            shutil.rmtree(workdir)
            pass

    def setItUp(self,workdir,testName,to_add=""):
        print("setUp - In method", testName)
        test_comp = {}
        test_comp["workdir"]=workdir
        test_comp["killer"] = GracefulKiller()
        test_comp["configLoader"] = ConfigLoader()
        test_comp["configLoader"].workdir=workdir
        test_comp["repo_dir"]=os.path.join(test_comp["configLoader"].workdir,test_comp["configLoader"].git_repo_name)
        #self._git = Git(self._configLoader.git_repo_url,self._repo_dir, self._configLoader.git_user,self._configLoader.git_token)
        test_comp["git"]=self.getGitMock(test_comp["repo_dir"]) 
        test_comp["grafanaapihandler"] = self.getGrafanaAPIHandlerMock()
        test_comp["grafanadbhandler"] = self.getGrafanaDBHandlerMock(to_add)
        test_comp["registry"] = Registry(os.path.join(test_comp["configLoader"].workdir,"registry"))
        test_comp["gitregistry"] = Registry(os.path.join(test_comp["repo_dir"],"registry"))
        test_comp["grafanaregistry"] = Registry(os.path.join(test_comp["configLoader"].workdir,"grafana_registry"))
        
        test_comp["collector"]= Collector(test_comp["grafanadbhandler"],test_comp["grafanaapihandler"], test_comp["git"],test_comp["registry"],test_comp["gitregistry"],test_comp["grafanaregistry"])
        test_comp["processor"]= Processor(test_comp["grafanadbhandler"],test_comp["grafanaapihandler"],test_comp["git"], test_comp["registry"],test_comp["gitregistry"],test_comp["grafanaregistry"])
        test_comp["lock"]=Lock()
        return test_comp
    
    def getGitMock(self,repodir):
        git_instance = MagicMock(git_url="", repo_dir=repodir, git_user="", git_token="")  

        git_instance.clone.return_value = True
        git_instance.pull.return_value = True
        git_instance.push.return_value = True
        git_instance.stash.return_value = True
        git_instance.add_and_commit.return_value = True
        git_instance.get_local_short_sha_commit.return_value = "01808e5"
        git_instance.get_local_sha_commit.return_value = "01808e5532048b323c68f51e9a548b13af308bd7"
        git_instance.get_remote_sha_commit.return_value = "01808e5532048b323c68f51e9a548b13af308bd7"    
        return git_instance
    
    def get_all_dashboards_as_dbitem(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","dashboards.json")
        print("get_all_dashboards_as_dbitem:", dpath)
        dashboards=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()            
            for dashboard in data:
                dashboards.append(dashboardItemDecoder(dashboard))
        return dashboards

    def get_all_folders_as_dbitem(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","folders.json")
        print("get_all_folders_as_dbitem:", dpath)
        folders=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()
            for folder in data:
                folders.append(dashboardItemDecoder(folder))
        return folders
    
    def get_all_dashboards_as_dbitem(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","dashboards.json")
        dashboards=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()            
            for dashboard in data:
                dashboards.append(dashboardItemDecoder(dashboard))
        return dashboards

    def get_all_folders_as_dbitem(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","folders.json")
        folders=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()
            for folder in data:
                folders.append(dashboardItemDecoder(folder))
        return folders
    
    def get_all_folders_as_dbitem_one_folder(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","folders.json")
        folders=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()
            for folder in data:
                folders.append(dashboardItemDecoder(folder))

        #copy reosureces from one_folder 
           
        if not os.path.exists(os.path.join(workdir,"grafana_registry","enough.txt")):
            if os.path.exists(os.path.join(workdir,"grafana_registry")):
                shutil.rmtree(os.path.join(workdir,"grafana_registry"))
            shutil.copytree(os.path.join(dir_path,"resources","grafana_registry","one_folder"),os.path.join(workdir,"grafana_registry"))
        else:
            if os.path.exists(os.path.join(workdir,"grafana_registry")):
                shutil.rmtree(os.path.join(workdir,"grafana_registry"))
            shutil.copytree(os.path.join(dir_path,"resources","grafana_registry","one_folder_one_dashboard"),os.path.join(workdir,"grafana_registry"))
            os.close(os.open(os.path.join(workdir,"grafana_registry","enough.txt"), os.O_CREAT))
        
        return folders

    def get_all_dashboards_as_dbitem_one_folder(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","dashboards.json")
        dashboards=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()            
            for dashboard in data:
                dashboards.append(dashboardItemDecoder(dashboard))

        #copy reosureces from one_folder 
        if os.path.exists(os.path.join(workdir,"grafana_registry")):
            shutil.rmtree(os.path.join(workdir,"grafana_registry"))
        shutil.copytree(os.path.join(dir_path,"resources","grafana_registry","one_folder"),os.path.join(workdir,"grafana_registry"))
        return dashboards
     
    def get_all_dashboards_as_dbitem_one_folder_one_dash(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","dashboards.json")
        dashboards=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()            
            for dashboard in data:
                dashboards.append(dashboardItemDecoder(dashboard))

        #copy reosureces from one_folder 
        
        if os.path.exists(os.path.join(workdir,"grafana_registry")):
            shutil.rmtree(os.path.join(workdir,"grafana_registry"))
        shutil.copytree(os.path.join(dir_path,"resources","grafana_registry","one_folder_one_dashboard"),os.path.join(workdir,"grafana_registry"))
        os.close(os.open(os.path.join(workdir,"grafana_registry","enough.txt"), os.O_CREAT))
        return dashboards
    
    def get_all_folders_as_dbitem_empty(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","folders.json")
        folders=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()
            for folder in data:
                folders.append(dashboardItemDecoder(folder))

        #copy reosureces from one_folder 
        if os.path.exists(os.path.join(workdir,"grafana_registry")):
            shutil.rmtree(os.path.join(workdir,"grafana_registry"))
        shutil.copytree(os.path.join(dir_path,"resources","grafana_registry","empty"),os.path.join(workdir,"grafana_registry"))
        return folders
    
    def get_all_dashboards_as_dbitem_empty(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir = os.path.join(dir_path,"tmp/grafana_workdir/",self._testMethodName)
        dpath=os.path.join(workdir,"grafana_registry","dashboards.json")
        dashboards=[]
        if os.path.isfile(dpath):
            # JSON file
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close()            
            for dashboard in data:
                dashboards.append(dashboardItemDecoder(dashboard))

        #copy reosureces from one_folder 
        if os.path.exists(os.path.join(workdir,"grafana_registry")):
            shutil.rmtree(os.path.join(workdir,"grafana_registry"))
        shutil.copytree(os.path.join(dir_path,"resources","grafana_registry","empty"),os.path.join(workdir,"grafana_registry"))
        return dashboards
    
    def getGrafanaDBHandlerMock(self, to_add=""): 
        gdbh_instance=MagicMock()  
        if to_add == "one_folder":
            gdbh_instance.get_all_dashboards.side_effect=self.get_all_dashboards_as_dbitem_one_folder
            gdbh_instance.get_all_folders.side_effect=self.get_all_folders_as_dbitem_one_folder
            gdbh_instance.get_all_dashboards_updated_after_date.side_effect=self.get_all_dashboards_as_dbitem_one_folder
            gdbh_instance.get_all_folders_updated_after_date.side_effect=self.get_all_folders_as_dbitem_one_folder
        elif to_add == "one_folder_one_dashboard":
            gdbh_instance.get_all_dashboards.side_effect=self.get_all_dashboards_as_dbitem_one_folder_one_dash
            gdbh_instance.get_all_folders.side_effect=self.get_all_folders_as_dbitem_one_folder
            gdbh_instance.get_all_dashboards_updated_after_date.side_effect=self.get_all_dashboards_as_dbitem_one_folder_one_dash
            gdbh_instance.get_all_folders_updated_after_date.side_effect=self.get_all_folders_as_dbitem_one_folder
        elif to_add == "empty":
            gdbh_instance.get_all_dashboards.side_effect=self.get_all_dashboards_as_dbitem_empty
            gdbh_instance.get_all_folders.side_effect=self.get_all_folders_as_dbitem_empty
            gdbh_instance.get_all_dashboards_updated_after_date.side_effect=self.get_all_dashboards_as_dbitem_empty
            gdbh_instance.get_all_folders_updated_after_date.side_effect=self.get_all_folders_as_dbitem_empty
        else:
            gdbh_instance.get_all_dashboards.side_effect=self.get_all_dashboards_as_dbitem
            gdbh_instance.get_all_folders.side_effect=self.get_all_folders_as_dbitem
            gdbh_instance.get_all_dashboards_updated_after_date.side_effect=self.get_all_dashboards_as_dbitem
            gdbh_instance.get_all_folders_updated_after_date.side_effect=self.get_all_folders_as_dbitem
        

        gdbh_instance.sync_dashboard_item.return_value=True
        return gdbh_instance
    
    def getfolder(self,uid):
        dir_path=os.path.dirname(os.path.realpath(__file__))
        folder_path=os.path.join(dir_path,"resources/folders",uid + ".json")
        data = {}
        if os.path.isfile(folder_path):
            f = open (folder_path, "r")
            data = json.loads(f.read())
            f.close() 
        return data
    
    def getdashboard(self,uid):
        dir_path=os.path.dirname(os.path.realpath(__file__))
        dash_path=os.path.join(dir_path,"resources/dashboards",uid + ".json")
        data = {}
        if os.path.isfile(dash_path):
            f = open (dash_path, "r")
            data = json.loads(f.read())
            f.close() 
        return data

    def getGrafanaAPIHandlerMock(self): 
        gapih_instance=MagicMock()  
        gapih_instance.create_folder.return_value=True
        gapih_instance.delete_folder.return_value=True
        gapih_instance.get_folder.side_effect=self.getfolder
        gapih_instance.get_dashboard.side_effect=self.getdashboard
        gapih_instance.delete_dashboard.return_value=True
        gapih_instance.create_dashboard.return_value=True

        return gapih_instance

    def copyRegistryTo(self,from_dir,to_dir):
        shutil.copy(os.path.join(from_dir,"commit_sha.json"),os.path.join(to_dir,"commit_sha.json"))
        shutil.copy(os.path.join(from_dir,"dashboards.json"),os.path.join(to_dir,"dashboards.json"))
        shutil.copy(os.path.join(from_dir,"date.json"),os.path.join(to_dir,"date.json"))
        shutil.copy(os.path.join(from_dir,"folders.json"),os.path.join(to_dir,"folders.json"))

    def copyGitRegistryTo(self,from_dir,to_dir):
        shutil.copy(os.path.join(from_dir,"dashboards.json"),os.path.join(to_dir,"dashboards.json"))
        shutil.copy(os.path.join(from_dir,"date.json"),os.path.join(to_dir,"date.json"))
        shutil.copy(os.path.join(from_dir,"folders.json"),os.path.join(to_dir,"folders.json"))

    def copyGrafanaRegistryTo(self,from_dir,to_dir):  
        shutil.copy(os.path.join(from_dir,"dashboards.json"),os.path.join(to_dir,"dashboards.json"))
        shutil.copy(os.path.join(from_dir,"folders.json"),os.path.join(to_dir,"folders.json"))
    

    def test_add_folder_from_grafana_to_git(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))

        #setup initial state:
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","empty"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","one_folder"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","empty"),os.path.join(repo_dir,"registry"))
        test_comp=self.setItUp(workdir,self._testMethodName)
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),1)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        uid=test_comp["gitregistry"].get_folders()[0].uid
        dpath=os.path.join(test_comp["repo_dir"],"folders",uid + ".json")
        uid_fromfile=""
        if os.path.isfile(dpath):
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close() 
            uid_fromfile=data["uid"]
        self.assertEqual(uid,uid_fromfile)

    def test_add_dashboard_from_grafana_to_git(self):

        #setup initial state:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","one_folder"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","one_folder_one_dashboard"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","one_folder"),os.path.join(repo_dir,"registry"))
        if os.path.exists(os.path.join(repo_dir,"folders")):
            shutil.rmtree(os.path.join(repo_dir,"folders"))
        shutil.copytree(os.path.join(dir_path,"resources","folders"),os.path.join(repo_dir,"folders"))
        test_comp=self.setItUp(workdir,self._testMethodName)
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),1)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        uid=test_comp["gitregistry"].get_dashboards()[0].uid
        dpath=os.path.join(test_comp["repo_dir"],"dashboards",uid + ".json")
        uid_fromfile=""
        if os.path.isfile(dpath):
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close() 
            uid_fromfile=data["dashboard"]["uid"]
        self.assertEqual(uid,uid_fromfile)

    def test_delete_folder_from_grafana_to_git(self):
        #setup initial state:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","one_folder"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","empty"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","one_folder"),os.path.join(repo_dir,"registry"))
        if os.path.exists(os.path.join(repo_dir,"folders")):
            shutil.rmtree(os.path.join(repo_dir,"folders"))
        shutil.copytree(os.path.join(dir_path,"resources","folders"),os.path.join(repo_dir,"folders"))
        test_comp=self.setItUp(workdir,self._testMethodName)
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),1)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),0)
    
    def test_delete_dashboard_from_grafana_to_git(self):
        #setup initial state:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","one_folder_one_dashboard"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","one_folder"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","one_folder_one_dashboard"),os.path.join(repo_dir,"registry"))
        if os.path.exists(os.path.join(repo_dir,"folders")):
            shutil.rmtree(os.path.join(repo_dir,"folders"))
        shutil.copytree(os.path.join(dir_path,"resources","folders"),os.path.join(repo_dir,"folders"))
        if os.path.exists(os.path.join(repo_dir,"dashboards")):
            shutil.rmtree(os.path.join(repo_dir,"dashboards"))
        shutil.copytree(os.path.join(dir_path,"resources","dashboards"),os.path.join(repo_dir,"dashboards"))
        test_comp=self.setItUp(workdir,self._testMethodName)
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),1)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),1)
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),0)
    
    def test_delete_folder_with_dashbards_from_grafana_to_git(self):
        #setup initial state:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","one_folder_one_dashboard"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","empty"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","one_folder_one_dashboard"),os.path.join(repo_dir,"registry"))
        if os.path.exists(os.path.join(repo_dir,"folders")):
            shutil.rmtree(os.path.join(repo_dir,"folders"))
        shutil.copytree(os.path.join(dir_path,"resources","folders"),os.path.join(repo_dir,"folders"))
        if os.path.exists(os.path.join(repo_dir,"dashboards")):
            shutil.rmtree(os.path.join(repo_dir,"dashboards"))
        shutil.copytree(os.path.join(dir_path,"resources","dashboards"),os.path.join(repo_dir,"dashboards"))
        test_comp=self.setItUp(workdir,self._testMethodName)
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),1)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),1)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),0)
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),0)
       
    def test_add_folder_from_git_to_grafana(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        #setup initial state:
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","empty"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","empty"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","one_folder"),os.path.join(repo_dir,"registry"))
        if os.path.exists(os.path.join(repo_dir,"folders")):
            shutil.rmtree(os.path.join(repo_dir,"folders"))
        shutil.copytree(os.path.join(dir_path,"resources","folders"),os.path.join(repo_dir,"folders"))
        test_comp=self.setItUp(workdir,self._testMethodName,"one_folder")
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),1)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        uid=test_comp["grafanaregistry"].get_folders()[0].uid
        dpath=os.path.join(test_comp["repo_dir"],"folders",uid + ".json")
        uid_fromfile=""
        if os.path.isfile(dpath):
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close() 
            uid_fromfile=data["uid"]
        self.assertEqual(uid,uid_fromfile)

    def test_add_dashboard_from_git_to_grafana(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        #setup initial state:
        workdir=self.setWorkdir(self._testMethodName)
        self.copyRegistryTo(os.path.join(dir_path,"resources","registry","one_folder"),os.path.join(workdir,"registry"))
        self.copyGrafanaRegistryTo(os.path.join(dir_path,"resources","grafana_registry","one_folder"),os.path.join(workdir,"grafana_registry"))
        repo_dir=os.path.join(workdir,"grafana-dashboards")
        self.copyGitRegistryTo(os.path.join(dir_path,"resources","git_registry","one_folder_one_dashboard"),os.path.join(repo_dir,"registry"))
        if os.path.exists(os.path.join(repo_dir,"folders")):
            shutil.rmtree(os.path.join(repo_dir,"folders"))
        shutil.copytree(os.path.join(dir_path,"resources","folders"),os.path.join(repo_dir,"folders"))
        if os.path.exists(os.path.join(repo_dir,"dashboards")):
            shutil.rmtree(os.path.join(repo_dir,"dashboards"))
        shutil.copytree(os.path.join(dir_path,"resources","dashboards"),os.path.join(repo_dir,"dashboards"))
        test_comp=self.setItUp(workdir,self._testMethodName,"one_folder_one_dashboard")
        
        # run __main__
        __main__.cycleIt(test_comp["git"],test_comp["collector"],test_comp["configLoader"],test_comp["lock"],test_comp["processor"],test_comp["registry"],test_comp["grafanadbhandler"],test_comp["gitregistry"])

        #asses final state
        self.assertEqual(len(test_comp["collector"].git_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_create_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].git_update_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_delete_actions["dashboards"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_create_actions["dashboards"]),1)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["folders"]),0)
        self.assertEqual(len(test_comp["collector"].grafana_update_actions["dashboards"]),0)
        #asses registries
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["registry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_folders()),len(test_comp["grafanaregistry"].get_folders()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["registry"].get_dashboards()))
        self.assertEqual(len(test_comp["gitregistry"].get_dashboards()),len(test_comp["grafanaregistry"].get_dashboards()))
        #asses that file has been copied to git folder structure
        uid=test_comp["gitregistry"].get_dashboards()[0].uid
        dpath=os.path.join(test_comp["repo_dir"],"dashboards",uid + ".json")
        uid_fromfile=""
        if os.path.isfile(dpath):
            f = open (dpath, "r")
            data = json.loads(f.read())
            f.close() 
            uid_fromfile=data["dashboard"]["uid"]
        self.assertEqual(uid,uid_fromfile)


    def test_delete_folder_from_git_to_grafana(self):
        pass
    def test_delete_folder_with_dashbards_from_git_to_grafana(self):
        pass
    def test_delete_dashboard_from_git_to_grafana(self):
        pass
"""
  
    def test_update_folder_from_grafana_to_git(self):
        pass
    def test_update_dashboard_from_grafana_to_git(self):
        pass

    def test_update_dashboard_from_git_to_grafana(self):
        pass    
    def test_update_folder_from_git_to_grafana(self):
        pass
   
    
"""
if __name__ == '__main__':
    unittest.main()
