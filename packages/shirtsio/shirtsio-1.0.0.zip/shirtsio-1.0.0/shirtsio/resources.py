# coding=utf-8
import ast
import logging
from shirtsio.requestor import APIRequestor

logger = logging.getLogger('shirtsio')

api_key = None


class APIResource(object):
    @classmethod
    def dict_params(cls, no_api_key, params):
        api_key_param = {'api_key': api_key}

        if no_api_key:
            return params

        if params:
            return dict(api_key_param, **params)

        return api_key_param

    @classmethod
    def do_request(cls, url=None, params=None, method="get", files=None, no_api_key=False):
        requestor = APIRequestor(api_key)
        params = cls.dict_params(no_api_key, params)
        url = requestor.api_url(url)
        return requestor.request(url, params, method, files)

# This is the encapsulation class for billing requests to Shirt.io
class Payment(APIResource):
    url_payment = "payment/"
    url_payment_status = "payment/status/"

    @classmethod
    def payment(cls, params):
        # https://shirts.io/api/v1/payment/
        return cls.do_request(cls.url_payment, params, method='post')

    @classmethod
    def update_payment_url(cls, params):
        # https://shirts.io/api/v1/payment/status/
        return cls.do_request(cls.url_payment_status, params, method='post')

    @classmethod
    def get_payment_status(cls, params):
        # https://shirts.io/api/v1/payment/status/
        return cls.do_request(cls.url_payment_status, params, method='get')


# This is the encapsulation class for order requests to Shirt.io
class Order(APIResource):
    url_order = "order/"
    url_status = "status/"

    @classmethod
    def place_order(cls, params, files):
        return cls.do_request(cls.url_order, params, method='post', files=files)

    @classmethod
    def get_order_status(cls, params):
        # https://shirts.io/api/v1/status/
        return cls.do_request(cls.url_status, params)


# This is the encapsulation class for products requests to Shirt.io
class Products(APIResource):
    url_products = "products/"
    url_category = "products/category/"

    @classmethod
    def list_categories(cls):
        # https://shirts.io/api/v1/products/category/
        return cls.do_request(cls.url_category)

    @classmethod
    def list_products(cls, category_id):
        # https://shirts.io/api/v1/products/category/{Category_ID}/
        url = cls.url_category + category_id + "/"
        return cls.do_request(url)

    @classmethod
    def get_product(cls, product_id):
        # https://shirts.io/api/v1/products/{Product_ID}/
        url = cls.url_products + product_id + "/"
        return cls.do_request(url)

    @classmethod
    def inventory_count(cls, product_id, color, state=None):
        params = {'color': color, 'state': state}
        inventory = None
        # https://shirts.io/api/v1/products/{Product_ID}/
        url = cls.url_products + product_id + "/"
        result_inventory = cls.do_request(url, params)
        if result_inventory and ('inventory' in result_inventory):
            inventory = result_inventory['inventory']
        return inventory


# This is the encapsulation class for quote requests to Shirt.io
class Quote(APIResource):
    url_quote = "quote/"

    @classmethod
    def get_quote(cls, params):
        # https://shirts.io/api/v1/quote
        return cls.do_request(cls.url_quote, params)


# This is the encapsulation class for webhook registration，list，delete requests to Shirt.io
class Webhook(APIResource):
    url_webhook = "webhooks/"

    @classmethod
    def add_webhook(cls, listener_url):
        url = cls.url_webhook + "register" + "/"
        params = {'url': "'%s'" % listener_url}
        return cls.do_request(url, params, method='post')

    @classmethod
    def delete_webhook(cls, listener_url):
        url = cls.url_webhook + "delete" + "/"
        params = {'url': "'%s'" % listener_url}
        return cls.do_request(url, params, method='post')

    @classmethod
    def list_webhook(cls):
        url = cls.url_webhook + "list" + "/"
        return cls.do_request(url)