====
Kupu
====

What is Kupu?
=============

Kupu is a cross-browser WYWSIWYG editor. It allows the comfortable
editing of the body of an HTML document. It's client-side (browser)
requirements are one of:

- Mozilla 1.3.1 or higher

- Internet Explorer 5.5 or higher

- Netscape Navigator 7.1 or higher

Server-side there are hardly any requirements, except for some way of
processing data (CGI or something more fancy like PHP, ASP or Python
scripts in Zope).

Kupu is particularly suited for content migration as well as editing.
Content copied from an existing web page is pasted with all formatting
intact. This includes structure such as headings and lists, plus links,
image references, text styling, and other aspects. Copying text from a
word processor with an HTML clipboard - such as MSWord - works exactly
the same.

Kupu will clean up the content before it is sent to the server, and can
send data to the server asynchronously using PUT (which allows the data
to be saved without reloading the page) as well as in a form.

Kupu can be customized on many different levels, allowing a lot of changes
from CSS, but also providing a JavaScript extension API.

Code repository
===============

The code for this extension can be found in Git:
https://github.com/silvacms/Products.SilvaKupu
