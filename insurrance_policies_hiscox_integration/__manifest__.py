{
    'name': 'Insurance Policy Management and Hiscox API Integration',
    'version': '1.0',
    'category': 'Insurance',
    'summary': 'Manage insurance policies, coverage, and premiums and integrate with Hiscox API',
    'author': 'Mohamed Habib Challouf',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/insurance_policy_views.xml',
        'views/hiscox_view.xml',
        'data/cron_jobs.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
