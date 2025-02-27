from odoo import http
from odoo.http import request

class InsurancePolicyAPI(http.Controller):

    @http.route('/api/insurance/policy', type='json', auth='public', methods=['POST'])
    def create_policy(self, **kwargs):
        policy = request.env['insurance.policy'].sudo().create({
            'policyholder_id': kwargs.get('policyholder_id'),
            'product_id': kwargs.get('product_id'),
            'coverage_amount': kwargs.get('coverage_amount'),
            'premium': kwargs.get('premium'),
            'start_date': kwargs.get('start_date'),
            'end_date': kwargs.get('end_date'),
            'state': kwargs.get('state', 'active'),
        })
        return {'id': policy.id, 'message': 'Policy created successfully'}

    @http.route('/api/insurance/policy/<int:policy_id>', type='json', auth='public', methods=['PUT'])
    def update_policy(self, policy_id, **kwargs):
        policy = request.env['insurance.policy'].sudo().browse(policy_id)
        if not policy.exists():
            return {'error': 'Policy not found'}
        policy.write(kwargs)
        return {'message': 'Policy updated successfully'}
    