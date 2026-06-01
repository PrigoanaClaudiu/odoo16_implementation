# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from datetime import date


class ResPartner(models.Model):
    _inherit = "res.partner"

    vip_tier = fields.Selection([('standard', 'Standard'), ('silver', 'Silver'), ('gold', 'Gold')],
                                tracking=True, default="standard", string="VIP Tier")

    current_year_net_invoiced = fields.Monetary(string="Current Year Net Invoiced", compute='_compute_current_year_net')

    def _get_current_year_net_invoiced(self):
        self.ensure_one()
        today = fields.Date.today(self)
        date_start = date(today.year, 1, 1)
        date_end = date(today.year, 12, 31)

        return [('state', '=', 'posted'), ('invoice_date', '>=', date_start), ('invoice_date', '<=', date_end),
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('commercial_partner_id', '=', self.commercial_partner_id.id)]

    def _compute_current_year_net(self):
        for partner in self:
            invoices = self.env['account.move'].search(partner._get_current_year_net_invoiced())
            partner.current_year_net_invoiced = sum(move.amount_untaxed_signed for move in invoices)
