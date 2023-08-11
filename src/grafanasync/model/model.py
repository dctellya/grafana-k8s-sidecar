#!/usr/bin/env python
import dataclasses
from typing import Any, Dict, Optional, Union


@dataclasses.dataclass
class DatasourceIdentifier:
    """
    A Grafana data source can be identified by either a numerical id, an
    alphanumerical uid, or a name.
    """

    id: Optional[str] = None
    uid: Optional[str] = None
    name: Optional[str] = None