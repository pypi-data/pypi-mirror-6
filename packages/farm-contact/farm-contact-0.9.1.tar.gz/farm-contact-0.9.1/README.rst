============
farm-contact
============

Overview
========
A django application which provides a contact form which sends an email and stores its details in the database.

Installation
============
* Install with ``pip install farm-contact``.
* Add ``contact`` to your installed apps.
* Add ``contact.context_processors.contact_form`` to your ``TEMPLATE_CONTEXT_PROCESSORS``.
* Set ``ENQUIRY_SUBJECT="Enquiry"`` or whatever you want it to be (defaults to Contact Form Enquiry).
* Run ``manage.py syncdb``.
* Run ``manage.py migrate contact``.

Usage
=====
First you will need to add at least one ``Enquiry type`` in the admin.
You can then either include the default template like this:

``{% include 'contact/index.html' %}``

Or create your own.

Contact
=======
jon@wearefarm.com
