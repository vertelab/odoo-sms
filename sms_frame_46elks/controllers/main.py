# -*- coding: utf-8 -*-
import openerp.http as http
from openerp.http import request

class TwilioController(http.Controller):

    @http.route('/sms/46elks/receipt', type="http", auth="public", csrf=False)
    def sms_twilio_receipt(self, **kwargs):
        """Update the state of a sms message, don't trust the posted data"""
        
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['sms.gateway.46elks'].sudo().delivary_receipt(values['AccountSid'], values['MessageSid'])
        
        return "<Response></Response>"
        
    @http.route('/sms/46elks/receive', type="http", auth="public", csrf=False)
    def sms_twilio_receive(self, **kwargs):
        """Fetch the new message directly from Twilio, don't trust posted data"""
        
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        
        twilio_account = request.env['sms.account'].sudo().search([('twilio_account_sid','=', values['AccountSid'])])
        request.env['sms.gateway.46elks'].sudo().check_messages(twilio_account.id, values['MessageSid'])
        
        return "<Response></Response>"