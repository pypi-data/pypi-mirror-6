from __future__ import division, absolute_import, print_function

import StringIO
from struct import pack, unpack, calcsize
import ctypes

import numpy

import ooxcb
from ooxcb.protocol import (
    xproto,
)
from ooxcb.resource import get_internal

from operator import attrgetter
from ._x11_common import GeistXBase

xproto.mixin()


def _bit_c_to_byte(bit_cs):
    res = numpy.copy(bit_cs[0])
    for bit_c in bit_cs[1:]:
        res <<= 1
        res |= bit_c
    return res


def unpack_from_stream(fmt, stream, offset=0):
    if offset:
        stream.seek(offset, 1)
    s = stream.read(calcsize(fmt))
    return unpack(fmt, s)


class GetNumpyImageReply(ooxcb.Reply):
    def __init__(self, conn):
        ooxcb.Reply.__init__(self, conn)
        self.depth = None
        self.visual = None
        self.data = []

    def read(self, stream):
        self._address = stream.address
        _unpacked = unpack_from_stream("=xBxxxxxxIxxxxxxxxxxxxxxxxxxxx", stream)
        self.depth = _unpacked[0]
        self.visual = _unpacked[1]
        mem_array = ctypes.cast(
            stream._ptr,
            ctypes.POINTER(ctypes.c_ubyte*(self.length * 4))
        )
        self.data = numpy.frombuffer(mem_array.contents, dtype=numpy.uint8)

    def build(self, stream):
        count = 0
        stream.write(pack("=xBxxxxxxIxxxxxxxxxxxxxxxxxxxx", self.depth, self.visual))
        count += 32
        build_list(self.conn, stream, self.data, 'B')



class GeistXBackend(GeistXBase):
    def __init__(self, display=':0'):
        GeistXBase.__init__(self, display=display)

    @property
    def rect(self):
        geometry_getter = attrgetter('x', 'y', 'width', 'height')
        return geometry_getter(self._root.get_geometry().reply())

    def _get_image(self, format, x, y, width, height, plane_mask):
        drawable = get_internal(self._root)
        msg = pack("=xBxxIhhHHI", format, drawable, x, y, width, height, plane_mask)
        return self._conn.xproto.send_request(
            ooxcb.Request(self._conn, msg, 73, False, True),
            xproto.GetImageCookie(),
            GetNumpyImageReply
        )

    def capture(self):
        x, y, w, h = self.rect
        raw_img = self._get_image(
            xproto.ImageFormat.XYPixmap,
            x,
            y,
            w,
            h,
            0xFFFFFFFF
        ).reply().data
        im = numpy.unpackbits(
            raw_img.reshape(3, 8, h, w // 8, 1),
            4
        )[:, :, :, :, ::-1].reshape(3, 8, h, w)
        res = numpy.zeros((h, w, 3), numpy.uint8)
        res[:, :, 0] = _bit_c_to_byte(im[0])
        res[:, :, 1] = _bit_c_to_byte(im[1])
        res[:, :, 2] = _bit_c_to_byte(im[2])
        return res
