"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import struct
from typing import Iterator, IO


class OggStream:
    """A simple Ogg stream parser for extracting Opus packets from Ogg container."""

    def __init__(self, stream: IO[bytes]) -> None:
        self.stream: IO[bytes] = stream
        self._buffer: bytearray = bytearray()
        self._packet_buffer: list = []  # Буфер для пакетов из текущей страницы

    def iter_packets(self) -> Iterator[bytes]:
        """Iterate over Opus packets in the Ogg stream."""
        while True:
            # Если есть пакеты в буфере, возвращаем их
            if self._packet_buffer:
                yield self._packet_buffer.pop(0)
                continue
            
            # Читаем новую страницу
            packets = self._read_page_packets()
            if not packets:
                break
            
            # Добавляем все пакеты в буфер, кроме первого (который возвращаем сразу)
            if len(packets) > 1:
                self._packet_buffer.extend(packets[1:])
            
            # Возвращаем первый пакет
            if packets:
                yield packets[0]

    def _read_page_packets(self) -> list:
        """Read all Opus packets from a single Ogg page."""
        # Read Ogg page header (27 bytes minimum)
        header = self._read_exact(27)
        if not header:
            return []

        # Check OggS magic
        if header[:4] != b'OggS':
            return []

        # Read number of segments (byte 26)
        num_segments = header[26]

        if num_segments == 0:
            # Empty page, skip to next
            return self._read_page_packets()

        # Read segment table
        segment_table = self._read_exact(num_segments)
        if not segment_table:
            return []

        # Calculate page data size
        page_size = sum(segment_table)

        if page_size == 0:
            # Empty page, skip to next
            return self._read_page_packets()

        # Read page data
        page_data = self._read_exact(page_size)
        if not page_data:
            return []

        # Skip Ogg identification header (first page with OpusHead)
        if page_data[:8] == b'OpusHead':
            return self._read_page_packets()

        # Extract packets from page
        # Segments are combined into packets (segment < 255 = end of packet)
        packets = []
        offset = 0
        packet_start = 0

        for seg_size in segment_table:
            offset += seg_size
            if seg_size < 255:
                # End of packet
                packet = bytes(page_data[packet_start:offset])
                if packet:
                    packets.append(packet)
                packet_start = offset

        # Handle last packet if any
        if packet_start < len(page_data):
            packet = bytes(page_data[packet_start:])
            if packet:
                packets.append(packet)

        return packets

    def _read_exact(self, size: int) -> bytes:
        """Read exactly `size` bytes from the stream."""
        data = self.stream.read(size)
        if len(data) < size:
            return b''
        return data

