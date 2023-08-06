
.. _settings:

==============
Settings Files
==============

.. currentmodule:: engineer.conf

Engineer is configured using a simple settings file (or several settings files if you so desire). The file should
contain the desired site settings in `YAML <http://pyyaml.org/wiki/PyYAMLDocumentation#YAMLsyntax>`_. A typical
settings file looks like this:

.. code-block:: yaml

    SITE_TITLE: Engineer Site
    HOME_URL: '/'
    SITE_URL: http://localhost:8080

    PUBLISH_DRAFTS: no
    POST_DIR:
      - posts
      - archives

    THEME_SETTINGS:
      typekit_id: vty2qol
      twitter_id: tylerbutler
      tweet_count: 4

    POST_TIMEZONE: 'America/Los_Angeles'

All top-level Engineer settings are in all caps with underscores separating words. Themes or other plugins may have
their own specific settings that do not follow this convention. A comprehensive list of all the settings is below,
but in practice only a few of them are needed.


Content Location Settings
=========================

These settings control the location on the local file system where Engineer should either look for or output files.

.. class:: EngineerConfiguration

   .. attribute:: SETTINGS_DIR

      **Default:** path to folder containing settings file

      The path to the directory containing the settings file used. This is usually set automatically based on the
      location of the settings file used.


   .. attribute:: CONTENT_DIR

      **Default:** ``SETTINGS_DIR/content``

      The path to the directory that contains any :ref:`raw content` for the site. Raw content includes things like
      favicons, :file:`robots.txt` files, etc. Raw content is always processed last in :ref:`build pipeline`,
      so anything in this folder will overwrite any automatically generated content.


   .. attribute:: POST_DIR

      **Default:** ``[SETTINGS_DIR/posts]``

      A list of paths that contain :doc:`posts` for the site. You can specify a single path here or multiple paths.
      When specifying multiple paths the files will always be processed in their original directory.

      .. seealso::
         :ref:`build pipeline`


   .. attribute:: OUTPUT_DIR

      **Default:** ``SETTINGS_DIR/output``

      The path that the generated site should be output to. By using multiple settings files,
      each with a different ``OUTPUT_DIR`` setting, it is easy to push out multiple copies of a site to different
      locations without changing anything in the source files.


   .. attribute:: TEMPLATE_DIR

      **Default:** ``SETTINGS_DIR/templates``

      The path to the directory containing site-specific :doc:`templates`, including templates used for themes.

      .. seealso::
         :doc:`themes`


   .. attribute:: TEMPLATE_PAGE_DIR

      **Default:** ``TEMPLATE_DIR/pages``

      The path to the directory containing :ref:`template pages`. These can be outside your standard
      :attr:`~engineer.conf.EngineerConfiguration.TEMPLATE_DIR` if you wish; for example,
      you may set this to be ``/pages`` and place your template pages in the root of your site content directory
      rather than with other templates.

      .. seealso::
         :ref:`template pages`, :doc:`themes`


   .. attribute:: CACHE_DIR

      **Default:** ``SETTINGS_DIR/_cache/<settings file name>/``

      The path Engineer should place its caches. This location should be unique per config,
      and by default varies based on the name of the settings file used. **In general you should not
      need to modify this.**


   .. attribute:: CACHE_FILE

      **Default:** ``CACHE_DIR/engineer.cache``

      The Engineer cache file location. **In general you should not need to modify this.**


   .. attribute:: OUTPUT_CACHE_DIR

      **Default:** ``CACHE_DIR/output_cache``

      The Engineer output cache directory. **In general you should not need to modify this.**


   .. attribute:: JINJA_CACHE_DIR

      **Default:** ``CACHE_DIR/jinja_cache``

      The Jinja cache directory. **In general you should not need to modify this.**


   .. attribute:: BUILD_STATS_FILE

      **Default:** ``CACHE_DIR/build_stats.cache``

      The Engineer build stats cache file location. **In general you should not need to modify this.**


   .. attribute:: LOG_DIR

      **Default:** ``SETTINGS_DIR/logs``

      The Engineer log directory. All build logs will be stored in this directory. **In general you should not need
      to modify this.**


   .. attribute:: LOG_FILE

      **Default:** ``LOG_DIR/build.log``

      TODO


Site Settings
=============

.. class:: EngineerConfiguration

   .. attribute:: SITE_TITLE

      **Default:** ``'SITE_TITLE'``

      The title of your site. Where this text appears depends on your theme, but you should always set it since it
      usually appears very prominently, such as in the main header.


   .. attribute:: SITE_URL

      **Default:** ``'SITE_URL'``

      The absolute URL to your site. For example, ``http://tylerbutler.com/``. This is used to generate some links in
      your site, so it should be accurate. In general, Engineer generates relative URLs for use internally,
      but there are some cases, such as the RSS feed, that require the absolute URL.


   .. attribute:: HOME_URL

      **Default:** ``'/'``

      The root URL to your site. By default this is set to ``/`` which assumes your Engineer site will live
      at the root of a domain. However, if you're putting your site at http://example.com/blog, for example,
      you would set this to ``/blog`` so Engineer would generate URLs correctly for you.


   .. attribute:: STATIC_URL

      **Default:** ``HOME_URL/static``

      The relative URL to your static content such as JavaScript and CSS files.


   .. attribute:: PERMALINK_STYLE

      **Default:** ``fulldate``

      .. note:: While the ``fulldate`` style is the current Engineer default, this will change in an upcoming
         version. If you wish to continue using that style, you should update your settings files to specify the
         fulldate style rather than rely on the default.

      A format string that controls how links to your posts are formatted. You can use one of the built-in permalink
      styles (described below) or provide a custom one. Permalink format strings should use standard
      `Python string formatting <http://docs.python.org/library/string.html#format-specification-mini-language>`_.
      The following named parameters are available for you to use in your format string:

      ``year``
         The year portion of the post's timestamp as an integer.

      ``month``
         The month portion of the post's timestamp as string - includes a leading zero if needed.

      ``day``
         The day portion of the post's timestamp as a string - includes a leading zero if needed.

      ``i_month``
         The month portion of the post's timestamp as an integer.

      ``i_day``
         The day portion of the post's timestamp as an integer.

      ``title`` (or ``slug``)
         The post's slug.

      ``timestamp``
         The post's timestamp as a datetime.

      ``post``
         The post object itself.

      Using the post and timestamp parameters you can create complex permalink styles, but for most purposes the
      year/month/day/slug convenience parameters are enough and simpler to use.

      **Built-in styles:**

      Engineer also provides some styles you can use directly. Simply use the name of the style below instead of
      defining your own.

      +--------------+----------------------------------------------+
      | Style        | Format String                                |
      +==============+==============================================+
      | ``pretty``   | ``{year}/{month}/{title}/``                  |
      +--------------+----------------------------------------------+
      | ``fulldate`` | ``{year}/{month}/{day}/{title}/``            |
      +--------------+----------------------------------------------+
      | ``slugdate`` | ``{year}/{month}/{day}/{title}.html``        |
      +--------------+----------------------------------------------+


   .. attribute:: SITE_AUTHOR

      **Default:** ``None``

      The name of the primary author of your site. May be used by themes.


   .. attribute:: ROLLUP_PAGE_SIZE

      **Default:** ``5``

      This setting controls how many posts are displayed on a rollup page such as the main site home page.


   .. attribute:: URLS

      **Default:** n/a

      TODO


RSS Feed Settings
=================

.. class:: EngineerConfiguration

   .. attribute:: FEED_TITLE

      **Default:** ``SITE_TITLE Feed``

      The title of the site's RSS feed.


   .. attribute:: FEED_ITEM_LIMIT

      **Default:** ``ROLLUP_PAGE_SIZE``

      Controls how many posts are listed in the site RSS feed.


   .. attribute:: FEED_DESCRIPTION

      **Default:** ``The FEED_ITEM_LIMIT most recent posts from SITE_TITLE.``

      The description of the site's RSS feed.


   .. attribute:: FEED_URL

      **Default:** ``HOME_URL/feeds/rss.xml``

      The URL of the site's RSS feed. This only affects the links to the feed that
      are output in templates using :ref:`urlname('feed') <urlname>`. The feed itself
      will still be written out to ``HOME_URL/feeds/rss.xml``, so you can
      configure a Feedburner URL, for example, as your feed URL, and then point
      Feedburner to ``HOME_URL/feeds/rss.xml``.


Theme Settings
==============

.. seealso::
   :doc:`themes`

.. class:: EngineerConfiguration

   .. attribute:: THEME

      **Default:** ``dark_rainbow``

      The :ref:`ID <theme id>` of the theme to be used for the site.


   .. attribute:: THEME_DIRS

      **Default:** ``None``

      A list of paths that contain :doc:`themes` for the site. You can specify a single path here or multiple paths.

      .. note::
         You do not need to use this setting if custom themes are found inside the :file:`themes` folder within the
         site's folder.

      .. versionadded:: 0.2.3


   .. attribute:: THEME_SETTINGS

      **Default:** ``{}``

      Any theme-specific settings. This is a dictionary of settings that the theme in use will use. What is
      appropriate for this setting differs based on the theme.


   .. attribute:: THEME_FINDERS

      **Default:** ``['engineer.finders.ThemeDirsFinder', 'engineer.finders.SiteFinder',
      'engineer.finders.DefaultFinder']``

      TODO

      .. versionchanged:: 0.2.3


Preprocessor/Compressor Settings
================================

.. seealso::
   :ref:`build pipeline`

.. class:: EngineerConfiguration

   .. attribute:: COMPRESSOR_ENABLED

      **Default:** ``True``

      If ``True``, JavaScript and CSS files will be minified as part of the site generation process.


   .. attribute:: COMPRESSOR_FILE_EXTENSIONS

      **Default:** ``['js', 'css']``

      The file extensions that should be minified.

      .. note::
         This setting shouldn't be used at this point - it's there because there are plans to make the minification
         process more configurable.


   .. attribute:: PREPROCESS_LESS

      **Default:** ``True``

      If ``True``, LESS files will be processed into CSS files (which will then be minified if needed) as part of the
      site generation process.


   .. attribute:: LESS_PREPROCESSOR

      **Default:** bundled dotLESS compiler on Windows, :program:`lessc` elsewhere

      If you want to use another LESS processor, or you need to specify a path to :program:`lessc`,
      you can use this setting. On Windows the dotLESS compiler is bundled, but on other platforms you'll need to
      download and install LESS and lessc yourself.


Miscellaneous Settings
======================

.. class:: EngineerConfiguration

   .. attribute:: ACTIVE_NAV_CLASS

      **Default:** ``current``

      When set, active navigation links (output using the :ref:`navigation_link<navigation>` macro) will have the
      specified class.

      .. note::
         This value can still be overridden in individual calls to ``navigation_link`` by passing an ``active_class``
         parameter.

   .. attribute:: DEBUG

      **Default:** ``False``

      This flag is used to designate a site is in debug mode. Templates or other Engineer code might output content
      slightly differently in debug mode to provide more details about the rendering process. This should *always* be
      set to ``False`` when building a site for production.

      .. note::
         This setting is different than the :option:`--verbose <engineer -v>` option passed into the Engineer
         commandline. The ``--verbose`` option only changes the level of output at the command line. The ``DEBUG``
         setting can be used to change up actual template rendering or code processing.


   .. attribute:: NORMALIZE_INPUT_FILES

      .. deprecated:: 0.4.0
         This setting is now ignored. Use :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`
         and :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA_CONFIG` instead.


   .. attribute:: NORMALIZE_INPUT_FILE_MASK

      .. deprecated:: 0.4.0
         This setting is now ignored. Use :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`
         and :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA_CONFIG` instead.


   .. attribute:: PUBLISH_DRAFTS

      **Default:** ``False``

      If ``True``, posts that have draft :ref:`status <post status>` will be considered published during site
      generation. This can be useful to test out how a new post might look on the site without worrying that you'll
      forget to change its status back to draft before you do a *real* build.


   .. attribute:: PUBLISH_PENDING

      **Default:** ``False``

      Ordinarily Engineer only generates output for posts whose :ref:`timestamp <post timestamp>` is in the past.
      Published posts that have a future date are considered 'pending.' When ``PUBLISH_PENDING`` is ``True``,
      Engineer will output these future posts regardless of the current time.


   .. attribute:: PUBLISH_REVIEW

      **Default:** ``False``

      If ``True``, posts marked with a status of :attr:`~engineer.enums.Status.review` will be output. This is
      useful for draft posts that you want to preview in the context of a site. These posts can be marked ``review``
      and a settings file with ``PUBLISH_REVIEW`` set to true can be used to output them for review purposes. Using
      :attr:`~engineer.enums.Status.review` instead of :attr:`~engineer.enums.Status.published` and
      :attr:`PUBLISH_PENDING` helps preview posts without setting arbitrary dates in the future and eliminates
      concerns about accidental publication.


   .. attribute:: POST_TIMEZONE

      **Default:** System default timezone

      If your posts are primarily posted from a specific timezone, you can set this setting to instruct Engineer to
      assume that the timestamps in posts are in this timezone.

      .. seealso::
         :ref:`timezones`


   .. attribute:: SERVER_TIMEZONE

      **Default:** POST_TIMEZONE

      If the server hosting your site is in a different timezone than you are, you can set this setting so Engineer
      knows to adjust times appropriately. This is necessary mostly for :doc:`Emma <emma>`; it shouldn't affect
      generating your site in most cases.

      .. seealso::
         :ref:`timezones`


   .. attribute:: TIME_FORMAT

      **Default:** ``%I:%M %p %A, %B %d, %Y %Z``

      TODO


   .. attribute:: PLUGINS

      **Default:** None

      A list of modules that contain Engineer :ref:`plugins`.

      .. seealso::
         :ref:`plugins`


.. _settings inheritance:

Settings File Inheritance
=========================

A settings file can inherit settings from another file. The inheritance model is what one would expect - it is
similar to class inheritance in most programming languages.

In order to do this, you set the ``SUPER`` setting in your settings file to the path of the settings file. For
example, you might have a file called :file:`base.yaml` that contains your :attr:`~EngineerConfiguration.SITE_TITLE`,
:attr:`~EngineerConfiguration.POST_DIR`, :attr:`~EngineerConfiguration.SITE_URL`,
:attr:`~EngineerConfiguration.HOME_URL`, etc., and a second file called :file:`production.yaml` that looks like this::

    SUPER: base.yaml
    OUTPUT_DIR: <path to output dir>

When you do a build using :file:`production.yaml`, the settings from :file:`base.yaml` will be loaded first,
then the settings from :file:`production.yaml` will be loaded. The settings in :file:`production.yaml` will always
'win,' so any settings present in both will use the value specified in :file:`production.yaml`.

Inheritance can span more than two files. In our example, if :file:`base.yaml` inherited from another settings file,
those settings would be loaded, then :file:`base.yaml`, *then* :file:`production.yaml`. This nesting can be arbitrarily
deep, though it gets unwieldy after about three or four levels.

A given settings file can only directly inherit from a single parent.
