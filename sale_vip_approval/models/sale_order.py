from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[("waiting_approval", "Waiting Approval"), ("sale",)], ondelete={"waiting_approval": "set default",})

    overall_discount = fields.Float(string="Overall Discount (%)",compute="_compute_overall_discount")

    is_discount_approval_manager = fields.Boolean(string="Is Discount Approval Manager", compute="_compute_is_discount_approval_manager",)

    @api.depends_context("uid")
    def _compute_is_discount_approval_manager(self):
        is_manager = self.env.user.has_group("sales_team.group_sale_manager")
        for order in self:
            order.is_discount_approval_manager = is_manager

    def _get_discount_approval_limit(self):
        return 15.0

    def _is_discount_approval_manager(self):
        return self.env.user.has_group("sales_team.group_sale_manager")

    def _requires_discount_approval(self):
        self.ensure_one()
        return self.overall_discount > self._get_discount_approval_limit()

    def action_request_discount_approval(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError(
                    _("Only draft or sent quotations can be submitted for approval.")
                )

            if not order._requires_discount_approval():
                raise UserError(
                    _("This quotation does not require discount approval.")
                )

            if order._is_discount_approval_manager():
                raise UserError(
                    _("Sales Managers can confirm this quotation directly.")
                )

            order.write({
                "state": "waiting_approval",
            })

            order.message_post(
                body=_(
                    "Discount approval requested. Overall discount is %.2f%%."
                ) % order.overall_discount
            )

        return True

    def action_confirm(self):
        for order in self:
            if order._requires_discount_approval() and not order._is_discount_approval_manager():
                raise UserError(
                    _(
                        "This quotation has an overall discount of %.2f%% and "
                        "requires Sales Manager approval."
                    ) % order.overall_discount
                )

        return super().action_confirm()

    def _get_overall_discount(self):
        self.ensure_one()

        if not self.amount_undiscounted:
            return 0.0

        return (self.amount_undiscounted - self.amount_untaxed) / self.amount_undiscounted * 100

    @api.depends("amount_undiscounted", "amount_untaxed")
    def _compute_overall_discount(self):
        for order in self:
            order.overall_discount = order._get_overall_discount()

    @api.onchange("partner_id")
    def _onchange_partner_id_update_gold_discount(self):
        for order in self:
            order.order_line._update_gold_discount()

    def write(self, vals):
        protected_fields = {"message_follower_ids", "message_ids", "activity_ids", }

        for order in self:
            if order.state == "waiting_approval" and not order._is_discount_approval_manager():
                if any(field not in protected_fields for field in vals):
                    raise UserError(_("Only Sales Managers can modify orders waiting for approval."))

        return super(SaleOrder, self).write(vals)


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