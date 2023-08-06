About tgext.scss
-------------------------

`SCSS <http://sass-lang.com/>`_ is a cool and useful extension to CSS,
but it always required some effort to be used and even
specific production environment configurations for some systems.

tgext.scss has born to make life easier for `TurboGears2  <http://www.turbogears.org>`_ developers,
it will rely on an internal minimal SCSS compiler
(based on `Zeta-Library <https://github.com/klen/zeta-library>`_ SCSS parser)
to serve all the files in your public directory
that end with *.scss* as **text/css** converting them and minifying them.

Installing
-------------------------------

tgext.scss can be installed both from pypi or from bitbucket::

    easy_install tgext.scss

should just work for most of the users

Enabling tgext.scss
----------------------------------

If tgext.pluggable is available enabling tgext.scss is just a matter of appending to your `config/app_cfg.py`::

    from tgext.pluggable import plug
    plug(base_config, 'tgext.scss')

Otherwise manually using tgext.scss is really simple, you edit your `config/middeware.py` and just after
the `#Wrap your base TurboGears 2 application with custom middleware here` comment wrap
`app` with `SCSSMiddleware`::

    from tgext.scss import SCSSMiddleware

    make_base_app = base_config.setup_tg_wsgi_app(load_environment)

    def make_app(global_conf, full_stack=True, **app_conf):
        app = make_base_app(global_conf, full_stack=True, **app_conf)

        # Wrap your base TurboGears 2 application with custom middleware here
        app = SCSSMiddleware(app)
    
        return app


Now you just have to put your .scss file inside *public/css* and they will be served as CSS.

@Import Support
-----------------------------------

tgext.scss provides minimal support for @import command. The required syntax is in the form::

    @import url('/css/file.scss');

The specified path is relative to your project public files directory.
*Nested imports are not implemented right now, this means that imported files cannot import another scss*

How much it will slow me down?
-----------------------------------

Actually as tgext.scss uses aggressive caching it won't you slow down at all,
indeed it might even be able to serve you CSS files even faster.

Here is the report of a benchmark (absolutely not reliable as every other benchmark)
made on paster serving the same CSS file or SCSS::

    $ /usr/sbin/ab -n 1000 http://localhost:8080/css/style.css
    Requests per second:    961.26 [#/sec] (mean)

    $ /usr/sbin/ab -n 1000 http://localhost:8080/css/style.scss
    Requests per second:    1200.34 [#/sec] (mean)

In these case SCSS is even faster than directly serving the same css file as
it is served from memory (due to caching performed by tgext.scss)
and is also minified resulting in less bandwith usage.

Off course this means that tgext.scss will require a bit more memory than serving
your css files alone, but as css files are usually small this amount is trascurable.
