CHANGELOG
=========

Version 0.1.3

- The data mapper factories (SQLAlchemy and Storm) support querying for
  existing objects in fixtures
- Added experimental SQLAlchemy support

Version 0.1.2

- Made setting factoryoptions more flexible. It's now possible to change the
  default flush/commit behavior of StormFactory per fixture class and or at
  setup time when using the context manager syntax.

Version 0.1.1

- Bugfix: StormFactory did not flush/commit the store on fixture teardown
  teardown, meaning the store would not be left clean for subsequent operations

Version 0.1

- initial release
