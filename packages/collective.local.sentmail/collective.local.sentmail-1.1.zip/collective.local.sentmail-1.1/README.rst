==========================
collective.local.sentmail
==========================

.. image:: https://secure.travis-ci.org/collective/collective.local.sentmail.png
    :target: http://travis-ci.org/collective/collective.local.sentmail

INTRODUCTION
------------

This module creates a "Sent mails" folder in your portal root. Each time a IMailSentEvent is launched, it creates a SentMail item in this folder with the event's attributes (subject, body and recipients).

Sent mails are visible only by their owner (the mail's sender) and editable by nobody.

A IMailSentEvent implementation example can be found in collective.local.sendto package.

CREDITS
-------

Authors :
 * Cédric Messiant (cedric.messiant@gmail.com)
 * Vincent Fretin (vincent.fretin@gmail.com)

COMPATIBILITY
-------------

Plone 4.3
