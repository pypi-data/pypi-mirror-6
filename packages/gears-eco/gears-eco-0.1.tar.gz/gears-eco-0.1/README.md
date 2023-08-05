gears-eco
==================

Eco: Embedded CoffeeScript templates for Gears. 

Installation
------------

Install `gears-eco` with pip:

    $ pip install gears-eco


Requirements
------------

- [node.js](http://nodejs.org)
- [eco](https://github.com/sstephenson/eco)


Usage
-----

Add `gears_eco.EcoCompiler` to `environment`'s compilers registry:

    from gears_eco import EcoCompiler
    environment.compilers.register('.eco', EcoCompiler.as_handler())

If you use Gears in your Django project, add this code to your settings file:

    GEARS_COMPILERS = {
        '.eco': 'gears_eco.EcoCompiler',
    }
