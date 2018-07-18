from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    margin_amount = fields.Char(compute='_get_average_margin_percentage',
                                string='Margin Amount')

    margin_percentage = fields.Char(compute='_get_average_margin_percentage', 
                                    string='Margin Percentage')

    @api.one
    @api.depends('invoice_line_ids','invoice_line_ids.quantity',
                 'invoice_line_ids.price_unit', 'invoice_line_ids.discount')
    def _get_average_margin_percentage(self):
        
        sale_price = 0.0
        discount = 0.0
        cost = 0.0
        margin_amount = 0.0
        line_cost = 0.0
        line_margin_amount = 0.0
        margin_percentage = 0.0

        for record in self:
            if record.invoice_line_ids:
                for line in record.invoice_line_ids:
                    sale_price = line.price_unit * line.quantity
                    discount = (sale_price * line.discount)/100
                    cost = line.product_id.standard_price * line.quantity
                    line_cost += cost
                    margin_amount = (sale_price - discount) - cost
                    line_margin_amount += margin_amount
                if line_cost:
                    margin_percentage = (line_margin_amount / line_cost) * 100
                else:
                    margin_percentage = 100
                record.margin_amount = str(round(line_margin_amount,2))
                record.margin_percentage = str(round(margin_percentage,2)) + '%'
