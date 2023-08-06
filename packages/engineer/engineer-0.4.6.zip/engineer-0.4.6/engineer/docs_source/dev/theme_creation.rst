
.. currentmodule:: engineer.conf

========================
Creating Your Own Themes
========================

Theme Package Structure
=======================

Themes are essentially a folder with a manifest and a collection of templates and supporting static files (images,
CSS, Javascript, etc.). Custom themes should be put in a :file:`themes` folder within the site's root. You can put
themes elsewhere by specifying the :attr:`~EngineerConfiguration.THEME_DIRS` setting.

A sample theme folder might look like this::

    /theme_id
        - metadata.yaml
        /static
            /scripts
                - script.js
                - ...
            /stylesheets
                - theme.less
                - reset.css
                - ...
        /templates
            /theme
               /layouts
                    - ...
                - _footer.html
                - base.html
                - post_list.html
                - ...

.. _theme manifest:

Theme Manifest
==============

Each theme must contain a file called ``metadata.yaml`` that contains metadata about the theme. The theme manifest
is a simple text file in YAML format. The Dark Rainbow theme manifest looks like this, for example:

.. literalinclude:: ../../themes/dark_rainbow/metadata.yaml
   :language: yaml


Theme Manifest Parameters
-------------------------

.. _theme name:

``name``
    The verbose human-readable name of the theme.


.. _theme id:

``id``
    The ID of the theme. This must match the folder name of the theme and should not contain spaces. This is used
    internally by Engineer to identify the theme.


.. _theme self_contained:

``self_contained`` *(optional)*
    Indicates whether the theme is self-contained or not. Defaults to ``True`` if not specified.

    .. note:: This parameter is not currently used and may be deprecated in the future.


.. _theme description:

``description`` *(optional)*
    A more verbose description of the theme.


.. _theme author:

``author`` *(optional)*
    The name and/or email address of the theme's author.


.. _theme website:

``website`` *(optional)*
    The website where the theme or information about it can be found.


.. _theme license:

``license`` *(optional)*
    The license under which the theme is made available.


.. _theme use_foundation:

``use_foundation`` *(optional)*
    Indicates whether the theme makes use of the Foundation CSS library included in Engineer. Defaults to ``False``.


.. _theme use_lesscss:

``use_lesscss`` *(optional)*
    Indicates whether the theme makes use of the LESS CSS library included in Engineer. Defaults to ``False``.


.. _theme use_modernizr:

``use_modernizr`` *(optional)*
    Indicates whether the theme makes use of the Modernizr library included in Engineer. Defaults to ``False``.


.. _theme use_jquery:

``use_jquery`` *(optional)*
    Indicates whether the theme makes use of the jQuery library included in Engineer. Defaults to ``False``.


.. _theme use_tweet:

``use_tweet`` *(optional)*
    Indicates whether the theme makes use of the Tweet library included in Engineer. Defaults to ``False``.

    .. versionadded:: 0.3.0


.. _theme settings:

``settings`` *(optional)*
    A dictionary of all the themes-specific settings that users of your theme can provide via
    :attr:`~engineer.conf.EngineerConfiguration.THEME_SETTINGS` and their default values. If your theme supports
    custom settings, you **must** specify defaults. Due to the way Engineer loads your theme settings and a user's
    site settings, your settings may not be created at all unless you specify them here.

    .. versionadded:: 0.2.3

    .. seealso:: :ref:`use theme settings`


.. _theme template_dirs:

``template_dirs`` *(optional)*
    A list of paths, each relative to the path to the theme manifest file itself,
    that should be included when searching for theme templates. These paths are in addition to the ``templates``
    folder within the theme's folder itself, and will be searched in the order specified *after* the theme's
    ``templates`` folder.

    Like :ref:`copy_content<theme copy_content>`, this parameter is useful if you are creating multiple themes that
    share common templates. You can specify the paths to the common templates and they will be available during the
    build process.

    .. code-block:: yaml

        template_dirs:
          - '../_shared/templates/'

    .. versionadded:: 0.4.0


.. _theme copy_content:

``copy_content`` *(optional)*
    A list of paths to files or directories that should be copied to the theme's output location during a build. This
    is useful if you are creating multiple themes that all share some common static content (JavaScript files, images,
    etc.). By specifying this parameter, content will be copied to a central location for you during the build
    process so you can include it in your theme templates, LESS files, etc.

    This parameter should be a 'list of lists.' Each entry in the list is a list itself containing two items. The
    first item is the path to the file or folder that should be copied. *This path should be relative to the location
    of the theme manifest.*

    The second parameter should be the target location for the file or folder. *The target path should be relative to
    the static/theme folder in the output folder.*

    For example, consider the following ``copy_content`` parameter in a theme manifest:

    .. code-block:: yaml

        copy_content:
          - ['../Font-Awesome-More/font', 'font']
          - ['../bootswatch/img/', 'img']
          - ['../bootstrap/js/', 'js']

    In this example, the ``../Font-Awesome-More/font`` (a path relative to the location of the theme manifest file
    itself) will be copied to ``static/theme/font``.

    .. versionadded:: 0.4.0


Required Templates
==================

The following templates must be present in a theme's :file:`templates/theme` folder:

* _single_post.html
* base.html
* post_archives.html
* post_detail.html
* post_list.html
* template_page_base.html

You can of course include additional templates or template fragments, for use either internally in your theme, or that
users of your theme can take advantage of to further customize their site.

You should also ensure that your theme templates load the :ref:`built-in fragments` that Engineer users will expect.


RSS and Sitemap Templates
-------------------------

Themes can provide custom templates for the RSS feed and sitemap, just as :ref:`individual sites can <rss template>`.
These templates should be in the theme's :file:`templates/theme` folder.

.. versionadded:: 0.3.0


Required Styles
===============

TODO

.image, .left, .right, .caption


.. _use theme settings:

Referring to Custom Theme Settings in Templates
===============================================

Custom theme settings are available in all Engineer templates. Every template is passed a context variable called
``theme`` that represents the current theme. Any custom settings specified are available as attributes on that
object. For example, if your theme defines a custom setting called ``typekit_id``, then you can refer to that setting
in any Engineer template like so:

.. code-block:: html+jinja

    {# TYPEKIT #}
    <script type="text/javascript"
           src="http://use.typekit.com/{{ theme.typekit_id }}.js"></script>
    <script type="text/javascript">
       try {
           Typekit.load();
       } catch (e) {}
    </script>


Useful Macros
=============

TODO


.. _zipping themes:

Zipping Themes
==============

You can optionally put your theme directory in a zip file. The file should have a ``.zip`` file extension. Engineer
will unzip the folder to a temporary location during a build and load the theme from that temporary location.

.. versionadded:: 0.2.3


Sharing Your Theme
==================

The simplest way to share your theme is to :ref:`zip it up <zipping themes>` and make it available to download. Users
can then download it and use it by placing it in their site's :file:`themes` directory or in another one of their
:attr:`~EngineerConfiguration.THEME_DIRS`.

You may wish instead to deliver your theme as an installable Python package. This allows users to download and install
your theme via ``pip`` or any other tool. See :ref:`theme plugins` for more details.


Add Your Theme to Engineer
--------------------------

If you'd like to make your theme available with the main Engineer application, send a pull request on github.
