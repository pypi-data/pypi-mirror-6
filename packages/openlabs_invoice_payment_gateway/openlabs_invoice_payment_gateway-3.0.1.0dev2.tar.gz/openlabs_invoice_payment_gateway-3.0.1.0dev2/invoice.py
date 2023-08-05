# -*- coding: utf-8 -*-
"""

    invoice

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta

__all__ = ['Invoice']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'

    def pay_using_transaction(self, payment_transaction):
        """
        Pay an invoice using an existing payment_transaction

        :param payment_transaction: Active record of a payment transaction
        """
        for line in payment_transaction.move.lines:
            if line.account == self.account:
                self.write(
                    [self], {'payment_lines': [('add', [line.id])]}
                )
                return line
        raise Exception('Missing account')
