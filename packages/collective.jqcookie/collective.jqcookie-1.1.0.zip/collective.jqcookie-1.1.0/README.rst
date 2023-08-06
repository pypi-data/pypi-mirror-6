Introduction
============

Adds an 8 year old version of `jquery-cookie <https://github.com/carhartl/jquery-cookie>`_ to plone.

Usage
=====

Set the value of a cookie.

    $.cookie('the_cookie', 'the_value');

Create a cookie with all available options.

    $.cookie('the_cookie', 'the_value', { expires: 7, path: '/', domain: 'jquery.com', secure: true });

Create a session cookie.

    $.cookie('the_cookie', 'the_value');

Delete a cookie by passing null as value. Keep in mind that you have to use the same path and domain used when the cookie was set.

    $.cookie('the_cookie', null);

Links
=====

* Main github project repository: https://github.com/4teamwork/collective.jqcookie
* Issue tracker: https://github.com/4teamwork/collective.jqcookie/issues

Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``collective.jqcookie`` is licensed under GNU General Public License.
