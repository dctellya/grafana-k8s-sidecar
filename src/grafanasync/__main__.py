#!/usr/bin/env python

import os
import re
import signal
from datetime import datetime, timedelta

#from requests.packages.urllib3.util.retry import Retry

#from helpers import REQ_RETRY_TOTAL, REQ_RETRY_CONNECT, REQ_RETRY_READ, REQ_RETRY_BACKOFF_FACTOR

from grafanasync.util import get_logger
from time import sleep
from grafanasync.util import GracefulKiller
from grafanasync.config import ConfigLoader
from grafanasync.handlers import Git
from grafanasync.handlers import Registry
from grafanasync.handlers import GrafanaAPIHandler
from grafanasync.handlers import GrafanaDBHandler
from grafanasync.process import Collector
from grafanasync.process import Processor
from grafanasync.process import Lock

# Get logger
logger = get_logger()

def check_git_grafana(configLoader, git,grafanaapihandler):
    logger.info("Load config: { req_retry_total: %s, req_retry_connect: %s, req_retry_head: %s, req_retry_backoff_factor: %s, req_timeout: %s, grafana_base_url: %s,grafana_user: %s, git_repo_url: %s, git_repo_name: %s, git_user: %s, workdir: %s }", 
                configLoader.req_retry_total,
                configLoader.req_retry_connect,
                configLoader.req_retry_head,
                configLoader.req_retry_backoff_factor,
                configLoader.req_timeout,
                configLoader.grafana_base_url,
                configLoader.grafana_user,
                configLoader.git_repo_url,
                configLoader.git_repo_name,
                configLoader.git_user,
                configLoader.workdir)
    # clone git repo if it doesn't exist
    if os.path.exists(git.repo_dir) != True :
        git.clone()

    # check grafana api status
    logger.info("grafana.health.check():" + str(grafanaapihandler.client.health.check()))

def main():
    logger.info("Starting collector")

    killer = GracefulKiller()
    configLoader = ConfigLoader()
    repo_dir=os.path.join(configLoader.workdir,configLoader.git_repo_name)
    git = Git(configLoader.git_repo_url,repo_dir, configLoader.git_user,configLoader.git_token)
    grafanaapihandler = GrafanaAPIHandler(configLoader.grafana_base_url, configLoader.grafana_user, configLoader.grafana_pass)
    grafanadbhandler = GrafanaDBHandler(configLoader.grafana_db_type, configLoader.grafana_conn_str)
    check_git_grafana(configLoader, git, grafanaapihandler)
    registry = Registry(os.path.join(configLoader.workdir,"registry"))
    gitregistry = Registry(os.path.join(repo_dir,"registry"))
    grafanaregistry = Registry(os.path.join(configLoader.workdir,"grafana_registry"))
    #grafanaapihandler.get_all_folders()
    collector= Collector(grafanadbhandler, grafanaapihandler, git, registry,gitregistry,grafanaregistry)
    processor= Processor(grafanadbhandler, grafanaapihandler, git, registry,gitregistry,grafanaregistry)
    lock=Lock()
    logger.info("Watching...")
    
    print("get_local_short_sha_commit:",git.get_local_short_sha_commit())
    print("get_local_sha_commit:",git.get_local_sha_commit())
    print("get_remote_sha_commit:",git.get_remote_sha_commit())

    while not killer.kill_now:
        cycleIt(git,collector,configLoader,lock,processor,registry,grafanadbhandler,gitregistry)
        sleep(30)
        
    logger.info("End Watching...")
    logger.info("End collector - Graceful termination")
    

def cycleIt(git,collector,configLoader,lock,processor,registry,grafanadbhandler,gitregistry):
    #try:
        logger.info("Collect Updates")
        #git.stash()
        git.pull(configLoader.branch_name)
        collector.flush()
        collector.collectChanges()
        
        logger.info("Has Updates - Acquire Lock")
        if lock.doIneedLock(collector.git_delete_actions,collector.git_create_actions,collector.git_update_actions):
            lock.acquireLock()
        logger.info("Has Updates - ProcessUpdates")
        processor.processChanges(collector)
        #persist to registry
        logger.info("Has Updates - persist to registry")
        registry.persist_date(datetime.now())
        registry.persist_folders(grafanadbhandler.get_all_folders())
        registry.persist_dashboards(grafanadbhandler.get_all_dashboards())
        #move to git registry
        logger.info("Has Updates - persist to git registry")
        gitregistry.persist_folders(registry.folders)
        gitregistry.persist_dashboards(registry.dashboards)
        gitregistry.persist_date(registry.date)
        logger.info("Has Updates - Check Lock")
        if lock.doIneedLock(collector.git_delete_actions,collector.git_create_actions,collector.git_update_actions):
            if lock.checkLock():
                message=str(gitregistry.date)
                git.add_and_commit(message)
                git.push(configLoader.branch_name) 
                registry.persist_commit(git.get_local_sha_commit())  
            else:
                #git.stash()
                git.pull(configLoader.branch_name)
                registry.persist_commit(git.get_local_sha_commit())
            lock.releaseLock()
    #except Exception as e:
    #    logger.error(e)

if __name__ == "__main__":
    main()