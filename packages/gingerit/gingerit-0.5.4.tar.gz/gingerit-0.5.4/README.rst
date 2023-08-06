gingerit
========

.. image:: https://pypip.in/v/gingerit/badge.png
    :target: https://pypi.python.org/pypi/gingerit

.. image:: https://landscape.io/github/Azd325/gingerit/master/landscape.png
    :target: https://landscape.io/github/Azd325/gingerit/master
    :alt: Code Health


.. image:: https://coveralls.io/repos/Azd325/gingerit/badge.png?branch=master
    :target: https://coveralls.io/r/Azd325/gingerit?branch=master

.. image:: https://travis-ci.org/Azd325/gingerit.png?branch=master
    :target: https://travis-ci.org/Azd325/gingerit


Python wrapper for correcting spelling and grammar mistakes based on the context of complete sentences.

Installation:
-------------

::

    pip install gingerit

Usage:
------

::

    from gingerit.gingerit import GingerIt

    text = 'The smelt of fliwers bring back memories.'

    parser = GingerIt()
    parser.parse(text)

TODO:
-----

 - More tests
 - Commandline Tool

Contributing:
-------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

Thanks
------

Thank you for [Ginger Proofreader](http://www.gingersoftware.com/) for such awesome service. Hope they will keep it free :)

Thanks to @subosito for this inspriration https://github.com/subosito/gingerice (Ruby Gem)
