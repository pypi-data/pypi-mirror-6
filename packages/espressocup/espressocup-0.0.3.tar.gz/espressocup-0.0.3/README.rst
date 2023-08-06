Why? What?
==========

I'm making a very light-weight internal network service, and am using
the amazing flask, as it's excellent for prototyping such things.

However, I feel like it's a little over-weight for the simplicity of the
task.  So, out of curiosity, I'm trying to make a flask-alike server
and WSGI microframework which has just enough for these types of projects.

It's not intended to replace flask, obviously.  There's no point.

But it is intended that for things like this which don't need a templating
language, or any of that, it should be close enough to flask that I can
drop this in, and with minimal changes have it running very quickly.

current state:
==============

very very very initial alpha.  For pure JSON based views, it's kind of
working.  For templating, it's using pythons string.format instead of
jinja2.

Routes currently don't use variables, but are just a plain lookup.

static files seem to be (initially) working.

mime detection of template types isn't really working yet.

All that said:

It's quite fast. (Ha, no surprise, with all those caveats...)

broken stuff:
=============

- the 'request' object is just the pure WSGI environ at the moment.
- MIME types for templates (and static files)
- routing <with><vars>

