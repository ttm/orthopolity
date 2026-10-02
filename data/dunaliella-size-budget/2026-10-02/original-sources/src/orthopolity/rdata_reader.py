"""Read R workspace files (RDX2/RDX3, XDR serialization) without R.

Numeric and logical vectors stay undecoded byte ranges until `decode()` is
called, so a caller can inspect design columns (factors, identifiers, names)
without converting any outcome value. Closures, environments and similar
language objects are parsed structurally but never evaluated. Byte-code
objects are rejected rather than guessed.
"""
from __future__ import annotations

import bz2
import gzip
import lzma
import struct
from dataclasses import dataclass, field

import numpy as np

NILVALUE, REF, GLOBALENV, UNBOUND, MISSINGARG, BASENAMESPACE = 254, 255, 253, 252, 251, 247
NAMESPACE, PACKAGE, PERSIST, EMPTYENV, BASEENV, ALTREP = 249, 250, 248, 242, 241, 238
SYM, LIST, CLO, ENV, PROM, LANG, SPECIAL, BUILTIN, CHAR = 1, 2, 3, 4, 5, 6, 7, 8, 9
LGL, INT, REAL, CPLX, STR, DOT, VEC, EXPR, BCODE, EXTPTR, WEAKREF, RAW, S4 = (
    10, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25)
NA_INTEGER = -2**31


@dataclass
class RVector:
    """An R atomic vector whose numeric payload is decoded only on request."""
    kind: int
    length: int
    payload: object
    attributes: dict = field(default_factory=dict)

    def decode(self):
        if self.kind == STR:
            return list(self.payload)
        if self.kind == RAW:
            return bytes(self.payload)
        if self.kind == REAL:
            return np.frombuffer(self.payload, dtype='>f8').astype(float)
        if self.kind == CPLX:
            parts = np.frombuffer(self.payload, dtype='>f8').astype(float)
            return parts[0::2]+1j*parts[1::2]
        values = np.frombuffer(self.payload, dtype='>i4').astype(np.int64)
        if self.kind == LGL:
            result = np.where(values == NA_INTEGER, np.nan, values.astype(float))
            return result
        return values

    def decode_rows(self, rows):
        """Decode only the listed elements of a numeric vector; others stay bytes."""
        widths = {REAL: (8, '>f8'), INT: (4, '>i4'), LGL: (4, '>i4')}
        if self.kind not in widths:
            raise ValueError('Row-wise decoding applies to numeric vectors')
        width, dtype = widths[self.kind]
        indices = [int(row) for row in rows]
        if any(row < 0 or row >= self.length for row in indices):
            raise IndexError('Row outside the vector')
        values = np.array([np.frombuffer(self.payload[row*width:(row+1)*width], dtype=dtype)[0]
                           for row in indices], dtype=float)
        if self.kind != REAL:
            values[values == NA_INTEGER] = np.nan
        return values

    def is_factor(self):
        return self.kind == INT and 'factor' in (self.attributes.get('class') or RVector(STR, 0, [])).payload

    def factor_labels(self):
        """Decode a factor's integer codes into level labels; NA codes are None."""
        if not self.is_factor():
            raise ValueError('Not a factor')
        levels = self.attributes['levels'].payload
        return [None if code == NA_INTEGER else levels[code-1] for code in self.decode()]


@dataclass
class RList:
    """A generic vector (list, data frame) or pairlist with attributes."""
    items: list
    names: list | None
    attributes: dict = field(default_factory=dict)


@dataclass
class RLanguage:
    """A structurally parsed closure, call, promise or environment; never evaluated."""
    kind: int
    parts: dict


class _Stream:
    def __init__(self, data):
        self.data = memoryview(data)
        self.position = 0
        self.references = []

    def take(self, count):
        if self.position+count > len(self.data):
            raise ValueError('Truncated R serialization stream')
        chunk = self.data[self.position:self.position+count]
        self.position += count
        return chunk

    def integer(self):
        return struct.unpack('>i', self.take(4))[0]

    def length(self):
        value = self.integer()
        if value == -1:
            upper, lower = struct.unpack('>II', self.take(8))
            value = (upper << 32) + lower
        if value < 0:
            raise ValueError('Negative vector length')
        return value


def _string_vector(stream):
    if stream.integer() != 0:
        raise ValueError('Named persistent string vectors are not supported')
    return [_item(stream) for _ in range(stream.integer())]


def _pairlist_to_dict(value):
    """Attribute pairlists become {tag: value} dictionaries."""
    result = {}
    while isinstance(value, RLanguage) and value.kind == LIST:
        result[value.parts['tag']] = value.parts['car']
        value = value.parts['cdr']
    return result


def _item(stream):
    flags = stream.integer()
    kind = flags & 0xFF
    levels = flags >> 12
    has_attributes, has_tag = bool(flags & (1 << 9)), bool(flags & (1 << 10))
    if kind == NILVALUE:
        return None
    if kind in (GLOBALENV, UNBOUND, MISSINGARG, BASENAMESPACE, EMPTYENV, BASEENV):
        return RLanguage(kind, {})
    if kind == REF:
        index = flags >> 8
        if index == 0:
            index = stream.integer()
        return stream.references[index-1]
    if kind in (PERSIST, PACKAGE, NAMESPACE):
        value = RLanguage(kind, {'names': _string_vector(stream)})
        stream.references.append(value)
        return value
    if kind == SYM:
        name = _item(stream)
        stream.references.append(name)
        return name
    if kind == ENV:
        value = RLanguage(ENV, {'locked': stream.integer()})
        stream.references.append(value)
        for part in ('enclosure', 'frame', 'hashtab', 'attributes'):
            value.parts[part] = _item(stream)
        return value
    if kind in (LIST, LANG, CLO, PROM, DOT):
        attributes = _pairlist_to_dict(_item(stream)) if has_attributes else {}
        tag = _item(stream) if has_tag else None
        car = _item(stream)
        cdr = _item(stream)
        return RLanguage(kind, {'tag': tag, 'car': car, 'cdr': cdr, 'attributes': attributes})
    if kind == ALTREP:
        raise ValueError('ALTREP serialization (RDX3 compact vectors) is not supported')
    if kind == BCODE:
        raise ValueError('Byte-code objects are not supported')
    if kind == EXTPTR:
        value = RLanguage(EXTPTR, {})
        stream.references.append(value)
        value.parts['protected'], value.parts['tag'] = _item(stream), _item(stream)
    elif kind == WEAKREF:
        value = RLanguage(WEAKREF, {})
        stream.references.append(value)
    elif kind in (SPECIAL, BUILTIN):
        value = RLanguage(kind, {'name': bytes(stream.take(stream.integer())).decode('ascii')})
    elif kind == CHAR:
        size = stream.integer()
        if size == -1:
            return None
        raw = bytes(stream.take(size))
        return raw.decode('latin-1' if levels & (1 << 2) else 'utf-8')
    elif kind in (LGL, INT):
        size = stream.length()
        value = RVector(kind, size, stream.take(4*size))
    elif kind == REAL:
        size = stream.length()
        value = RVector(kind, size, stream.take(8*size))
    elif kind == CPLX:
        size = stream.length()
        value = RVector(kind, size, stream.take(16*size))
    elif kind == STR:
        size = stream.length()
        value = RVector(kind, size, [_item(stream) for _ in range(size)])
    elif kind in (VEC, EXPR):
        size = stream.length()
        value = RList([_item(stream) for _ in range(size)], None)
    elif kind == RAW:
        size = stream.length()
        value = RVector(kind, size, stream.take(size))
    elif kind == S4:
        value = RList([], None)
    else:
        raise ValueError(f'Unsupported R serialization type {kind}')
    if has_attributes:
        value.attributes = _pairlist_to_dict(_item(stream))
        if isinstance(value, RList) and 'names' in value.attributes:
            value.names = value.attributes['names'].payload
    return value


def _open(path):
    with open(path, 'rb') as handle:
        magic = handle.read(6)
    if magic[:2] == b'\x1f\x8b':
        opener = gzip.open
    elif magic[:3] == b'BZh':
        opener = bz2.open
    elif magic[:6] == b'\xfd7zXZ\x00':
        opener = lzma.open
    else:
        opener = open
    with opener(path, 'rb') as handle:
        return handle.read()


def load_rdata(path):
    """Return {object name: parsed object} for an R workspace file."""
    data = _open(path)
    if data[:5] not in (b'RDX2\n', b'RDX3\n'):
        raise ValueError('Not an R workspace (RDX2/RDX3) file')
    stream = _Stream(data[5:])
    if bytes(stream.take(2)) != b'X\n':
        raise ValueError('Only XDR-format R workspaces are supported')
    version = stream.integer()
    stream.integer(), stream.integer()
    if version == 3:
        stream.take(stream.integer())
    elif version != 2:
        raise ValueError(f'Unsupported serialization version {version}')
    saved = _item(stream)
    if stream.position != len(stream.data):
        raise ValueError('Trailing bytes after the R workspace object')
    return _pairlist_to_dict(saved)


def data_frame(value):
    """Columns of an R data frame as {name: RVector}, without decoding numbers."""
    if not isinstance(value, RList) or 'data.frame' not in (value.attributes.get('class') or RVector(STR, 0, [])).payload:
        raise ValueError('Not an R data frame')
    if value.names is None or len(value.names) != len(value.items) or len(set(value.names)) != len(value.names):
        raise ValueError('Data frame columns need distinct names')
    lengths = {item.length for item in value.items}
    if len(lengths) > 1:
        raise ValueError('Data frame columns differ in length')
    return dict(zip(value.names, value.items))
