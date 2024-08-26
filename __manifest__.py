{
    'name': 'GEVI_SIS',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Módulo para gestión de servicios con cotizaciones y seguimiento',
    'description': """
        Este módulo permite la gestión completa de servicios, incluyendo:
        - Cotizaciones de servicio
        - Órdenes de servicio
        - Programación de visitas técnicas
        - Portal del cliente para seguimiento de servicios
    """,
    'author': 'GEVI',
    'website': 'https://www.suempresa.com',
    'depends': ['base', 'mail', 'calendar', 'contacts', 'sale', 'stock', 'portal'],
    'data': [
        'security/service_security.xml',
        'security/ir.model.access.csv',
        'views/service_quotation_views.xml',
        'views/service_order_views.xml',
        #'views/res_partner_views.xml',
        #'views/service_team_views.xml',
        'views/service_visit_views.xml',
        'views/service_dashboard.xml',
       # 'data/service_sequence.xml',
        #'data/mail_template_data.xml',
       # 'report/service_reports.xml',
        'wizard/assign_technician_views.xml',
        'views/portal_templates.xml',
        'views/service_menus.xml',
    ],
    'demo': [
        #demo/service_demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}