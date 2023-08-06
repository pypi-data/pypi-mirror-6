pyramid_maintenance
===================

:author: Benoît Pineau <beny@sickless.net>
:date: 2014-02-12


What is it
----------

pyramid_maintenance is a pyramid tween.

This tween gives you the possibility to put an application in maintenance mode (rendering only one specific template for all routes), but let a 'normal' access to your application for users who have specific permission(s).


How to install it
-----------------

::
    pip install pyramid_maintenance


How to enable it
----------------

If you want to enable pyramid_maintenance tween in your pyramid app, you have to add in your .ini file::

    pyramid.tweens = pyramid_maintenance.tween_maintenance


And define the following settings::

    # List of roles (separeted by commas). The pyramid app isn't
    # in maintenance mode for people who have one of these roles.
    pyramid_maintenance.roles = role1, role2
    # Relative path from defined template location directories.
    pyramid_maintenance.template = template.mako
