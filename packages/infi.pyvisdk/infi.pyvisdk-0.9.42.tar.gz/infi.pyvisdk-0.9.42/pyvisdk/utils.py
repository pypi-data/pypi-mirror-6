'''
Created on Jul 29, 2011

@author: eplaster
'''
import re
from munch import Munch

def camel_to_under(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def munchify(*sequence):
    """[item_a, item_b, ... ] -> munch(item_a=item_a, item_b=item_b, ....)"""
    enums = Munch({item:item for item in sequence})
    return enums
