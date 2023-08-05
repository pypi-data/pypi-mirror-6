General Information
===================

This program is a tool to translate and create automatically an srt file to be used as a subtitle
for your video, to be auto reproduce in your language.

Supported on the google api for google-translate and based on the parser library pysrt with this
program you will be able to translate in a matter of seconds your subtitles from the origin
language for your videos.

The flow of work is something like this:

1. Download or create your subtitle for your videos in `srt format`_ in your language.
2. Run this script telling the origin and destiny.
3. Gualá your subtitle is in other language.

.. note::
    
    This translations are not perfect due to the normal leak of quality of google translate,
    remember install a `program`_ to post-edit your subtitles easily. and this is a list of `players`_
    which support natively this subs. 

Dependencies:
-------------

    - Generate your `google API key`_, if you don't know what it is, I recomend read the `official help`_.
    - pysrt_. 
    - google-api-python-client_.

Installing:
-----------

This is an script designed to run directly from the source code, only install
the dependencies using the installer of your preference and run the script, you can install it
quickly with pip.::

    $sudo pip install pysrttranslator


Or you can install from the sources::

    $ Download the source.
    $ tar zxfv source.tar.gz
    $ cd source
    $ sudo setup.py install

Configuring.
------------

You need create a config file with at least the Google API key.::

    $touch local.cfg
    $nano local.cfg

Paste this test file on your local.cfg file, you can read the config options to know how set global
and local variables in this case the file will be read from the location where you are.

.. code:: ini

    [__main__]
    input_lang = en #origin lang of your subtitle
    output_lang = es #destiny lang of your subtitles
    log_file = pysrttranslator.log #where your log will be
    google_api_key = INSERTHEREYOURKEY #your api key generated in google develper console

Usage.
------

Some examples about how to use it.

1.- Translating a file and saving it in the same folder from english to spanish.::

    $pysrttranslator file.srt -i en -o es

With this command you will obtain a file called `file.es.srt` just beside the file.srt file.

2.- Translating a file and saving the result in other folder from english to spanish.::

    $pysrttranslator file.srt /path/destiny/fileoutput.srt -i en -o es

3.- Run this command to get all options.::

    $pysrttranslator --help

Options availables.
'''''''''''''''''''

This is what you will get if you run the --help option.

.. _google API key: https://cloud.google.com/console#/project
.. _official help: https://developers.google.com/console/help/new/#usingkeys
.. _google-api-python-client: https://code.google.com/p/google-api-python-client/source/browse/README 
.. _pysrt: https://pypi.python.org/pypi/pysrt
.. _srt format: http://en.wikipedia.org/wiki/.srt#SubRip_text_file_format
.. _players: http://ale5000.altervista.org/subtitles.htm
.. _program: http://home.gna.org/subtitleeditor/
