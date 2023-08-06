Webtopay (mokejimai.lt) integration app for Django web framework
================================================================

Inspired by django-paypal

How to use
----------

1. install django-webtopay
2. add ``WEBTOPAY_PASSWORD='pass'`` to your settings file
3. Add callback url::
   url(r'^wtp/', include('webtopay.urls.makro'))
   (it should be relatively hard to guess)
4. Create a form for submission::

    form = WebToPaymentForm(
        dict(projectid = 123123,
            orderid = '3c3662bcb661d6de679c636744c66b62',
            accepturl = request.build_absolute_uri(),
            cancelurl = request.build_absolute_uri(),
            callbackurl = reverse('webtopay-makro'),
            paytext = "Payment for services",
            p_firstname = "Vardenis",
            p_lastname = "Pavardenis",
            p_email = "vardenis@pavardenis.lt",
            amount = 989, # 9 Lt 89 ct
            test = 1
            ),
        button_html="<input type='submit' value='Pay!'/>",
    )

5) Catch a django signal when the payment is completed::

    from webtopay.signals import payment_was_successful
    def process_payment(**kargs):
        trans = kargs['sender']
        if price_i_expect * 100 != trans.amount:
            log.error("Received wrong amount. Expected: %d, got: %d",\
                price_i_expect*100, trans.amount)
            return
        paid = True
        # from this point we assume customer paid
        #...
    payment_was_successful.connect(process_payment)

You should catch payment_was_flagged signal if you want to know when something
went wrong::

    from webtopay.signals import payment_was_flagged
    def investigate_payment(**kargs):
        # kargs['sender'] is an instance of WebToPayResponse.
        # All fields are documented in webtopay/models.py
        log.warn("Payment went wrong for %s, please investigate",
            kargs['sender'].orderid)
    payment_was_flagged.connect(investigate_payment)


If you have any questions or problems, please use *issues* page.

|travis|_

.. |travis| image:: https://travis-ci.org/Motiejus/django-webtopay.png
.. _travis: https://travis-ci.org/Motiejus/django-webtopay
