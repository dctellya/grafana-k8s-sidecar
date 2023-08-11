#!/usr/bin/env python
import sqlalchemy as db
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.orm import column_property, DeclarativeBase
import datetime
import json
import decimal
from typing import Any, Dict, Optional, Union
from dataclasses import asdict 
import dataclasses
from dateutil import parser

class Base(DeclarativeBase):
    pass

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
        return (datetime.datetime.min + obj).time().isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)

class GrafanaDBHandler:
    def __init__(self, db_type, conn_str):
        self._engine= None
        if conn_str is None or len(conn_str) == 0:
            raise Exception('No valid conn string')
        
        if db_type == "sqlite" or db_type == "mysql" or db_type == "postgresql":
            self._engine=db.create_engine(conn_str)
            
        else:
            raise Exception('No valid Grafana DB type')

    @property
    def engine(self):
        return self._engine
    
    @property
    def connection(self):
        return self._conn
    
    @property
    def metadata(self):
        return self._metadata
    
    def get_all_dashboards(self):
        with Session(self._engine) as session:
            #stmt = db.select(DashboardItem).where(DashboardItem.is_folder == 0)
            d1 = dashboard_table.alias("a")
            d2 = dashboard_table.alias("b")
            stmt=db.select(d1.c.uid,
                      #d1.c.version,
                      d1.c.slug,
                      d1.c.title,
                      d1.c.org_id,
                      d1.c.created,
                      d1.c.updated,
                      d1.c.is_folder,
                      d2.c.uid.label("folder_uid"),
                    ).select_from(d1).where(d1.c.is_folder == 0).join(d2, d1.c.folder_id == d2.c.id).order_by(d2.c.uid.label("folder_uid"))
            dashboards= session.execute(stmt).all()
            dashboardArr = []
            for d in dashboards:
                dashboard=DashboardItem(d.uid,d.slug,d.title,d.org_id,d.created,d.updated,d.folder_uid,d.is_folder)
                dashboardArr.append(dashboard)
            session.close() 
            return dashboardArr 
    
    def get_all_folders(self):
        with Session(self._engine) as session:
            #stmt = db.select(DashboardItem).where(DashboardItem.is_folder == 1)
            d1 = dashboard_table.alias("a")
            d2 = dashboard_table.alias("b")
            stmt=db.select(d1.c.uid,
                      #d1.c.version,
                      d1.c.slug,
                      d1.c.title,
                      d1.c.org_id,
                      d1.c.created,
                      d1.c.updated,
                      d1.c.is_folder,
                      d2.c.uid.label("folder_uid"),
                    ).select_from(d1).where(d1.c.is_folder == 1).join(d2, d1.c.id == d2.c.id).order_by(d2.c.uid.label("folder_uid"))
            folders= session.execute(stmt).fetchall()
            folderArr = []
            for f in folders:
                folder=DashboardItem(f.uid,f.slug,f.title,f.org_id,f.created,f.updated,f.folder_uid,f.is_folder)
                folderArr.append(folder)
            session.close() 
            return folderArr
        
    def get_all_dashboards_updated_after_date(self, thedate):
        with Session(self._engine) as session:
            #stmt = db.select(DashboardItem).where(DashboardItem.is_folder == 0).where(DashboardItem.updated >= thedate)
            d1 = dashboard_table.alias("a")
            d2 = dashboard_table.alias("b")
            stmt=db.select(d1.c.uid,
                      #d1.c.version,
                      d1.c.slug,
                      d1.c.title,
                      d1.c.org_id,
                      d1.c.created,
                      d1.c.updated,
                      d1.c.is_folder,
                      d2.c.uid.label("folder_uid"),
                    ).select_from(d1).where(d1.c.is_folder == 0).where(d1.c.updated >= thedate).join(d2, d1.c.folder_id == d2.c.id)
            dashboards= session.execute(stmt).all()
            dashboardArr = []
            for d in dashboards:
                dashboard=DashboardItem(d.uid,d.slug,d.title,d.org_id,d.created,d.updated,d.folder_uid,d.is_folder)
                dashboardArr.append(dashboard)
            session.close() 
            return dashboardArr
    
    def get_all_folders_updated_after_date(self,thedate):
        with Session(self._engine) as session:
            #stmt = db.select(DashboardItem).where(DashboardItem.is_folder == 1).where(DashboardItem.updated >= thedate)
            d1 = dashboard_table.alias("a")
            d2 = dashboard_table.alias("b")
            stmt=db.select(d1.c.uid,
                      #d1.c.version,
                      d1.c.slug,
                      d1.c.title,
                      d1.c.org_id,
                      d1.c.created,
                      d1.c.updated,
                      d1.c.is_folder,
                      d2.c.uid.label("folder_uid"),
                    ).select_from(d1).where(d1.c.is_folder == 1).where(d1.c.updated >= thedate).join(d2, d1.c.id == d2.c.id)
            folders= session.execute(stmt).all()
            folderArr = []
            for f in folders:
                folder=DashboardItem(f.uid,f.slug,f.title,f.org_id,f.created,f.updated,f.folder_uid,f.is_folder)
                folderArr.append(folder)
            session.close() 
            return folderArr  
    
    def sync_dashboard_item(self,uid,datecreated,dateupdated):
        print("uid:",uid)
        print("created:",datecreated)
        print("updated:", dateupdated)
        with Session(self._engine) as session:
            with session.begin():
                dtc=parser.parse(datecreated).replace(tzinfo=None)
                dtu=parser.parse(dateupdated).replace(tzinfo=None)         
                print("created after removing tz:",dtc)
                print("updated after removing tz:", dtu)
                session.execute(
                    text("UPDATE dashboard SET created = :created, updated = :updated WHERE uid = :uid"),
                    {'created': dtc,'updated': dtu, 'uid': str(uid)}
                )
                result = session.execute(
                    text(" SELECT id,version from dashboard WHERE uid = :uid"),
                    {'uid': str(uid)}
                ).first()
                print(result)
                if not result is None:
                    id = result[0]
                    version = result[1]
                    session.execute(
                        text("UPDATE dashboard_version SET created = :updated WHERE dashboard_id = :id AND version = :version"),
                        {'updated': dtu, 'id': int(id),'version': int(version)}
                    )

dashboard_table=db.Table(
        "dashboard",
        Base.metadata,
        db.Column("id", db.Integer, primary_key=True),
        #db.Column("version", db.Integer, nullable=False),
        db.Column("slug", db.String, nullable=False),
        db.Column("title", db.String, nullable=False),
        db.Column("org_id", db.Integer, nullable=False),
        db.Column("created", db.DateTime, nullable=False),
        db.Column("updated", db.DateTime, nullable=False),
        db.Column("folder_id", db.Integer, nullable=False,default=0),
        db.Column("is_folder", db.Integer, nullable=False,default=0),
        db.Column("uid", db.String, nullable=True),
    )

@dataclasses.dataclass
class DashboardItem:
    uid: Optional[str] = None
    #version: Optional[int] = 0
    slug: Optional[str] = None
    title: Optional[str] = None
    org_id: Optional[int] = 0
    created: Optional[datetime.datetime] = None
    updated: Optional[datetime.datetime] = None
    folder_uid: Optional[str] = None
    is_folder: Optional[int] = 0
    def __init__(self, uid: str, slug: str, title: str, org_id: int,created: datetime,updated: datetime,folder_uid:str,is_folder:int):
        self.uid = uid
        #self.version = version
        self.slug = slug
        self.title = title
        self.org_id = org_id
        self.created = created
        self.updated = updated
        self.folder_uid = folder_uid
        self.is_folder = is_folder
    def toDict(self):
        return asdict(self)
    def __eq__(self, other): 
        if not isinstance(other, DashboardItem):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return (self.uid == other.uid and 
                #self.version == other.version and 
                self.slug == other.slug and
                self.title == other.title and 
                self.org_id == other.org_id and 
                self.created == other.created and
                self.updated == other.updated and 
                self.folder_uid == other.folder_uid and 
                self.is_folder == other.is_folder
                )

def dashboardItemDecoder(di_dict):
    di=DashboardItem(
        uid = di_dict["uid"],
        #version = di_dict["version"],
        slug = di_dict["slug"],
        title = di_dict["title"],
        org_id = di_dict["org_id"],
        created = parser.parse(di_dict["created"]),
        updated = parser.parse(di_dict["updated"]),
        folder_uid = di_dict["folder_uid"],
        is_folder = di_dict["is_folder"],
    )
    return di

