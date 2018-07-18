from odoo import api, models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    margin_percentage = fields.Char(compute='_get_total_percentage',
                                    string='Margin Percentage')

    @api.one
    @api.depends('quantity', 'price_unit', 'discount')
    def _get_total_percentage(self):
        
        sale_price = 0.0
        discount = 0.0
        cost = 0.0
        margin_amount = 0.0
        margin_percentage = 0.0

        for record in self:
            if record.product_id:
                sale_price = record.price_unit * record.quantity
                discount = (sale_price*record.discount)/100
                cost = record.product_id.standard_price * record.quantity
                margin_amount = (sale_price - discount) - cost
                if cost:
                    margin_percentage = (margin_amount / cost) * 100
                else:
                    margin_percentage = 100
                record.margin_percentage = str(
                    round(margin_percentage, 2)) + ' %'
