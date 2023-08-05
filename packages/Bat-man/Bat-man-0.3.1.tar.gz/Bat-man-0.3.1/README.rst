Bat-man
=======

Bat-man is a batch downloader and converter of YouTube videos.

Requirements
============
* Python 3
* Gtk3 for Python
* ffmpeg
* LAME

Running stand-alone
===================

Extract the .zip file, and in the destination folder, run:

`$ python -m batman.gtk_batch_downloader`

Installing
==========

To install this program, run, as root:

`# python setup.py install`

After install, you can run the program by typing:

`$ bat-man`

PIP Installing
==============

You can also install this program using PIP:

`# pip install Bat-man`

How to use
==========

1. Set the destination of the MP3 files with the button "Set destination", in bottom-left.
2. Add new videos with File -> Insert new videos, or right-click in the tree view and select Paste, for videos in the clipboard.
3. The download will start automatically.
4. Drink a coffee.
5. If yours internet connection is like mine, drink more coffee.
6. Go see your doctor.
7. Done!

To-do list(it should even be here?)
===================================
1. Convert to more formats(Base implemented, has support for Vorbis, MP3, AAC, FLAC, Theora and LibX264 - the last two as video codecs)
2. Try to use an API for converting videos, instead of commandline
3. Smooth exit for threads(Partially implemented.)

