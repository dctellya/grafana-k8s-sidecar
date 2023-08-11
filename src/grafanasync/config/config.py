#!/usr/bin/env python

import os


class ConfigLoader:
    
    def __init__(self):
        self._req_retry_total = 5 if os.getenv("REQ_RETRY_TOTAL") is None else int(os.getenv("REQ_RETRY_TOTAL"))
        self._req_retry_connect = 10 if os.getenv("REQ_RETRY_CONNECT") is None else int(os.getenv("REQ_RETRY_CONNECT"))
        self._req_retry_head = 5 if os.getenv("REQ_RETRY_READ") is None else int(os.getenv("REQ_RETRY_READ"))
        self._req_retry_backoff_factor = 1.1 if os.getenv("REQ_RETRY_BACKOFF_FACTOR") is None else float(os.getenv("REQ_RETRY_BACKOFF_FACTOR"))
        self._req_timeout = 10 if os.getenv("REQ_TIMEOUT") is None else float(os.getenv("REQ_TIMEOUT"))
        
        self._grafana_base_url = "http://localhost" if os.getenv("GRAFANA_BASE_URL") is None else os.getenv("GRAFANA_BASE_URL")
        self._grafana_user = "" if os.getenv("GRAFANA_USERNAME") is None else os.getenv("GRAFANA_USERNAME")
        self._grafana_pass = "" if os.getenv("GRAFANA_PASS") is None else os.getenv("GRAFANA_PASS") 

        self._git_repo_url = "" if os.getenv("GIT_REPO_URL") is None else os.getenv("GIT_REPO_URL")
        self._git_user = "" if os.getenv("GIT_USERNAME") is None else os.getenv("GIT_USERNAME")
        self._git_token = "" if os.getenv("GIT_TOKEN") is None else os.getenv("GIT_TOKEN")
        self._git_repo_name = "grafana-dashboards" if os.getenv("GIT_REPO_NAME") is None else os.getenv("GIT_REPO_NAME")
        self._git_branch_name = "trunk" if os.getenv("GIT_BRANCH_NAME") is None else os.getenv("GIT_BRANCH_NAME")
        
        self._git_grafana_dashboards_dir = "grafana/dashboards" if os.getenv("GIT_GRAFANA_DASHBOARDS_DIR") is None else os.getenv("GIT_GRAFANA_DASHBOARDS_DIR")
        #self._git_grafana_alerts_dir = "grafana/alerts" if os.getenv("GIT_GRAFANA_ALERTS_DIR") is None else os.getenv("GIT_GRAFANA_ALERTS_DIR")
        self._git_registr_dir = "registry" if os.getenv("GIT_REGISTRY_DIR") is None else os.getenv("GIT_REGISTRY_DIR")
        self._workdir = "/tmp/grafana_workdir" if os.getenv("WORKDIR") is None else os.getenv("WORKDIR")
        self._grafana_db_type = "sqllite3" if os.getenv("GRAFANA_DB_TYPE") is None else os.getenv("GRAFANA_DB_TYPE")
        self._grafana_conn_str = "sqllite3:///var/lib/grafana/grafana.db" if os.getenv("GRAFANA_CONN_STR") is None else os.getenv("GRAFANA_CONN_STR")
    
    @property
    def grafana_db_type(self):
        return self._grafana_db_type
    
    @grafana_db_type.setter    
    def grafana_db_type(self, value): 
        self._grafana_db_type = value
    
    @property
    def grafana_conn_str(self):
        return self._grafana_conn_str
    
    @grafana_conn_str.setter    
    def grafana_conn_str(self, value): 
        self._grafana_conn_str = value

    @property
    def req_retry_total(self):
        return self._req_retry_total
    
    @req_retry_total.setter    
    def req_retry_total(self, value): 
        self._req_retry_total = value

    @property
    def req_retry_connect(self):
        return self._req_retry_connect
    
    @req_retry_connect.setter    
    def req_retry_connect(self, value): 
        self._req_retry_connect = value

    @property
    def req_retry_head(self):
        return self._req_retry_head
    
    @req_retry_head.setter    
    def req_retry_head(self, value): 
        self._req_retry_head = value

    @property
    def req_retry_backoff_factor(self):
        return self._req_retry_backoff_factor
    
    @req_retry_backoff_factor.setter    
    def req_retry_backoff_factor(self, value): 
        self._req_retry_backoff_factor = value

    @property
    def req_timeout(self):
        return self._req_timeout
    
    @req_timeout.setter    
    def req_timeout(self, value): 
        self._req_timeout = value

    @property
    def grafana_base_url(self):
        return self._grafana_base_url
    
    @grafana_base_url.setter    
    def grafana_base_url(self, value): 
        self._grafana_base_url = value

    @property
    def grafana_user(self):
        return self._grafana_user
    
    @grafana_user.setter    
    def grafana_user(self, value): 
        self._grafana_user = value

    @property
    def grafana_pass(self):
        return self._grafana_pass
    
    @grafana_pass.setter    
    def grafana_pass(self, value): 
        self._grafana_pass = value

    @property
    def git_repo_url(self):
        return self._git_repo_url
    
    @git_repo_url.setter    
    def git_repo_url(self, value): 
        self._git_repo_url = value

    @property
    def git_repo_name(self):
        return self._git_repo_name
    
    @git_repo_name.setter    
    def git_repo_name(self, value): 
        self._git_repo_name = value

    @property
    def git_user(self):
        return self._git_user
    
    @git_user.setter    
    def git_user(self, value): 
        self._git_user = value

    @property
    def git_token(self):
        return self._git_token
    
    @git_token.setter    
    def git_token(self, value): 
        self._git_token = value

    @property
    def branch_name(self):
        return self._git_branch_name
    
    @branch_name.setter    
    def branch_name(self, value): 
        self._branch_name = value

    @property
    def git_grafana_dashboards_dir(self):
        return self._git_grafana_dashboards_dir
    
    @git_grafana_dashboards_dir.setter    
    def git_grafana_dashboards_dir(self, value): 
        self._git_grafana_dashboards_dir = value

    @property
    def git_grafana_alerts_dir(self):
        return self._git_grafana_alerts_dir
    
    @git_grafana_alerts_dir.setter    
    def git_grafana_alerts_dir(self, value): 
        self._git_grafana_alerts_dir = value

    @property
    def git_grafana_rules_dir(self):
        return self._git_grafana_rules_dir
    
    @git_grafana_rules_dir.setter    
    def git_grafana_rules_dir(self, value): 
        self._git_grafana_rules_dir = value

    @property
    def git_registr_dir(self):
        return self._git_registr_dir
    
    @git_registr_dir.setter    
    def git_registr_dir(self, value): 
        self._git_registr_dir = value

    @property
    def workdir(self):
        return self._workdir

    @workdir.setter    
    def workdir(self, value): 
        self._workdir = value

