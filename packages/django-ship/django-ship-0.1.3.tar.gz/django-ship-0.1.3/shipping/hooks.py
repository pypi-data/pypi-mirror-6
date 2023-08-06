#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

try:
    from mezzanine.conf import settings
    from cartridge.shop.utils import set_shipping
    from cartridge.shop.models import Cart
except ImportError,e:
    pass

from shipping.fretefacil import FreteFacilShippingService
from shipping.models import DeliverableProperty

def fretefacil_shipping_handler(request, form, order=None):
    if request.session.get("free_shipping"): return
    settings.use_editable()
    if form is not None: user_postcode = form.shipping_detail_postcode
    else: user_postcode = settings.CLIENT_POSTCODE
    shippingservice = FreteFacilShippingService()
    cart = Cart.objects.from_request(request)
    delivery_value = 0.0
    if cart.has_items():
        for product in cart:
            properties = DeliverableProperty.objects.filter(sku=product.sku)
            if len(properties) > 0:
                props = properties[0]
                deliverable = shippingservice.create_deliverable(settings.STORE_POSTCODE,
                                                                 user_postcode,
                                                                 props.width,
                                                                 props.height,
                                                                 props.length,
                                                                 props.weight)
                delivery_value += float(shippingservice.delivery_value(deliverable))
    set_shipping(request, _("PayPal Frete Fácil"),delivery_value)