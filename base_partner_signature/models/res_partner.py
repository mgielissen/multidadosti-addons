from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    signature = fields.Binary(string='Signature')
