.. _Emencia: http://www.emencia.com
.. _Gestus: https://github.com/sveetch/Gestus
.. _nap: https://github.com/kimmobrunfeldt/nap

**Gestus-client** is the REST client to retrieve and push data on a `Gestus`_ app.

Install
=======

Require
*******

* `nap`_ >= 1.0.0;
* pkginfo >= 1.2b1;
* argparse == 1.2.1;
* argcomplete == 0.8.0;
* argh == 0.24.1;

Usage
=====

The client can register a new website environment or update an allready existing environment.

During the register or update action, if the eggs directory is given it will be scanned to search for installed eggs, a list of finded eggs will be sended to the service.

Website environment's datas can be setted either from the command line arguments or from a config file. If a config file is used it will be used to fill the default datas to send and you can overrides them with the command line arguments. 

So if in the Config file you set the ``user`` option to ``ping`` and set this option to ``pong`` in the command line args, the used value will be ``pong``.

Config
******

The client can be used directly, but you should create a ``gestus.cfg`` file in your project to avoid to put arguments on the command line.

The file format is like ``*.INI`` file, here is a full example : ::

    [Gestus]
    user = your_username
    password = your_password
    host = service_url
    name = website_name
    url = website_url
    env = environment_name
    eggs = eggs_directory
    server = website_hostname

Available options are :

* **user**: the username to connect to the service;
* **password**: the password to connect to the service;
* **host**: the service's url (http/https);
* **name**: the website project name;
* **url**: the website project url (where it should be published);
* **env**: the environment kind name (``integration`` or ``production``);
* **eggs**: the path to eggs directory to scan;
* **server**: the website hostname;

There are all optionnal to register a new environment. But to update an allready existing environment you will need at least two additional options :

* website_id = the website's ID as it has been registered on the Gestus service;
* environment_id = the environment's ID as it has been registered on the Gestus service;

Config saving
-------------

Note that a Config file is automatically saved at the end of a register or update action, you can disable this using the ``passive`` argument : ::

    gestus --passive

Else the default behavior is to save a ``gestus.cfg`` file in the current directory, you can set another filename and path with ``config`` argument : ::

    gestus --config /home/foo/bar/my-gestus-config.cfg

Register a new website environment
==================================

This will only register a new environment, you can't update an allready existing website environment datas from this command.

    gestus register

If the website environment allready exists, the register command will get its datas and saving in a config file, then it will send again the egg list, this is the only thing that can be updated from this command.

If it does not exist, it will create it, then send the egg list and save returned datas in the config file.


