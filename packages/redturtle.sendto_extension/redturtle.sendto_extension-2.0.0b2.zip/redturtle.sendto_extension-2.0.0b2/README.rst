Enhance the "Send this page" Plone feature providing a complex form for send the link to a page to
**multiple recipients**, **members** of the portal and **groups**.

.. contents::

Introduction
============

Normally Plone gives you a feature for sending the link to a page to someone (a feature that is still available on
Plone 4, but is hidden): calling the ``/sendto_form`` view on a document.

.. image:: http://blog.redturtle.it/pypi-images/redturtle.sendto_extension/redturtle.sendto_extension-2.0.0a1-00.png/image_mini
   :alt: Default Plone send to form
   :align: right
   :target: http://blog.redturtle.it/pypi-images/redturtle.sendto_extension/redturtle.sendto_extension-2.0.0a1-00.png

The default Plone form for sending the page is missing some features like:

* captcha protection
* sending to multiple recipients
* sending to users and groups
* manage BCC

If you need the "*send to*" feature and one or more of features above, this add-on if for you.

How to use
==========

After installation the "Send to" action will show you a totally new interface.

.. image:: http://blog.redturtle.it/pypi-images/redturtle.sendto_extension/redturtle.sendto_extension-2.0.0a1-01.png/image_preview
   :alt: New send to form
   :align: right
   :target: http://blog.redturtle.it/pypi-images/redturtle.sendto_extension/redturtle.sendto_extension-2.0.0a1-01.png

Add me to recipients
--------------------

Checking this will add the sender to the recipients list, for getting a copy of the message

Message
-------

You can choose a personal message to be sent with the link. The message will be part of the mail body, while the
**general message format can be configured** in the site control panel ("*Send to form settings*").

Send to
-------

This field (and the "BCC" alternative) accept a list of e-mail addresses, to send the message to **multiple recipeints**.
For security reason you can disabled this multiple recipients field and going back to a single recipient,
changing the proper site permission (by default, only authenticated members can use the multiple recipient feature).

Send to site members
--------------------

This field (and the "BCC" alternative) provide an autocomplete **selection of site members** to send the document to.
For security reason you can disabled the user selection field changing the proper site permission
(by default, only authenticated members can query for site members).

Send to groups
--------------

Same as before, but query for **groups**. All users inside those groups will be notified.

Anonymous usage
===============

.. image:: http://blog.redturtle.it/pypi-images/redturtle.sendto_extension/redturtle.sendto_extension-2.0.0a1-02.png/image_preview
   :alt: Send to form for anonyomus
   :align: right
   :target: http://blog.redturtle.it/pypi-images/redturtle.sendto_extension/redturtle.sendto_extension-2.0.0a1-02.png

This add-on is mainly designed for large intranets, but in the case you want to use it on a public site it's configured
to not transform your site in a SPAM source.

All main features are disabled by default, and you can also enabled a **captcha protection** from the Plone control panel
("*Send to form settings*").

Dependency
==========

Tested on Plone 4.3

Credits
=======

Developed with the support of `Camera di Commercio di Ferrara`__;
Camera di Commercio di Ferrara supports the `PloneGov initiative`__.

.. image:: http://www.fe.camcom.it/cciaa-logo.png/
   :alt: CCIAA Ferrara - logo

__ http://www.fe.camcom.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
