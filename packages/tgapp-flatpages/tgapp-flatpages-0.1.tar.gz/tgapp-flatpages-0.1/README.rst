About flatpages
-------------------------

flatpages is a Pluggable application for TurboGears2 meant
to simply management of simple static pages inside your
TurboGears application.

Instead of creating a controller and template for "About",
"Contacts" and similar pages, just plug flatpages and
edit them directly from the administration interface.

Installing
-------------------------------

flatpages can be installed both from pypi or from bitbucket::

    pip install tgapp-flatpages

should just work for most of the users

Plugging flatpages
----------------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with flatpages::

    plug(base_config, 'flatpages')

You will be able to access the plugged application 
management interface at *http://localhost:8080/pages/manage*
while all the pages you create will be served at
*http://localhost:8080/pages/PAGENAME*.

Restricting access to pages
-----------------------------

flatpages supports restricting access to pages only to users
that has a specific permission. When creating the page
set it to *Public*, *Only Registered Users* or any of
the ``Permission`` your application provides.

Loading pages from file
-----------------------------

When working with static pages it's often easier to include
the starting version or new versions into the source code itself
instead of providing a database migration each time the content
has to be changed.

To allow this, flatpages permits to load the page content
from a file local to the application itself. To do so
it's sufficient to set ``file://path/relative/to/application/package``
as the content of the static page.

Options
-----------------------------

flatpages exposes some options to control the behavior when
rendering a page, pass this to the plug call to set them:

  * ``format`` -> This is the format used to render the page content,
    can be **html** or **rst** if you store pages in RST or HTML format.

  * ``templates`` -> This is a list of the templates available to render
    the pages. Each entry is in the form: ``("engine:package.templates.path", "Template Description")``.

