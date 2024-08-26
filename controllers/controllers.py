# -*- coding: utf-8 -*-
# from odoo import http


# class ProductClient(http.Controller):
#     @http.route('/product_client/product_client', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_client/product_client/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_client.listing', {
#             'root': '/product_client/product_client',
#             'objects': http.request.env['product_client.product_client'].search([]),
#         })

#     @http.route('/product_client/product_client/objects/<model("product_client.product_client"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_client.object', {
#             'object': obj
#         })

