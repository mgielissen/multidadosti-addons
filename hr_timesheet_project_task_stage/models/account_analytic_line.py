from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    project_task_type_id = fields.Many2one(comodel_name='project.task.type',
                                           string='Task Stage')

    def _timesheet_preprocess(self, vals):
        """ Deduce other field values from the one given.
            Overrride this to compute on the fly some field that can not be computed fields.
            :param values: dict values for `create`or `write`.
        """
        vals = super(AccountAnalyticLine, self)._timesheet_preprocess(vals)

        # get partner_id from project
        if vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['customer_partner_id'] = project.partner_id.id

        # get stage from task
        if vals.get('task_id'):
            task = self.env['project.task'].browse(vals.get('task_id'))
            vals['project_task_type_id'] = task.stage_id.id
       
        return vals
