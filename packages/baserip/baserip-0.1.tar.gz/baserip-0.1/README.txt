Baserip
=======

Baserip is a tool for copying a single video title from a DVD whilst 
transcoding it. The purpose of this is to make the video available 
to devices you may have which do not have a DVD player.

Baserip was created because Acidrip is no longer being maintained 
and I found myself needing a DVD ripper. 
The design of Baserip is heavily influenced by Acidrip.

Baserip is, in fact, a simple front-end to Mplayer/Mencoder which is 
itself a front-end to some video encoding and decoding libraries.


INSTALLATION
============

Unpack the tarball and go into the top level directory. As root 
type::

    python3 setup.py install

The installation directory is usually:
/usr/local/lib/python3.x/dist-utils

Here you will find Baserip. Within Baserip you will find a "share" 
directory. In this there is a .desktop file and an icon. You can use 
these to manually add an entry to your desktop menu system.


REQUIREMENTS
============

In order to run Baserip you will need the following:

* Python3
* PyQt4
* pyudev
* mplayer/mencoder
* lsdvd
* lame



HOW TO USE BASERIP
==================

Please read the on-line documentation.

Baserip - What's Next
=====================

Dear Baserip users,

I don't know how many of you there are but I'm guessing there are
at least a few judging by the download statistics. With the release
of the 0.1 version Baserip has achieved the "does what I want" status.
However, I still feel compelled to add a few more things and I intend
to complete a 0.2 version. Currently I'm thinking that the 0.2 version
will have the following improvements:

# More audio codecs, I'll probably add AC3, AAC and vorbis.
# An edit box for setting the audio bitrate rather than relying on
  the profile to supply the bitrate.
# The ability for the user to select the container format of the
  encoded movie.
# An initial copy of the movie onto hard disk before encoding. I'll do
  this if this proves faster than reading off the DVD drive. It will
  probably be worth doing only for multi-pass encodes.
# Improve the installation so it's seemless with the desktop.

Baserip was only ever meant to be a simple "copier" of standard DVDs, it
certainly is not intended for bulk copying nor for the power user who
wants every option available. But I realise that even with the changes
mentioned above that Baserip has not achieved feature parity with
Acidrip nor do I know if anyone else has a burning need for a
particular feature so if you want to see a particular feature please
write to me at:

geoff (at) electron dot me dot uk

and I'll see if I can do it. Please remember that Baserip is a hobby
project of mine and even small changes can take some time. I can't
promise I can do everything but I will, at least, *consider* 
everything.

Best regards,
Geoff
