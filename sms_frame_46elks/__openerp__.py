{
    'name': "SMS Framework - 46elks Gateway",
    'version': "1.0",
    'author': "Vertel AB",
    'category': "Tools",
    'support': "support@vertel.se",
    'summary': "Adds 46elks sms gatway to the sms framework",
    'license':'LGPL-3',
    'data': [
        'data/sms.gateway.csv',
        'views/sms_account.xml',
        'views/ir_actions_todo.xml',
        'views/sms_message.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'depends': ['sms_frame','mail'],
    'images':[
        'static/description/3.jpg',
        'static/description/1.jpg',
        'static/description/2.jpg',
    ],
    'installable': True,
}