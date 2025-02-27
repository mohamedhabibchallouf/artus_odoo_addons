from odoo import models, fields, api
from datetime import date, timedelta

class InsurancePolicy(models.Model):
    _name = "insurance.policy"
    _description = "Insurance Policy"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Policy Number", required=True, copy=False, readonly=True, index=True, default=lambda self: self.env['ir.sequence'].next_by_code('insurance.policy'))
    policyholder_id = fields.Many2one('res.partner', string="Versicherungsnehmer", required=True)
    product_id = fields.Many2one('product.product', string="Versicherungsprodukt", required=True)
    coverage_amount = fields.Monetary(string="Deckungssumme", currency_field='currency_id')
    premium = fields.Monetary(string="Prämie", currency_field='currency_id')
    start_date = fields.Date(string="Vertragsbeginn", required=True)
    end_date = fields.Date(string="Vertragsende", required=True)
    currency_id = fields.Many2one('res.currency', string="Währung", default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('active', 'Aktiv'),
        ('expired', 'Abgelaufen'),
        ('cancelled', 'Gekündigt')
    ], string="Status", default="active")

    @api.model
    def check_expiring_policies(self):
        policies = self.search([('end_date', '<=', date.today() + timedelta(days=30)), ('state', '=', 'active')])
        for policy in policies:
            policy.state = 'expired'
            self.env['mail.message'].create({
                'subject': "Versicherungspolice läuft bald ab",
                'body': f"Die Versicherungspolice {policy.name} für {policy.policyholder_id.name} läuft am {policy.end_date} ab.",
                'model': 'insurance.policy',
                'res_id': policy.id,
                'message_type': 'notification',
            })


    def action_cancel(self):
        self.state = 'cancelled'
        self.env['mail.message'].create({
            'subject': "Versicherungspolice gekündigt",
            'body': f"Die Versicherungspolice {self.name} für {self.policyholder_id.name} wurde gekündigt.",
            'model': 'insurance.policy',
            'res_id': self.id,
            'message_type': 'notification',
        })
    
    