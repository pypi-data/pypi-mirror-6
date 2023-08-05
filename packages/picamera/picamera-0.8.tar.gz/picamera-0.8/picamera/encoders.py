# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# Python camera library for the Rasperry-Pi camera module
# Copyright (c) 2013, Dave Hughes <dave@waveform.org.uk>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import (
    unicode_literals,
    print_function,
    division,
    absolute_import,
    )

# Make Py2's str equivalent to Py3's
str = type('')

import io
import datetime
import threading
import warnings
import ctypes as ct

import picamera.mmal as mmal
from picamera.exc import (
    mmal_check,
    PiCameraWarning,
    PiCameraError,
    PiCameraValueError,
    PiCameraRuntimeError,
    )


__all__ = [
    'PiEncoder',
    'PiVideoEncoder',
    'PiImageEncoder',
    'PiRawImageEncoder',
    'PiOneImageEncoder',
    'PiMultiImageEncoder',
    ]


def _encoder_callback(port, buf):
    encoder = ct.cast(port[0].userdata, ct.POINTER(ct.py_object))[0]
    encoder._callback(port, buf)
_encoder_callback = mmal.MMAL_PORT_BH_CB_T(_encoder_callback)


class PiEncoder(object):
    """
    Abstract base implemetation of an MMAL encoder for use by PiCamera
    """

    encoder_type = None

    def __init__(self, parent, port, format, **options):
        self.parent = parent
        self.encoder = None
        self.camera_port = port
        self.input_port = None
        self.output_port = None
        self.pool = None
        self.connection = None
        self.opened = False
        self.output = None
        self.lock = threading.Lock() # protects access to self.output
        self.exception = None
        self.event = threading.Event()
        self.stopped = True
        try:
            if parent.closed:
                raise PiCameraRuntimeError("Camera is closed")
            self._create_encoder(format, **options)
            self._create_pool()
            self._create_connection()
        except:
            self.close()
            raise

    def _create_encoder(self, format, **options):
        """
        Creates and configures the encoder itself
        """
        assert not self.encoder
        self.encoder = ct.POINTER(mmal.MMAL_COMPONENT_T)()
        mmal_check(
            mmal.mmal_component_create(self.encoder_type, self.encoder),
            prefix="Failed to create encoder component")
        if not self.encoder[0].input_num:
            raise PiCameraError("No input ports on encoder component")
        if not self.encoder[0].output_num:
            raise PiCameraError("No output ports on encoder component")
        # Ensure output format is the same as the input
        self.output_port = self.encoder[0].output[0]
        self.input_port = self.encoder[0].input[0]
        mmal.mmal_format_copy(
            self.output_port[0].format, self.input_port[0].format)
        # Set buffer size and number to appropriate values
        self.output_port[0].buffer_size = max(
            self.output_port[0].buffer_size_recommended,
            self.output_port[0].buffer_size_min)
        self.output_port[0].buffer_num = max(
            self.output_port[0].buffer_num_recommended,
            self.output_port[0].buffer_num_min)

    def _create_pool(self):
        """
        Allocates a pool of buffers for the encoder
        """
        assert not self.pool
        self.pool = mmal.mmal_port_pool_create(
            self.output_port,
            self.output_port[0].buffer_num,
            self.output_port[0].buffer_size)
        if not self.pool:
            raise PiCameraError(
                "Failed to create buffer header pool for encoder component")

    def _create_connection(self):
        """
        Connects the camera to the encoder object
        """
        assert not self.connection
        self.connection = self.parent._connect_ports(
            self.camera_port, self.input_port)

    def _callback(self, port, buf):
        """
        The encoder's main callback function
        """
        stop = False
        try:
            try:
                stop = self._callback_write(buf) and not self.stopped
            finally:
                self._callback_recycle(port, buf)
        except Exception as e:
            stop = True
            self.exception = e
        if stop:
            self.stopped = True
            self.event.set()

    def _callback_write(self, buf):
        """
        Performs output writing on behalf of the encoder callback function;
        return value determines whether writing has completed.
        """
        if buf[0].length:
            mmal_check(
                mmal.mmal_buffer_header_mem_lock(buf),
                prefix="Unable to lock buffer header memory")
            try:
                with self.lock:
                    if self.output:
                        written = self.output.write(
                           ct.string_at(buf[0].data, buf[0].length))
                        # Ignore None return value; most Python 2 streams have
                        # no return value for write()
                        if (written is not None) and (written != buf[0].length):
                            raise PiCameraError(
                                "Unable to write buffer to file - aborting")
            finally:
                mmal.mmal_buffer_header_mem_unlock(buf)
        return False

    def _callback_recycle(self, port, buf):
        """
        Recycles the buffer on behalf of the encoder callback function
        """
        mmal.mmal_buffer_header_release(buf)
        if port[0].is_enabled:
            new_buf = mmal.mmal_queue_get(self.pool[0].queue)
            if not new_buf:
                raise PiCameraError(
                    "Unable to get a buffer to return to the encoder port")
            mmal_check(
                mmal.mmal_port_send_buffer(port, new_buf),
                prefix="Unable to return a buffer to the encoder port")

    def _open_output(self, output):
        """
        Opens the specified output object, if necessary and tracks whether
        we were the one to open it.
        """
        with self.lock:
            self.opened = isinstance(output, (bytes, str))
            if self.opened:
                # Open files in binary mode with a *big* (1Mb) buffer
                self.output = io.open(output, 'wb', buffering=1048576)
            else:
                self.output = output

    def _close_output(self):
        """
        Closes the output object, if necessary or simply flushes it if we
        didn't open it and it has a flush method.
        """
        with self.lock:
            if self.output:
                if self.opened:
                    self.output.close()
                elif hasattr(self.output, 'flush'):
                    self.output.flush()
                self.output = None
                self.opened = False

    def start(self, output):
        """
        Starts the encoder object writing to the specified output
        """
        self.event.clear()
        self.stopped = False
        self.exception = None
        self._open_output(output)
        self.output_port[0].userdata = ct.cast(
            ct.pointer(ct.py_object(self)),
            ct.c_void_p)
        mmal_check(
            mmal.mmal_port_enable(self.output_port, _encoder_callback),
            prefix="Failed to enable encoder output port")

        for q in range(mmal.mmal_queue_length(self.pool[0].queue)):
            buf = mmal.mmal_queue_get(self.pool[0].queue)
            if not buf:
                raise PiCameraRuntimeError(
                    "Unable to get a required buffer from pool queue")
            mmal_check(
                mmal.mmal_port_send_buffer(self.output_port, buf),
                prefix="Unable to send a buffer to encoder output port")

    def wait(self, timeout=None):
        """
        Waits for the encoder to finish (successfully or otherwise)
        """
        result = self.event.wait(timeout)
        if result:
            mmal_check(
                mmal.mmal_port_disable(self.output_port),
                prefix="Failed to disable encoder output port")
            self._close_output()
            # Check whether the callback set an exception
            if self.exception:
                raise self.exception
        return result

    def stop(self):
        """
        Stops the encoder, regardless of whether it's finished
        """
        if self.encoder and self.output_port[0].is_enabled:
            mmal_check(
                mmal.mmal_port_disable(self.output_port),
                prefix="Failed to disable encoder output port")
        self.stopped = True
        self.event.set()
        self._close_output()

    def close(self):
        """
        Finalizes the encoder and deallocates all structures
        """
        self.stop()
        if self.connection:
            mmal.mmal_connection_destroy(self.connection)
            self.connection = None
        if self.pool:
            mmal.mmal_port_pool_destroy(self.output_port, self.pool)
            self.pool = None
        if self.encoder:
            if self.encoder[0].is_enabled:
                mmal.mmal_component_disable(self.encoder)
            mmal.mmal_component_destroy(self.encoder)
            self.encoder = None
            self.output_port = None
            self.input_port = None


class PiVideoEncoder(PiEncoder):
    encoder_type = mmal.MMAL_COMPONENT_DEFAULT_VIDEO_ENCODER

    def __init__(self, parent, port, format, **options):
        super(PiVideoEncoder, self).__init__(parent, port, format, **options)
        self._next_output = []

    def _create_encoder(
            self, format, bitrate=17000000, intra_period=0, profile='high',
            quantization=0, inline_headers=True, **options):
        super(PiVideoEncoder, self)._create_encoder(format, **options)

        try:
            self.output_port[0].format[0].encoding = {
                'h264': mmal.MMAL_ENCODING_H264,
                }[format]
        except KeyError:
            raise PiCameraValueError('Unrecognized format %s' % format)

        if not (0 <= bitrate <= 25000000):
            raise PiCameraValueError('bitrate must be between 0 (VBR) and 25Mbps')
        if quantization and bitrate:
            warnings.warn('Setting bitrate to 0 as quantization is non-zero', PiCameraWarning)
            bitrate = 0
        self.output_port[0].format[0].bitrate = bitrate
        mmal_check(
            mmal.mmal_port_format_commit(self.output_port),
            prefix="Unable to set format on encoder output port")

        if intra_period:
            mp = mmal.MMAL_PARAMETER_UINT32_T(
                    mmal.MMAL_PARAMETER_HEADER_T(
                        mmal.MMAL_PARAMETER_INTRAPERIOD,
                        ct.sizeof(mmal.MMAL_PARAMETER_UINT32_T),
                        ),
                    intra_period
                    )
            mmal_check(
                mmal.mmal_port_parameter_set(self.output_port, mp.hdr),
                prefix="Unable to set encoder intra_period")

        if quantization:
            mp = mmal.MMAL_PARAMETER_UINT32_T(
                    mmal.MMAL_PARAMETER_HEADER_T(
                        mmal.MMAL_PARAMETER_VIDEO_ENCODE_INITIAL_QUANT,
                        ct.sizeof(mmal.MMAL_PARAMETER_UINT32_T),
                        ),
                    quantization
                    )
            mmal_check(
                mmal.mmal_port_parameter_set(self.output_port, mp.hdr),
                prefix="Unable to set quantization")
            mp = mmal.MMAL_PARAMETER_UINT32_T(
                    mmal.MMAL_PARAMETER_HEADER_T(
                        mmal.MMAL_PARAMETER_VIDEO_ENCODE_QP_P,
                        ct.sizeof(mmal.MMAL_PARAMETER_UINT32_T),
                        ),
                    quantization + 6,
                    )
            mmal_check(
                mmal.mmal_port_parameter_set(self.output_port, mp.hdr),
                prefix="Unable to set quantization")

        mp = mmal.MMAL_PARAMETER_VIDEO_PROFILE_T(
                mmal.MMAL_PARAMETER_HEADER_T(
                    mmal.MMAL_PARAMETER_PROFILE,
                    ct.sizeof(mmal.MMAL_PARAMETER_VIDEO_PROFILE_T),
                    ),
                )
        try:
            mp.profile[0].profile = {
                'baseline':    mmal.MMAL_VIDEO_PROFILE_H264_BASELINE,
                'main':        mmal.MMAL_VIDEO_PROFILE_H264_MAIN,
                'high':        mmal.MMAL_VIDEO_PROFILE_H264_HIGH,
                'constrained': mmal.MMAL_VIDEO_PROFILE_H264_CONSTRAINED_BASELINE,
            }[profile]
        except KeyError:
            raise PiCameraValueError("Invalid H.264 profile %s" % profile)
        mp.profile[0].level = mmal.MMAL_VIDEO_LEVEL_H264_4
        mmal_check(
            mmal.mmal_port_parameter_set(self.output_port, mp.hdr),
            prefix="Unable to set encoder H.264 profile")

        mmal_check(
            mmal.mmal_port_parameter_set_boolean(
                self.input_port,
                mmal.MMAL_PARAMETER_VIDEO_IMMUTABLE_INPUT,
                1),
            prefix="Unable to set immutable flag on encoder input port")

        mmal_check(
            mmal.mmal_port_parameter_set_boolean(
                self.output_port,
                mmal.MMAL_PARAMETER_VIDEO_ENCODE_INLINE_HEADER,
                int(inline_headers)),
            prefix="Unable to set inline_headers")

        if not (bitrate and inline_headers):
            # If inline_headers is disabled, or VBR encoding is configured,
            # disable the split function
            self._next_output = None

        mmal_check(
            mmal.mmal_component_enable(self.encoder),
            prefix="Unable to enable video encoder component")

    def split(self, output):
        with self.lock:
            if self._next_output is None:
                raise PiCameraRuntimeError(
                    'Cannot use split_recording without inline_headers and CBR')
            self._next_output.append(output)
        # XXX Instead of a 10-second timeout, how about a warning here (which
        # can be converted to an error and captured by the test suite?)
        if not self.event.wait(10):
            raise PiCameraRuntimeError('Timed out waiting for an SPS header')
        self.event.clear()

    def _callback_write(self, buf):
        if buf[0].flags & mmal.MMAL_BUFFER_HEADER_FLAG_CONFIG:
            new_output = None
            with self.lock:
                if self._next_output:
                    new_output = self._next_output.pop(0)
            if new_output:
                self._close_output()
                self._open_output(new_output)
                self.event.set()
        super(PiVideoEncoder, self)._callback_write(buf)


class PiImageEncoder(PiEncoder):
    encoder_type = mmal.MMAL_COMPONENT_DEFAULT_IMAGE_ENCODER

    def _create_encoder(
            self, format, quality=85, thumbnail=(64, 48, 35), **options):
        super(PiImageEncoder, self)._create_encoder(format, **options)

        try:
            self.output_port[0].format[0].encoding = {
                'jpeg': mmal.MMAL_ENCODING_JPEG,
                'png':  mmal.MMAL_ENCODING_PNG,
                'gif':  mmal.MMAL_ENCODING_GIF,
                'bmp':  mmal.MMAL_ENCODING_BMP,
                }[format]
        except KeyError:
            raise PiCameraValueError("Unrecognized format %s" % format)
        mmal_check(
            mmal.mmal_port_format_commit(self.output_port),
            prefix="Unable to set format on encoder output port")

        if format == 'jpeg':
            mmal_check(
                mmal.mmal_port_parameter_set_uint32(
                    self.output_port,
                    mmal.MMAL_PARAMETER_JPEG_Q_FACTOR,
                    quality),
                prefix="Failed to set JPEG quality")

            if thumbnail is None:
                mp = mmal.MMAL_PARAMETER_THUMBNAIL_CONFIG_T(
                    mmal.MMAL_PARAMETER_HEADER_T(
                        mmal.MMAL_PARAMETER_THUMBNAIL_CONFIGURATION,
                        ct.sizeof(mmal.MMAL_PARAMETER_THUMBNAIL_CONFIG_T)
                        ),
                    0, 0, 0, 0)
            else:
                mp = mmal.MMAL_PARAMETER_THUMBNAIL_CONFIG_T(
                    mmal.MMAL_PARAMETER_HEADER_T(
                        mmal.MMAL_PARAMETER_THUMBNAIL_CONFIGURATION,
                        ct.sizeof(mmal.MMAL_PARAMETER_THUMBNAIL_CONFIG_T)
                        ),
                    1, *thumbnail)
            mmal_check(
                mmal.mmal_port_parameter_set(self.encoder[0].control, mp.hdr),
                prefix="Failed to set thumbnail configuration")

        mmal_check(
            mmal.mmal_component_enable(self.encoder),
            prefix="Unable to enable encoder component")


class PiOneImageEncoder(PiImageEncoder):
    def _callback_write(self, buf):
        return (
            super(PiOneImageEncoder, self)._callback_write(buf)
            ) or bool(
            buf[0].flags & (
                mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END |
                mmal.MMAL_BUFFER_HEADER_FLAG_TRANSMISSION_FAILED)
            )


class PiRawOneImageEncoder(PiOneImageEncoder):
    def _create_encoder(self, format, **options):
        # Overridden to skip creating an encoder. Instead we simply use the
        # camera's still port as the output port
        self.input_port = None
        self.output_port = self.camera_port

    def _create_connection(self):
        # Overridden to skip creating a connection; there's no encoder so
        # there's no connection
        pass


class PiCookedOneImageEncoder(PiOneImageEncoder):
    exif_encoding = 'ascii'

    def _add_exif_tag(self, tag, value):
        # Format the tag and value into an appropriate bytes string, encoded
        # with the Exif encoding (ASCII)
        if isinstance(tag, str):
            tag = tag.encode(self.exif_encoding)
        if isinstance(value, str):
            value = value.encode(self.exif_encoding)
        elif isinstance(value, datetime.datetime):
            value = value.strftime('%Y:%m:%d %H:%M:%S').encode(self.exif_encoding)
        # MMAL_PARAMETER_EXIF_T is a variable sized structure, hence all the
        # mucking about with string buffers here...
        buf = ct.create_string_buffer(
            ct.sizeof(mmal.MMAL_PARAMETER_EXIF_T) + len(tag) + len(value) + 1)
        mp = ct.cast(buf, ct.POINTER(mmal.MMAL_PARAMETER_EXIF_T))
        mp[0].hdr.id = mmal.MMAL_PARAMETER_EXIF
        mp[0].hdr.size = len(buf)
        if (b'=' in tag or b'\x00' in value):
            data = tag + value
            mp[0].keylen = len(tag)
            mp[0].value_offset = len(tag)
            mp[0].valuelen = len(value)
        else:
            data = tag + b'=' + value
        ct.memmove(mp[0].data, data, len(data))
        mmal_check(
            mmal.mmal_port_parameter_set(self.output_port, mp[0].hdr),
            prefix="Failed to set Exif tag %s" % tag)

    def start(self, output):
        timestamp = datetime.datetime.now()
        timestamp_tags = (
            'EXIF.DateTimeDigitized',
            'EXIF.DateTimeOriginal',
            'IFD0.DateTime')
        # Timestamp tags are always included with the value calculated
        # above, but the user may choose to override the value in the
        # exif_tags mapping
        for tag in timestamp_tags:
            self._add_exif_tag(tag, self.parent.exif_tags.get(tag, timestamp))
        # All other tags are just copied in verbatim
        for tag, value in self.parent.exif_tags.items():
            if not tag in timestamp_tags:
                self._add_exif_tag(tag, value)
        super(PiCookedOneImageEncoder, self).start(output)


class PiMultiImageEncoder(PiImageEncoder):
    def _open_output(self, outputs):
        self._output_iter = iter(outputs)
        self._next_output()

    def _next_output(self):
        if self.output:
            self._close_output()
        super(PiMultiImageEncoder, self)._open_output(next(self._output_iter))

    def _callback_write(self, buf):
        try:
            if (
                super(PiMultiImageEncoder, self)._callback_write(buf)
                ) or bool(
                buf[0].flags & (
                    mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END |
                    mmal.MMAL_BUFFER_HEADER_FLAG_TRANSMISSION_FAILED)
                ):
                self._next_output()
            return False
        except StopIteration:
            return True


class PiRawMultiImageEncoder(PiMultiImageEncoder):
    def _create_encoder(self, format, **options):
        # Overridden to skip creating an encoder. Instead we simply use the
        # camera's still port as the output port
        self.input_port = None
        self.output_port = self.camera_port

    def _create_connection(self):
        # Overridden to skip creating a connection; there's no encoder so
        # there's no connection
        pass


class PiCookedMultiImageEncoder(PiMultiImageEncoder):
    pass

