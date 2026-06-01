# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale VIP Approval',
    'version' : '1.2',
    'summary': 'TODO',
    'sequence': 10,
    'description': """
    TODO
""",
    'category': 'Sales/Sales',
    'depends' : ["sale_management", "mail", "account"],
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
