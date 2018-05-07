from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_order_line_category_id = fields.Many2one(comodel_name='sale.order.line.category',
                                                  string='Category')
