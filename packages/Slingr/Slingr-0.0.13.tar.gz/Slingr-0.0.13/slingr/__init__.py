#!/usr/bin/env python

from __future__ import absolute_import

__version__ = '0.0.13'

from flask import Flask

app = Flask(
    __name__, # TODO: it would be nice if this were the name of the Cob
    static_folder=None
)

from slingr.common  import *
from slingr.coburl  import *
from slingr.config  import *
from slingr.asset   import *
from slingr.node    import *
from slingr.build   import *
from slingr.runtime import *
from slingr.server  import *
