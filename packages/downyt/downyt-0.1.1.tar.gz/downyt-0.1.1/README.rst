=================================
downyt - Downloading from YouTube
=================================

**This project is deprecated!** This little tool was written to fill a void
that turned out it wasn't there. After I found *youtube-dl* I can only
recommend it for completeness and robustness:
http://rg3.github.io/youtube-dl

Introduction
------------

*downyt* is a simple commandline tool to make youtube videos available for
offline watching. It takes a youtube video URL or even just the video ID and
download it to your local storage. That's it! Nothing more, nothing less. It
might not change your life but it'll probably take the spinner out of your
underground commute...

Installation
------------

*downyt* is primarily implemented in Python 3.3. I'm planning on making it work
with Python 2.7 as well but it is currently untested and might now work. All
instructions assume that you have Python 3.3 setup.

It's simple, just get it from PyPI::

    pip install downyt

or install the latest version from github::

    pip install git+https://github.com/tangentlabs/django-fancypages.git

Usage
-----

You can download a video from YouTube by providing it's URL or video ID. An
example would be::

    downyt http://www.youtube.com/watch?v=1coLC-MUCJc

or::

    downyt '1coLC-MUCJc'

Both command will download the video into the current directory in the ``MP4``
format. Alternatively, you can specify the output format and directory like
this::

    downyt '1coLC-MUCJc' -t webm -o ~/Downloads

In addition, you can define the default download directory in a config file in
your home directory. Put the following in ``$HOME/.downyt/config.yml`` and it
will be used if no output directory is specified::

    output_dir: /home/username/Downloads

That's all there is to know.

License
-------

This project is released under the MIT License.


.. image:: https://d2weczhvl823v0.cloudfront.net/elbaschid/downyt/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

