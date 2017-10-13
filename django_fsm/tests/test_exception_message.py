from django.db import models
from django.test import TestCase

from django_fsm import FSMField, TransitionNotAllowed, transition, can_proceed
from django_fsm.signals import pre_transition, post_transition


PAY_MESSAGES = {
    'paid': 'This order was paid. You cannot pay it again.',
    'shipping': 'The order is shipping.',
    'delivered': 'this order was finished.'
}

DISPATCH_MESSAGES = {
    'pending': 'You need pay order.',
    'shipping': 'The order already is shipping.',
    'delivered': 'the order already is delivered.'
}

DELIVERY_MESSAGES = {
    'pending': 'First, you need pay the order.',
    'paid': 'Keep calm. The order is paid.',
    'delivered': 'This order was delivered.'
 }

class Order(models.Model):
    
    state = FSMField(default='pending')

    @transition(field=state, source='pending', target='paid', exceptions_message=PAY_MESSAGES)
    def pay(self):
        pass
    
    @transition(field=state, source='paid', target='shipping', exceptions_message=DISPATCH_MESSAGES)
    def dispatch(self):
        pass

    @transition(field=state, source='shipping', target='delivered', exceptions_message=DELIVERY_MESSAGES)
    def delivery(self):
        pass


class ExceptionMessageTest(TestCase):

    def test_dispatch_pending_message(self):
        model = Order()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.dispatch()
        exp = ctx.exception
        self.assertEqual(str(exp), DISPATCH_MESSAGES['pending'])

    def test_delivery_pending_message(self):
        model = Order()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.delivery()
        exp = ctx.exception
        self.assertEqual(str(exp), DELIVERY_MESSAGES['pending'])

    def test_pay_paid_message(self):
        model = Order()
        model.pay()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.pay()
        exp = ctx.exception
        self.assertEqual(str(exp), PAY_MESSAGES['paid'])
    
    def test_delivery_paid_message(self):
        model = Order()
        model.pay()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.delivery()
        exp = ctx.exception
        self.assertEqual(str(exp), DELIVERY_MESSAGES['paid'])

    def test_pay_shipping_message(self):
        model = Order()
        model.pay()
        model.dispatch()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.pay()
        exp = ctx.exception
        self.assertEqual(str(exp), PAY_MESSAGES['shipping'])

    
    def test_dispatch_shipping_message(self):
        model = Order()
        model.pay()
        model.dispatch()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.dispatch()
        exp = ctx.exception
        self.assertEqual(str(exp), DISPATCH_MESSAGES['shipping'])

    def test_pay_delivered_message(self):
        model = Order()
        model.pay()
        model.dispatch()
        model.delivery()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.pay()
        exp = ctx.exception
        self.assertEqual(str(exp), PAY_MESSAGES['delivered'])

    def test_dispatch_delivered_message(self):
        model = Order()
        model.pay()
        model.dispatch()
        model.delivery()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.dispatch()
        exp = ctx.exception
        self.assertEqual(str(exp), DISPATCH_MESSAGES['delivered'])

    def test_delivery_delivered_message(self):
        model = Order()
        model.pay()
        model.dispatch()
        model.delivery()
        with self.assertRaises(TransitionNotAllowed) as ctx:
            model.delivery()
        exp = ctx.exception
        self.assertEqual(str(exp), DELIVERY_MESSAGES['delivered'])
