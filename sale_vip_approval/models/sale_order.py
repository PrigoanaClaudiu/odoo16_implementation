from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id")
    def _onchange_partner_id_update_gold_discount(self):
        for order in self:
            order.order_line._update_gold_discount()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vip_discount = fields.Float(string="VIP Discount",default=0.0, copy=False)

    def _is_gold_customer_line(self):
        self.ensure_one()
        return self.order_id.partner_id.vip_tier == "gold" and not self.display_type

    def _update_gold_discount(self):
        for line in self:
            if line.display_type:
                continue

            if line._is_gold_customer_line():
                if not line.vip_discount:
                    available_discount = max(100.0 - line.discount, 0.0)
                    vip_discount_to_apply = min(10.0, available_discount)

                    line.discount += vip_discount_to_apply
                    line.vip_discount = vip_discount_to_apply
            else:
                if line.vip_discount:
                    line.discount = max(line.discount - line.vip_discount, 0.0)
                    line.vip_discount = 0.0

    @api.onchange("product_id", "product_uom_qty")
    def _onchange_apply_gold_discount(self):
        self._update_gold_discount()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._update_gold_discount()
        return lines