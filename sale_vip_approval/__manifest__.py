# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale VIP Approval',
    'version' : '1.2',
     'summary': "VIP customer perks and discount approval workflow for sales orders",
    'sequence': 10,
    'description': """
    Sale VIP Approval
    =================
    
    This module adds a VIP customer loyalty workflow and discount approval guardrails
    for Sales.

    * Adds VIP tiers on customer profiles: Standard, Silver, and Gold
    * Displays the customer's current-year net invoiced amount
    * Automatically applies a VIP discount for Gold customers on sale order lines
    * Computes the overall discount on sale orders
    * Blocks heavily discounted quotations from being confirmed by regular sales users
    * Adds a Waiting Approval state for quotations requiring manager approval
    * Notifies Sales Managers through scheduled activities
    * Allows Sales Managers to review and confirm quotations waiting for approval
    * Provides a dedicated menu for sale orders waiting for approval

""",
    'category': 'Sales/Sales',
    'depends' : ["sale_management", "mail", "account"],
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_approval_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
