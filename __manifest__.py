# __manifest__.py

{
    'name': 'Alquiler de Productos',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gestión de alquiler de productos',
    'description': 'Gestión de préstamos de productos en alquiler para clientes',
    'author': 'Gonzalo Carretero',
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/alquiler_producto_views.xml'
    ],
    'icon': '/alquiler_producto/static/description/icon56.png',
    'installable': True,
    'application': True,
}
