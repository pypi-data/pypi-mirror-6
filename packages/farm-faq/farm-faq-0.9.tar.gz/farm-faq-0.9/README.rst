========
farm-faq
========

Overview
========
A django application which provides all you need to implement an FAQs page. Includes django-cms hooks.

Installation
============
* Install with ``pip install farm-faq``.
* Add ``faq`` to your installed apps.
* Add ``faq.context_processors.faq_categories`` to your ``TEMPLATE_CONTEXT_PROCESSORS``.
* Run ``manage.py syncdb``.
* Run ``manage.py migrate faq``.

Usage
=====
First you will need to add at least one ``FAQ Question`` in the admin.
You can then either include the default templates like this:

* List of questions ``{% include 'faq/list.html' %}``
* Questions and answers ``{% include 'faq/items.html' %}``

Or create your own.

License
=======
Imperavi Redactor is licensed under Creative Commons Attribution-NonCommercial 3.0 license.

For commercial use please buy license here: http://redactorjs.com/download/ or use earlier version.

## Contact
jon@wearefarm.com
