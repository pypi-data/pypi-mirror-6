Changes
-------

1.8 (2014-02-15)
~~~~~~~~~~~~~~~~

* Minification script overhaul, now able to automatically determine
  the list of needed scripts given just the application's modules

* Eliminated MP.grid.column.CheckColumn, since it's been integrated
  into ExtJS 4

* Load a custom ext.js, workaround to br0ken ExtJS 4.2.1 bootstrap

* Updated Pyramid scaffold project


1.7 (2014-01-26)
~~~~~~~~~~~~~~~~

* Fix the batching of lookup combos, properly setting the pageSize of
  the store and of the widget itself


1.6 (2014-01-23)
~~~~~~~~~~~~~~~~

* Minor tweaks to the desktop CSS


1.5 (2014-01-20)
~~~~~~~~~~~~~~~~

* UK english translation catalog: thanks to Elisa to enlightening me
  about the fact that the "m/d/Y" date format is a US-only
  idiosyncrasy!

* Stabilized translatable messages extraction


1.4 (2014-01-19)
~~~~~~~~~~~~~~~~

* Fix ExtJS 4.2.1 ColumnManager

* Handle readonly state corner case


1.3 (2014-01-18)
~~~~~~~~~~~~~~~~

* Fix several (mostly minor) i18n issues

* Added an explicit English translation catalog


1.2 (2013-12-30)
~~~~~~~~~~~~~~~~

* Enable ``null`` usage on store's fields, when desiderable (this
  shall be verified: probably it can be always enabled, provided
  metapensiero.sqlalchemy.proxy behaves correctly, as it already
  should)

* Maintain and commit a logically ordered list of changed records


1.1 (2013-12-24)
~~~~~~~~~~~~~~~~

* Fix dictionary lookups combos nullable setting

* Rewrite the ``bump_version`` script to use Versio to handle more
  version schemes


1.0 (2013-12-23)
~~~~~~~~~~~~~~~~

* Ripristinate right-click context menu on grids

* Update Ext.ux.window.Notification to version 2.1.3

* Fix FilterBar on ExtJS 4.2.1

* By default order lookup dictionaries by key, can be changed with
  the special “__sort_by__” entry


0.9 (2013-12-15)
~~~~~~~~~~~~~~~~

* Combo's remoteFilter and remoteSort settings may be overridden now

* Optimized data sent to the server for new records


0.8 (2013-12-12)
~~~~~~~~~~~~~~~~

* Encoding issue on package meta data


0.7 (2013-12-12)
~~~~~~~~~~~~~~~~

* First official release on PyPI


0.6 (2013-12-12)
~~~~~~~~~~~~~~~~

* New MP.form.Panel, a customized form panel

* New CurrencyField, to edit money amounts

* Fix columns width auto-resize

* Do not use external sed to strip <debug>..</debug> section, to
  help poor Window$ users


0.5 (2013-08-04)
~~~~~~~~~~~~~~~~

* Use setuptools instead of distribute

* A function ``shouldBeDisabled()`` may be attached to an Action
  instance, and in such a case it may override the usual
  MP.action.Plugin's ``shouldDisableAction()`` function

* Install ExtJS 4.2.1

* Module.configure() now accepts a third argument, a configuration
  object, which is passed to each called function and also to the
  final callback

* Expose `remoteGroup` configuration option on grids


0.4 (2013-04-26)
~~~~~~~~~~~~~~~~

* The old forceFit configuration on custom grids has been removed as
  its goal is better fulfilled by the new ExtJS 4 flex option on the
  specific columns: it caused layout problems on grids when
  showing/hiding columns

* The background image of the desktop (the wallpaper) may be either
  "tiled", "stretched" or "centered", controlled by the property
  "wallpaperStyle" on the desktop

* Use a more generic name for the main CSS, "app.css" instead of
  "modules.css" (existing apps can either rename the "modules.css" or
  create a "app.css" containing ``@import "modules.css";``)


0.3 (2013-04-05)
~~~~~~~~~~~~~~~~

* New Pyramid scaffold to create a barebones desktop project


0.2 (2013-01-25)
~~~~~~~~~~~~~~~~

* ExtJS 4.2.0 final


0.1 (2012-12-11)
~~~~~~~~~~~~~~~~

* First usable version of the new packaging
