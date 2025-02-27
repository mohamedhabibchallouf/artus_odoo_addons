# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
import qrcode
import base64
from io import BytesIO

_logger = logging.getLogger(__name__)


class HiscoxConfiguration(models.Model):
    _name = 'hiscox.configuration'
    _description = 'Hiscox API Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    url = fields.Char(string='Hiscox API URL', required=True)


        
    def check_api_connection(self):
        """Checks if the Hiscox API is reachable."""
        hiscox_url = self.url  # Fetch the URL from the configuration model
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.get(hiscox_url, headers=headers, timeout=10)
            response.raise_for_status()
            _logger.info("Hiscox API is reachable.")
            return True
        except requests.RequestException as e:
            raise UserError(f"Hiscox API connection failed: please contact the administrator")
            _logger.error(f"Hiscox API connection failed: {e}")
            return False


class HiscoxCase(models.Model):
    _name = 'edited.hiscox.case'
    _description = 'Hiscox Application Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Customer Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    application_status = fields.Selection([
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Application Status', default='pending')
    qr_code = fields.Binary(string='QR Code')

    def generate_qr_code(self):
        """Generates a QR code containing customer information and stores it as a Base64-encoded image."""
        for record in self:
            qr_data = f"Name: {record.name}\nEmail: {record.email}\nPhone: {record.phone}\nStatus: {record.application_status}"
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            qr_image = base64.b64encode(buffer.getvalue())
            record.qr_code = qr_image

    def submit_to_hiscox(self):
        """Submits customer data to the Hiscox API via POST request."""
        hiscox_url = self.env['hiscox.configuration'].search([], limit=1).url  # Fetch the URL from the configuration model
        headers = {'Content-Type': 'application/json'}
        
        for record in self:
            payload = {
                'name': record.name,
                'email': record.email,
                'phone': record.phone,
            }
            try:
                response = requests.post(hiscox_url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                record.application_status = data.get('status', 'pending')
            except requests.RequestException as e:
                raise UserError(f"Error submitting to Hiscox API: please check the API connection")
                _logger.error(f"Error submitting to Hiscox API: {e}")
                record.application_status = 'pending'

    def check_status_from_hiscox(self):
        """Checks the application status from the Hiscox API via GET request."""
        hiscox_url = self.env['hiscox.configuration'].search([], limit=1).url  # Fetch the URL from the configuration model
        headers = {'Content-Type': 'application/json'}
        
        for record in self:
            params = {'email': record.email}
            try:
                response = requests.get(hiscox_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                record.application_status = data.get('status', record.application_status)
            except requests.RequestException as e:
                _logger.error(f"Error fetching status from Hiscox API: {e}")


