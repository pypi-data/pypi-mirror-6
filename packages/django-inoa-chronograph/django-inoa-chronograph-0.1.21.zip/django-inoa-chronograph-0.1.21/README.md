Chronograph is a simple application that allows you to schedule management commands to be run at regular intervals.
Schedules can be defined in Django's built-in admin interface. Requires cron or a similar tool (e.g. Windows Task Scheduler).

Chronograph has been forked by Inoa (http://www.inoa.com.br) so we could continue to update and maintain the library.
The former version in PyPI was out of date and apparently no longer mantained. Multiple forks exist around the internet
(mainly in GitHub), and we hope to eventually combine the best from all of them.

You can use PyPI to install this library quickly with pip: https://pypi.python.org/pypi/django-inoa-chronograph

The information below was retained from the source fork's original readme file.

---

======================
My Fork of Chronograph
======================
This fork includes these changes:
 - Adhoc jobs will be run by the cron job so the web ui doesn't block waiting on the job to finish
 - Minor change to the way the next run is calculated, now calculated from the previous next run value

Other changes made by the upstream project(https://github.com/okke-formsma/django-chronograph) are:
 - A `last_run_sucessful` flag on the Job model
 - A `success` flag on the Log model
 - A `subscribers` field on the Job model (ManyToMany with django.contrib.auth.models.User)
 - Whenever a job is run, all subscribers are e-mailed

Chronograph
===========

Chronograph is a simple application that allows you to control the frequency at
which a Django management command gets run.

To help explain how this is useful, let's consider a simple example.  Say you've
written an application that displays weather on your site.  You've written a
custom management command that you can execute which updates the weather::

    python manage.py update_weather

You would like to be able to run this command every hour so that you always have
the latest weather information displayed on your site.  Rather than having to
edit your crontab, ``cronograph`` allows you to simply add this functionality
via your admin.

Installing Chronograph
======================

Installing ``chronograph`` is pretty simple.  First add it into ``INSTALLED_APPS``
in your ``settings.py`` file.

After this run `syncdb``.  The only thing left to do is set up a periodic call to
run the jobs.

If you're using `cron`, the following example can be added to your `crontab`::

    * * * * * /path/to/your/project/manage.py cron

You're done!  Every minute ``cron`` will check to see if you have any pending jobs
and if you do they'll be run.  No more mucking about with your ``crontab``.

If you have a more complicated setup where ``manage.py`` might not work by default
see the section below on installing ``chronograph`` in a virtual environment.


Using a Virtual Environment
---------------------------

If you're using a virtual environment, setting up ``chronograph `` involves a bit more
work, but not by much.  Included is a script called ``chronograph.sh``.  Copy this file
to your project directory.

You should open up this script and modify the path to your virtual environment's ``activate``
script::

    $PROJECT_PATH"/../../../ve/bin/activate"

Make sure that this file is executable and then update your ``crontab`` to execute the
script.  Running ``crontab -e ``::

    * * * * * /path/to/your/project/chronograph.sh /path/to/your/project

Make sure that you pass ``/path/to/your/project`` to the script as the first argument.
This will ensure that ``cron`` will not have any problems finding your project directory.


Using Chronograph
=================

If you've completed the above steps, you're all done.  Now you can add some jobs to the system.
Remember, ``chronograph`` is designed to run any install ``django-admin`` management command and
it accommodates command-line arguments as well.

Cleaning Out Old Job Logs
-------------------------

If you'd like an easy way to delete old job logs, there is a management command that will do it for
you: ``cron_clean``.  You can use it like so::

  python manage.py cron_clean [weeks|days|hours|minutes] [integer]

So, if you want to remove all jobs that are older than a week, you can do the following::

  python manage.py cron_clean weeks 1

Since this is just a simple management command, you can also easily add it to ``chronograph``, via the
admin, so that it will clear out old logs automatically.
