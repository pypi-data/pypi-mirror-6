trebuchet
=========

[![Build Status](https://travis-ci.org/ops-hero/trebuchet.png?branch=master)](https://travis-ci.org/ops-hero/trebuchet)

	trebuchet |ˌtrebyəˈ sh et|
	noun
	a machine used in medieval siege warfare for hurling large stones or other missiles.
	ORIGIN Middle English : from Old French, from trebucher ‘overthrow.’


## Goal ##
Trebuchet is a packaging script that takes a configuration file (known as a `missile`) and build one or several Debian packages out of it. It can be used for application packages but also configuration packages.


## Concepts ##
Application packages are country agnostic and are composed of the source code of the project, the environment to run it (virtualenv...) and different upstart scripts that run the application in various ways (uwsgi, celery...). For each application, the packages are dependent among each others and restart each other during installation if necessary.

Configuration packages are specific to a product (several variation, branding for the same code) and an environment (live, staging...). It include the settings for all the applications needed to run the stack for a speficic product configuration. It also include NGINX configuration as it is specific to both. Those packages are meant to be installed on all the servers of the cluster for the product/environment. The application packages (the upstart ones) running on a server will then make use of those settings.

A YAML file needs to be specified within the repository of the application/settings you want to build. Most of the time `.missile.yaml`, but it could be anything.

Trebuchet do not do git manipulation; the working copy needs to be ready before.

Trebuchet do not calculate versioning; the version for the packages will have to be provided and be processed beforehand.

Trebuchet do not install nor deploy; it just build up packages.


## Installation ##
This is a fully fleshed python package, so very easy:

    $ pip install le-trebuchet

Or:

    $ git clone git@github.com:ops-hero/trebuchet.git -o upstream
    $ cd trebuchet
    $ python setup.py develop

The commmand `trebuchet` is now available in your path.

## Usage ##
The command include a proper documentation by itself, just run `trebuchet --help`

The main command is to build packages, just pass it the path to a `missile` file within a working copy directory:

    $ trebuchet build /path/to/working/copy/repo/.missile.yaml

> It also works with relative path: `trebuchet build .missile.yaml`.

Several options can be specified:

* The output folder for the Debian packages by using the option `--output DIR_PATH`. This can be used to organize the packages. Default behavior is to create them in the current directory.
* The build folder where the packages are prepared before the packaging can be setup via `--build DIR_PATH`. Default behavior is to create a temporary folder.
* The packages description can contain an extended description by using the option `--extended-description MESSSAGE`. For example, it could contain the changelog or the commits that will be part of the packages.

For example:

    $ trebuchet build example/application/.missile.yml --output /tmp --arch amd64 --build /tmp/trebuchet/build/ --extra-description "Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Donec mi velit, facilisis ac ullamcorper ac, tristique et odio. 
    Ut consectetur magna"
    ...
    [localhost] local: dpkg-deb --build /tmp/trebuchet/build/secret_sauce /var/trebuchet/debs/dh-secret-sauce-1.0.0-all.deb
    dpkg-deb: building package `dh-secret-sauce' in `/var/trebuchet/debs/dh-secret-sauce-1.0.0-all.deb'.
    ['dh-secret-sauce-web-1-upstart-1.0.0-all.deb', 'dh-secret-sauce-web-2-upstart-1.0.0-all.deb', 'dh-secret-sauce-web-upstart-1.0.0-all.deb', 'dh-secret-sauce-lib-1.0.0-amd64.deb', 'dh-secret-sauce-1.0.0-all.deb']
    $
    $ dpkg -I /var/trebuchet/debs/dh-secret-sauce-1.0.0-all.deb 
     new debian package, version 2.0.
     size 2368 bytes: control archive= 754 bytes.
         316 bytes,    10 lines   *  control              
          75 bytes,    13 lines   *  postinst             #!/bin/bash
         491 bytes,    28 lines   *  preinst              #!/bin/bash
         170 bytes,    12 lines   *  prerm                #!/bin/bash
     Package: dh-secret-sauce
     Version: 1.0.0
     Architecture: all
     Depends: dh-secret-sauce-lib (>= 1.0.0),  python (>= 2.7.3)
     Maintainer: Arnaud Seilles <arnaud.seilles@gmail.com>
     Description: Package dh-secret-sauce (version 1.0.0) built on the 2013-06-29 14:16:43.803091
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
      Donec mi velit, facilisis ac ullamcorper ac, tristique et odio. 
      Ut consectetur magna
    $


## Testing ##
There is a command to also check the syntax of the config file and print out the lists of packages that will be built:

    $ trebuchet lint /path/to/working/copy/repo/.missile.yaml



## Update ##
To update the package, do as follow:
    
    $ cd trebuchet
    $ git fetch upstream
    $ git pull --rebase origin master
    $ python setup.py develop


## TODO ##
* Add documentation for (extra file in configuration, cookbook of best  usage...)
* Add more configuration scheme, tests and documentation.
* To work locally as well (setup the folder in a workable way without packaging/installing).
* Handle dependencies for building and installing the package.
* Refactor to remove all this amateur stuff (customfiles, configuration...).