#!/usr/bin/env python
from git import Repo
import git 

import os
import subprocess
import re

class Git:

    def __init__(self, git_url, repo_dir, git_user, git_token,git_email="<>"):
        self._repo_dir=repo_dir
        self._git_user=git_user
        self._git_token=git_token
        self._git_email=git_email
        # get git_url
        
        user_prefix=""
       
        if self._git_token is not None and self._git_token:
            user_prefix=f"x-token-auth:{self._git_token}@"
        elif self._git_user is not None and self._git_user:
            user_prefix=f"{self._git_user}@"

        if user_prefix:
            if git_url.startswith('https://'):
                git_url=f"https://{user_prefix}{git_url.replace('https://','')}"
            elif git_url.startswith('http://'):
                git_url=f"http://{user_prefix}{git_url.replace('http://','')}"
        
        self._git_url=git_url
        if os.path.exists(os.path.join(repo_dir,".git")) == True :
            self._repo = Repo(repo_dir)
            self._repo.config_writer().set_value("user", "name", self._git_user).release()
            self._repo.config_writer().set_value("user", "email",self._git_email).release()

        else:
            self._repo = None
        
    @property
    def git_url(self):
        return self._git_url
    
    @property
    def repo_dir(self):
        return self._repo_dir
    
    @property
    def repo(self):
        return self._repo
    
    def clone(self):
        self._repo = Repo.clone_from(self.git_url, self.repo_dir)
        self._repo.config_writer().set_value("user", "name", self._git_user).release()
        self._repo.config_writer().set_value("user", "email",self._git_email).release()

    def pull(self,branch_name):
        #lets reset
        self._repo.git.reset('--hard')
        #lets pull
        origin = self._repo.remote(name="origin")
        origin.pull(branch_name)
   
    def push(self,branch_name):
        origin = self._repo.remote(name="origin")
        origin.push(branch_name)

    def stash(self):
        try:
            self._repo.git.stash("drop")
        except git.exc.GitCommandError as e:
            err=e.stderr.strip()
            if err == "stderr: 'No stash entries found.'":
                pass
            else:
                raise e
        
    def add_and_commit(self,message):
        #add all
        self._repo.git.add('--all')
        #commit
        self._repo.git.commit('-m', message)

    def get_local_short_sha_commit(self):
        return self._repo.git.rev_parse(self._repo.head, short=True)
    
    def get_local_sha_commit(self):
        return self._repo.head.object.hexsha
    
    def get_remote_sha_commit(self):
        process = subprocess.Popen(["git", "ls-remote", self.git_url], stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        sha = re.split(r'\t+', stdout.decode('ascii'))[0]
        return sha
    