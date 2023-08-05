# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from decimal import Decimal
from django.utils import simplejson

class ExtendedJSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, time):
            return obj.isoformat()
        return super(ExtendedJSONEncoder, self).default(obj) 

