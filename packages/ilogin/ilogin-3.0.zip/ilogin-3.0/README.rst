======
iLogin
======
ilogin is a single sign-on script (SSO) like
*Google Application Specific Passwords* that allows you to generate passwords
for each online and offline service you're using.
Check online version at: http://iloginr.com

This way you will have different passwords for each service and you don't have
to remember them as you'll be able to obtain each every time you want
to login to your service.

The advantage of this script is that your passwords are not stored anywhere,
never.

.. contents::

Install
=======

    ::

        $: easy_install ilogin
        $: python setup.py install


How it works?
=============
First time when you'll run this script, you'll be asked for the new password in
order to initialize the database::

    $: ilogin
    New password: MYSECRETPASSWORD

Remember this password as it will be used to login to database and to generate
passwords for your services. There is no possible way to recover this password.
If you lose it you'll have to reset all your online services passwords.

Add a service that you want to use with this script::

    $: ilogin add
    Service: google
    Advanced settings [y/N]:n
    Service added

Get a login for your service::

    $: ilogin
    Service: google
    Password: MYSECRETPASSWORD
    suno owqi exar efjt

Now go to google.com > Change password and update your password with the one
provided by this script: suno owqi exar efjt

For now one, every time you want to login to google, run ilogin and
copy&paste generated password within gooogle.com Password field::

    $: ilogin
    Service: google
    Password: MYSECRETPASSWORD
    suno owqi exar efjt

You can also auto copy password to clipboard (UNIX and OS X)::

    $: ilogin copy
    Service: google
    Password: MYSECRETPASSWORD
    Password copied to clipboard

You can import and export settings from/to CSV files::

    $: ilogin import
    CSV Input File Path: example.csv
    Import complete

    $: ilogin export
    CSV Output File Path:output.csv
    Export complete

See more options::

    $: ilogin help
    ilogin version 3.0

    Usage: ilogin <cmd>

    For older versions use ilogin2 <cmd> OR ilogin1 <cmd>

        cmd:
          - login   Get login password for service (default)

          - user    Get login username for service

          - add     Add service to ilogin

          - field   Add new field

          - import  Import services from CSV file. CSV file headers (advanced options are optional):

                    "Service", ["Password length", "User Name", "Use Numbers", "Use Special Charaters", "Use Capital Letters", "Version"]
                    "example.com", "16", "user@example.com", "n", "y", "false", "2"
                    "foo.bar", "", "", "", "", "", ""
                    "bar.foo", "9", "", "0", "1", "true", "7"

          - export  Export services to CSV file.
                    !! This will not export your passwords !!

          - passwd  Change ilogin password.
                    !! ALL YOUR SERVICES PASSWORDS WILL CHANGE AND YOU'LL NEED TO MANUALLY CHANGE THEM ON SERVER SIDE !!

          - copy    Get login password for service and copy it to clipboard
                      - UNIX:    xsel or xclip required
                      - OS X:    pbcopy required
                      - Windows: Not supported yet

