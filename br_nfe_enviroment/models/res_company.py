import operator
from odoo import api, fields, models


class ResCompany(models.Model):
    """NFe Server Enviroment"""
    _name = 'res.company'
    _inherit = ['res.company', 'server.env.mixin']

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        company_fields = {
            "tipo_ambiente": {},
        }
        company_fields.update(base_fields)
        return company_fields

    @api.model
    def _server_env_global_section_name(self):
        """Name of the global section in the configuration files

        Can be customized in your model
        """
        return 'res_company'
