#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
#! -*- coding: utf8 -*-
from trytond.pool import *
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pyson import Id
from trytond.pyson import Bool, Eval

__all__ = ['PartyIdentifier','Party']

class PartyIdentifier():
    __metaclass__ = PoolMeta
    __name__ = 'party.identifier'
    _rec_name = 'code'

    type_document = fields.Selection([
                ('', ''),
                ('04', 'RUC'),
                ('05', 'Cedula'),
                ('06', 'Pasaporte'),
                ('07', 'Consumidor Final'),
            ], 'Type Document', states={
                'readonly': ~Eval('active', True),
            },  depends=['active'])

    @classmethod
    def __setup__(cls):
        super(PartyIdentifier, cls).__setup__()
        cls._error_messages.update({
                'invalid_vat_code': ('Invalid VAT Number "%s".')})
        cls._sql_constraints += [
            ('code', 'UNIQUE(code)',
                'VAT Number already exists!'),
        ]
        cls.code.states['readonly'] = Eval('type_document') == '07'

    @staticmethod
    def default_type_document():
        return '05'

    @fields.depends('type_document', 'code')
    def on_change_type_document(self):
        if self.type_document == '07':
            self.code = '9999999999999'
        else:
            if self.code:
                self.code = self.code
            else:
                self.code = None

    def pre_validate(self):
        if self.type_document == '':
            pass
        elif self.type_document == '06':
            pass
        else:
            if not self.code:
                return
            if self.code == '9999999999999':
                return
            code = self.code.replace(".", "")
            if code.isdigit() and len(code) > 9:
                is_valid = self.compute_check_digit(code)
                if is_valid:
                    return
            self.raise_user_error('invalid_vat_code', (self.code,))

    def compute_check_digit(self, raw_number):
        factor = 2
        x = 0
        set_check_digit = None

        if self.type_document == '04':
            # Si es RUC valide segun el tipo de tercero
            if int(raw_number[2]) < 6:
                type_party='persona_natural'
            if int(raw_number[2]) == 6:
                type_party='entidad_publica'
            if int(raw_number[2]) == 9:
                type_party='persona juridica'

            if type_party == 'persona_natural':
                if len(raw_number) != 13 or int(raw_number[2]) > 5 or raw_number[-3:] != '001':
                    return
                number = raw_number[:9]
                set_check_digit = raw_number[9]
                for n in number:
                    y = int(n) * factor
                    if y >= 10:
                        y = int(str(y)[0]) + int(str(y)[1])
                    x += y
                    if factor == 2:
                        factor = 1
                    else:
                        factor = 2
                res = (x % 10)
                if res ==  0:
                    value = 0
                else:
                    value = 10 - (x % 10)
                return (set_check_digit == str(value))

            elif type_party == 'entidad_publica':
                if not len(raw_number) == 13 or raw_number[2] != '6' \
                    or raw_number[-3:] != '001':
                    return
                number = raw_number[:8]
                set_check_digit = raw_number[8]
                for n in reversed(number):
                    x += int(n) * factor
                    factor += 1
                    if factor == 8:
                        factor = 2
                value = 11 - (x % 11)
                if value == 11:
                    value = 0
                return (set_check_digit == str(value))

            else:
                if len(raw_number) != 13 or \
                    (type_party in ['persona_juridica'] \
                    and int(raw_number[2]) != 9) or raw_number[-3:] != '001':
                    return
                number = raw_number[:9]
                set_check_digit = raw_number[9]
                for n in reversed(number):
                    x += int(n) * factor
                    factor += 1
                    if factor == 8:
                        factor = 2
                value = 11 - (x % 11)
                if value == 11:
                    value = 0
                return (set_check_digit == str(value))
        else:
            #Si no tiene RUC valide: cedula, pasaporte, consumidor final (cedula)
            if len(raw_number) != 10:
                return
            number = raw_number[:9]
            set_check_digit = raw_number[9]
            for n in number:
                y = int(n) * factor
                if y >= 10:
                    y = int(str(y)[0]) + int(str(y)[1])
                x += y
                if factor == 2:
                    factor = 1
                else:
                    factor = 2
            res = (x % 10)
            if res ==  0:
                value = 0
            else:
                value = 10 - (x % 10)
            return (set_check_digit == str(value))

class Party:
    __metaclass__ = PoolMeta
    __name__ = 'party.party'

    commercial_name = fields.Char('Commercial Name')

    @staticmethod
    def default_contribuyente_especial():
        return False

    @staticmethod
    def default_mandatory_accounting():
        return 'NO'

    @classmethod
    def search_rec_name(cls, name, clause):
        parties = cls.search([
                ('vat_code',) + tuple(clause[1:]),
                ], limit=1)
        if parties:
            return [('vat_code',) + tuple(clause[1:])]
        return [('name',) + tuple(clause[1:])]
