Changes
-------

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


0.4 (2016-04-26)
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
