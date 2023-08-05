Changelog
=========

0.0.11 (2014/01/26)
-------------------

- Updated the package from a template.

0.0.10 (2013/11/19)
-------------------

- Switched to Python 3.

0.0.9 (2013/09/19)
-------------------

- Prepared files for porting to Python 3

0.0.8 (2013/08/24)
------------------

- Expanded vv-tracking interface to initialize repos and delete builds.
- Now always pushing when builds are created.

0.0.7 (2013/08/01)
------------------

- Added '--no-config' argument to vv-poller/builder to ignore local config.
- Implemented WorkingCopy.copy() method.
- Now always pushing new build requests and updated build statuses.

0.0.6 (2013/07/23)
------------------

- Repository.get_builds() now returns builds descending by start time.

0.0.5 (2013/07/23)
------------------

- Preserving case in setup.cfg options.
- [vv-tracking] 'virtualenv' is a now a boolean (env name: vv-builder-env)
- Now limiting Repository.get_builds() to 50 parsed build requests.

0.0.4 (2013/07/20)
------------------

- Removed pull/push logging on daemons.

0.0.3 (2013/07/20)
------------------

- Daemons now only show logging output on activity.
- Added better repo synchronization in the poller and builder.

0.0.2 (2013/07/19)
------------------

- Added a [vv-tracking] setting to build in a virtualenv: virtualenv=<name>
- Added a [vv-poller] setting to allow rebuilds: <A>_rebuild = True
- Removed the non-ETA states (UP, BP, TP, CP) from the sample build configuration.
- Limiting the rate of automatic push/pull to every 30 seconds.

0.0.1 (2013/07/16)
------------------

- Initial release of python-veracity.

