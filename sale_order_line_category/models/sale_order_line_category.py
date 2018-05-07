from odoo import fields, models


class SaleOrderLineCategory(models.Model):
    _name = 'sale.order.line.category'

    name = fields.Char(string='Category')
