# -*- coding: utf-8 -*-

# Copyright 2006 Joe Wreschnig
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# Modified for Python 3 by Ben Ockmore <ben.sput@gmail.com>

"""True Audio audio stream information and tags.

True Audio is a lossless format designed for real-time encoding and
decoding. This module is based on the documentation at
http://www.true-audio.com/TTA_Lossless_Audio_Codec\_-_Format_Description

True Audio files use ID3 tags.
"""

__all__ = ["TrueAudio", "Open", "delete", "EasyTrueAudio"]

from mutagenx.id3 import ID3FileType, delete
from mutagenx._util import cdata


class error(RuntimeError):
    pass


class TrueAudioHeaderError(error, IOError):
    pass


class TrueAudioInfo(object):
    """True Audio stream information.

    Attributes:

    * length - audio length, in seconds
    * sample_rate - audio sample rate, in Hz
    """

    def __init__(self, fileobj, offset):
        fileobj.seek(offset or 0)
        header = fileobj.read(18)
        if len(header) != 18 or not header.startswith(b"TTA"):
            raise TrueAudioHeaderError("TTA header not found")
        self.sample_rate = cdata.int_le(header[10:14])
        samples = cdata.uint_le(header[14:18])
        self.length = samples / self.sample_rate

    def pprint(self):
        return "True Audio, %.2f seconds, %d Hz." % (
            self.length, self.sample_rate)


class TrueAudio(ID3FileType):
    """A True Audio file.

    :ivar info: :class:`TrueAudioInfo`
    :ivar tags: :class:`ID3 <mutagenx.id3.ID3>`
    """

    _Info = TrueAudioInfo
    _mimes = ["audio/x-tta"]

    @staticmethod
    def score(filename, fileobj, header):
        return (header.startswith(b"ID3") + header.startswith(b"TTA") +
                filename.lower().endswith(".tta") * 2)


Open = TrueAudio


class EasyTrueAudio(TrueAudio):
    """Like MP3, but uses EasyID3 for tags.

    :ivar info: :class:`TrueAudioInfo`
    :ivar tags: :class:`EasyID3 <mutagenx.easyid3.EasyID3>`
    """

    from mutagenx.easyid3 import EasyID3 as ID3
    ID3 = ID3
