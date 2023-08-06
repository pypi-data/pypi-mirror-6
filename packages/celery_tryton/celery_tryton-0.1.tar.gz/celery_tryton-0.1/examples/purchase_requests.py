from itertools import groupby

from celery import Celery, group
from celery_tryton import TrytonTask
from trytond.pool import Pool
from trytond.transaction import Transaction

celery = Celery('purchase_requests')


@celery.task(base=TrytonTask)
def generate_all():
    pool = Pool()
    User = pool.get('res.user')
    Product = pool.get('product.product')
    admin, = User.search([
            ('login', '=', 'admin'),
            ])
    with Transaction().set_user(admin.id), \
        Transaction().set_context(
            User.get_preferences(context_only=True)):
        products = Product.search([
                ('type', 'in', ['goods', 'assets']),
                ('consumable', '=', False),
                ('purchasable', '=', True),
                ], order=[('id', 'ASC')])
        group(generate.s([p.id for _, p in l])
            for _, l in groupby(enumerate(products),
                lambda i: i[0] // 1000))()


@celery.task(base=TrytonTask)
def generate(products):
    pool = Pool()
    User = pool.get('res.user')
    PurchaseRequest = pool.get('purchase.request')
    Product = pool.get('product.product')
    admin, = User.search([
            ('login', '=', 'admin'),
            ])
    with Transaction().set_user(admin.id), \
        Transaction().set_context(
            User.get_preferences(context_only=True)):
        PurchaseRequest.generate_requests(Product.browse(products))
