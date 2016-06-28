#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
#! -*- coding: utf8 -*-
from trytond.pool import *
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pyson import Id
from trytond.pyson import Bool, Eval

__all__ = ['Address']

class Address:
    __metaclass__ = PoolMeta
    __name__ = 'party.address'

    @staticmethod
    def default_country():
        return Id('country', 'ec').pyson()
