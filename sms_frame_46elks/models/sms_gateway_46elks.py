# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Enterprise Resource Management Solution, third party addon
# Copyright (C) 2017- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _
from openerp.exceptions import Warning

import requests
import json

import logging
_logger = logging.getLogger(__name__)


class SmsGateway46elks(models.Model):

    _name = "sms.gateway.46elks"
    _description = "46elks SMS Gateway"
    
    api_url = fields.Char(string='API URL')
    
    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name='', my_record_id=0, media=None):
        """Actual Sending of the sms"""
        sms_account = self.env['sms.account'].search([('id','=',sms_gateway_id)])
        
        #format the from number before sending
        format_from = from_number
        if " " in format_from: format_from.replace(" ", "")
        
        #format the to number before sending
        format_to = to_number
        if " " in format_to: format_to.replace(" ", "")        
        
        media_url = ""
        #Create an attachment for the mms now since we need a url now
        if media:
            attachment_id = self.env['ir.attachment'].sudo().create({'name': 'mms ' + str(my_record_id), 'type': 'binary', 'datas': media, 'public': True})
            media_url = request.httprequest.host_url + "web/image/" + str(attachment_id.id) + "/media." + attachment_id.mimetype.split("/")[1]
	    
	    #Force the creation of the new attachment before you make the request
	    self.env.cr.commit() # all good, we commit
            
        #send the sms/mms
        base_url = self.env['ir.config_parameter'].search([('key','=','web.base.url')])[0].value
        payload = {'From': format_from.encode('utf-8'), 'To': format_to.encode('utf-8'), 'message': sms_content.encode('utf-8'), 'StatusCallback': base_url + "/sms/46elks/receipt"}
    
        #~ payload['whendelivered'] = base_url 
        #~ payload['flashsms'] = 'no' 

        if media:
            payload['image'] = media_url
            
        response_string = requests.post("https://api.46elks.com/a1/SMS",
            data=payload, 
            auth=(str(sms_account.x46elks_account_sid or ''), str(sms_account.x46elks_auth_token or ''))
        )

        #Analyse the reponse string and determine if it sent successfully other wise return a human readable error message   
        human_read_error = ""
        root = etree.fromstring(response_string.text.encode('utf-8'))
        my_elements_human = root.xpath('/46elksResponse/RestException/Message')
        if len(my_elements_human) != 0:
	    human_read_error = my_elements_human[0].text
        
        #The message id is important for delivary reports also set delivary_state=successful
	sms_gateway_message_id = ""
	delivary_state = "failed"
	my_elements = root.xpath('//Sid')
	if len(my_elements) != 0:
	    sms_gateway_message_id = my_elements[0].text
            delivary_state = "successful"
        
        #send a repsonse back saying how the sending went
        my_sms_response = sms_response()
        my_sms_response.delivary_state = delivary_state
        my_sms_response.response_string = response_string.text
        my_sms_response.human_read_error = human_read_error
        my_sms_response.message_id = sms_gateway_message_id
        return my_sms_response

    def check_messages(self, account_id, message_id=""):
        """Checks for any new messages or if the message id is specified get only that message"""
        pass
            
    def _add_message(self, sms_message, account_id):
        pass

    def delivary_receipt(self, account_sid, message_id):
        pass
            
class SmsAccount46elks(models.Model):

    _inherit = "sms.account"
    _description = "Adds the 46elks specfic gateway settings to the sms gateway accounts"
    
    x46elks_account_sid = fields.Char(string='Account SID')
    x46elks_auth_token = fields.Char(string='Auth Token')
    x46elks_type = fields.Selection([('main','Main Account'),('sub','Sub Account')],string='Type',help="Type of account")
    x46elks_last_check_date = fields.Datetime(string="Last Check Date")
    x46elks_currency = fields.Many2one(comodel_name='res.currency',string='Currency')
    x46elks_balance = fields.Float(string='Balance')
    x46elks_mobilenumber = fields.Char(string='Mobile number',help="Register mobile number for this account, if this is empty it's probably a subaccount.")
    x46elks_email = fields.Char(string='Email',help="Register mobile number for this account, if this is empty it's probably a subaccount.")
    

    @api.one
    def x46elks_checkaccount(self):
        response = requests.get("https://%s:%s@api.46elks.com/a1/me" % (self.x46elks_account_sid , self.x46elks_auth_token))
        
        _logger.error('get response %s %s %s' % (response.status_code,response.ok,response.content))
        if response.ok:
            res = json.loads(response.content)
            if res.get('name'):
                self.name = res['name']
                self.x46elks_type = 'sub'
            if res.get('displayname'):
                self.name = res['displayname']
                self.x46elks_type = 'main'
            if res.get('mobilenumber'):
                self.x46elks_mobilenumber = res['mobilenumber']
            if res.get('balance'):
                self.x46elks_balance = res['balance'] / 100.0 / 100.0
            if res.get('email'):
                self.x46elks_email = res['email']
                
            currency = self.env['res.currency'].search([('name','=',res.get('currency'))])
            if currency:
                self.x46elks_currency = currency
                
    @api.one
    def x46elks_checknumber(self):
        response = requests.get("https://%s:%s@api.46elks.com/a1/Numbers" % (self.x46elks_account_sid , self.x46elks_auth_token))
        
        _logger.error('get response %s %s %s' % (response.status_code,response.ok,response.content))
        if response.ok:
            res = json.loads(response.content)
            raise Warning(res)


    @api.one
    def x46elks_checkmessages(self):
        
        def _get_status(status):
            if message.get('status') == 'delivered':
                return 'DELIVRD'
            if message.get('status') == 'sent':
                return 'successful'
            if message.get('status') == 'failed':
                return 'UNDELIV'


        response = requests.get("https://%s:%s@api.46elks.com/a1/SMS" % (self.x46elks_account_sid , self.x46elks_auth_token))
        _logger.error('get response %s %s %s' % (response.status_code,response.ok,response.content))
        if response.ok:
            res = json.loads(response.content)
            for message in res.get('data'):
                _logger.error('%s' % message)
                sms = self.env['sms.message'].search([('sms_gateway_message_id','=',message.get('id'))])
                if not sms:
                    self.env['sms.message'].create({
                        'sms_gateway_message_id': message.get('id'),
                        'status': _get_status(message.get('status')),
                        'message_date': message.get('delivered'),
                        'direction': 'I' if message.get('direction') == 'incoming' else 'O',
                        'from_mobile': message.get('from'),
                        'to_mobile': message.get('to'),
                        'created': message.get('created'),
                        'flashsms': message.get('flashsms'),
                        'parts': message.get('parts'),
                        'cost': message.get('cost'),
                        'sms_content': message.get('message'),
                        'account_id': self.id,
                    })

                #~ self.x46elks_last_check_date = fields.Date.now()
    


