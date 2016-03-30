#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.pool import Pool
from .party import *
def register():
    Pool.register(
        Party,
        BankAccountNumber, 
        Address, 
        Company, 
        Configuration,
        module='nodux_party_ec', type_='model')
