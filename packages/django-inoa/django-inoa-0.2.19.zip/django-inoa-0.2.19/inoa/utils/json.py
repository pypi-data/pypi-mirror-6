# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from decimal import Decimal
from django.utils import simplejson

class ExtendedJSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            exponent = obj.as_tuple()[2]
            if exponent < 0:
                return "%%.%df" % -exponent % obj
            else:
                return "%d.0" % obj
        if isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, time):
            return obj.isoformat()
        return super(ExtendedJSONEncoder, self).default(obj) 

