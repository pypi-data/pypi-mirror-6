# -*- coding: utf-8 -*-
# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

# Python 2 and 3 compatibility utilities
import six

from blist import sorteddict
from recordtype import recordtype

from .authtree import MemoryPatriciaAuthTree
from .core import Output
from .hash import hash256
from .mixins import SerializableMixin
from .serialize import BigCompactSize, LittleInteger, VarInt
from .tools import compress_amount, decompress_amount

__all__ = (
    'UnspentTransaction',
    'OutPoint',
    'Coin',
    'BaseValidationIndex',
    'MemoryValidationIndex',
    'ContractOutPoint',
    'ContractCoin',
    'BaseContractIndex',
    'MemoryContractIndex',
)

# ===----------------------------------------------------------------------===

from .script import ScriptPickler

class UnspentTransaction(SerializableMixin, sorteddict):
    """Pruned version of core.Transaction: only retains metadata and unspent
    transaction outputs.

    Serialized format:
        - VARINT(version)
        - VARINT(code)
        - unspentness bitvector, for outputs[2] and further; least significant
          byte first
        - the non-spent, compressed TransactionOutputs
        - VARINT(height)
        - VARINT(reference_height)

    The code value consists of:
        - bit 1: outputs[0] is not spent
        - bit 2: outputs[1] is not spent
        - bit 3: outputs[2] is not spent
        - The higher bits encode N, the number of non-zero bytes in the following
          bitvector.
            - In case bit 1, bit 2 and bit 4 are all unset, they encode N-1, as
              there must be at least one non-spent output.

    Example: 0102835800816115944e077fe7c803cfa57f29b36bf87c1d358bb85e
             <><><--------------------------------------------><---->
             |  \                  |                             /
       version   code           outputs[1]                  height
    
        - version = 1
        - code = 2 (outputs[1] is not spent, and 0 non-zero bytes of bitvector follow)
        - unspentness bitvector: as 0 non-zero bytes follow, it has length 0
        - outputs[1]: 835800816115944e077fe7c803cfa57f29b36bf87c1d35
            * 8358: compact amount representation for 60000000000 (600 BTC)
            * 00: special txout type pay-to-pubkey-hash
            * 816115944e077fe7c803cfa57f29b36bf87c1d35: address uint160
        - height = 203998
    
     Example: 0208044086ef97d5790061b01caab50f1b8e9c50a5057eb43c2d9563a4ee...
              <><><--><-------------------------------------------------->
             /  |   \                     |
      version  code  unspentness     outputs[4]

              ...bbd123008c988f1a4a4de2161e0f50aac7f17e7f9555caa486af3b8668
                 <----------------------------------------------><----><-->
                                         |                        /      |
                                    outputs[16]              height  reference_height
    
      - version = 2
      - code = 8: neither outputs[0], outputs[1], nor outputs[2] are unspent, 2
        (1, +1 because both bit 2 and bit 4 are unset) non-zero bitvector bytes
        follow.
      - unspentness bitvector: bits 1 (0x02) and 13 (0x2000) are set, so
        outputs[1+3] and outputs[13+3] are unspent
      - outputs[4]: 86ef97d5790061b01caab50f1b8e9c50a5057eb43c2d9563a4ee
                    * 86ef97d579: compact amount representation for 234925952 (2.35 BTC)
                    * 00: special txout type pay-to-pubkey-hash
                    * 61b01caab50f1b8e9c50a5057eb43c2d9563a4ee: address uint160
      - outputs[16]: bbd123008c988f1a4a4de2161e0f50aac7f17e7f9555caa4
                     * bbd123: compact amount representation for 110397 (0.001 BTC)
                     * 00: special txout type pay-to-pubkey-hash
                     * 8c988f1a4a4de2161e0f50aac7f17e7f9555caa4: address uint160
      - height = 120891
      - reference_height = 1000
    """
    # We only need one script pickler, which every instance of UnspentTransaction
    # can use (there's no concurrency issues with picklers, and it needs to be
    # available to the class anyway for deserialize).
    _pickler = ScriptPickler()

    def __init__(self, *args, **kwargs):
        # Since we behave like a dictionary object, we implement the copy
        # constructor, which requires copying meta information not contained
        # within the dictionary itself.
        if args and all(hasattr(args[0], x) for x in
                ('version', 'height', 'reference_height')):
            other = args[0]
        else:
            other = None

        # You can either specify the transaction, another UnspentTransaction
        # object, or the metadata directly. Choose one.
        a = 'transaction' in kwargs
        b = other is not None
        c = any(x in kwargs for x in ('version', 'reference_height'))
        if a + b + c >= 2: # <-- yes, you can do this
            raise TypeError(u"instantiate by either specifying the "
                u"transaction directly, another %s, or its individual "
                u"metadata; choose one" % self.__class__.__name__)

        # Extract captured parameters from kwargs, starting with the transaction
        # because its metadata are used as the default.
        transaction = kwargs.pop('transaction', None)
        if other is None:
            other = transaction

        version = kwargs.pop('version', getattr(other, 'version', 1))
        height = kwargs.pop('height', getattr(other, 'height', 0))

        # Reference heights are added with transaction version=2, so we do
        # not extract that parameter unless version=2.
        reference_height = getattr(other, 'reference_height', 0)
        if version in (2,):
            reference_height = kwargs.pop('reference_height', reference_height)

        # Perform construction of the dictionary object (our superclass)
        super(UnspentTransaction, self).__init__(*args, **kwargs)

        # Store metadata
        self.version          = version
        self.height           = height
        self.reference_height = reference_height

        # Add the transaction's outputs only if outputs are not separately
        # specified (as is typically done if it is known in advance which
        # outputs are not spent at time of creation).
        if transaction is not None and not self:
            for idx,output in enumerate(transaction.outputs):
                self[idx] = output

    def serialize(self):
        # code&0x1: outputs[0] unspent
        # code&0x2: outputs[1] unspent
        # code&0x4: outputs[2] unspent
        # code>>3: N, the minimal length of bitvector in bytes, or N-1 if
        #   outputs[0], outputs[1], and outputs[1] are all spent
        bitvector = 0
        for idx in six.iterkeys(self):
            bitvector |= 1 << idx
        if not bitvector:
            raise TypeError()
        code = bitvector & 0x7
        bitvector >>= 3
        bitvector = LittleInteger(bitvector).serialize()
        bitvector_len = len(bitvector)
        if not code:
            bitvector_len -= 1
        code |= bitvector_len << 3

        result  = VarInt(self.version).serialize()
        result += VarInt(code).serialize()
        result += bitvector
        for output in six.itervalues(self):
            result += VarInt(compress_amount(output.amount)).serialize()
            result += self._pickler.dumps(output.contract)
        result += VarInt(self.height).serialize()
        if self.version in (2,):
            result += VarInt(self.reference_height).serialize()
        return result
    @classmethod
    def deserialize(cls, file_):
        output_class = getattr(cls, 'get_output_class', lambda:
                       getattr(cls, 'output_class', Output))()
        kwargs = {}
        kwargs['version'] = VarInt.deserialize(file_)

        # See description of code, bitvector above.
        code, bitvector = VarInt.deserialize(file_), 0
        bitvector |= code & 0x7
        code >>= 3
        if not bitvector:
            code += 1
        if code:
            bitvector |= LittleInteger.deserialize(file_, code) << 3
        idx, items = 0, []
        while bitvector:
            if bitvector & 0x1:
                items.append(
                    (idx, output_class(
                        decompress_amount(VarInt.deserialize(file_)),
                        cls._pickler.load(file_))))
            idx, bitvector = idx + 1, bitvector >> 1

        kwargs['height'] = VarInt.deserialize(file_)
        if kwargs['version'] in (2,):
            kwargs['reference_height'] = VarInt.deserialize(file_)
        return cls(items, **kwargs)

    def __eq__(self, other):
        # Compare metadata first, as it's probably less expensive
        if any((self.height  != other.height,
                self.version != other.version)):
            return False
        if self.version in (2,) and self.reference_height != other.reference_height:
            return False
        return super(UnspentTransaction, self).__eq__(other)
    __ne__ = lambda a,b:not a==b
    def __repr__(self):
        return '%s%s, version=%d, height=%d, reference_height=%d)' % (
            self.__class__.__name__,
            super(UnspentTransaction, self).__repr__()[10:-1],
            self.version,
            self.height,
            self.reference_height)

# ===----------------------------------------------------------------------===

OutPoint = recordtype('OutPoint', ['hash', 'index'])
def _serialize_outpoint(self):
    parts = list()
    parts.append(hash256.serialize(self.hash))
    if self.index == -1:
        parts.append(b'\xfe\xff\xff\xff\xff')
    else:
        parts.append(BigCompactSize(self.index).serialize())
    return b''.join(parts)
OutPoint.serialize = _serialize_outpoint
def _deserialize_outpoint(cls, file_):
    kwargs = dict()
    kwargs['hash'] = hash256.deserialize(file_)
    kwargs['index'] = BigCompactSize.deserialize(file_)
    return cls(**kwargs)
OutPoint.deserialize = classmethod(_deserialize_outpoint)
def _repr_outpoint(self):
    return '%s(hash=%064x, index=%d)' % (
        self.__class__.__name__, self.hash, self.index==2**32-1 and -1 or self.index)
OutPoint.__repr__ = _repr_outpoint

Coin = recordtype('Coin',
    ['version', 'amount', 'contract', 'height', 'reference_height'])
Coin._pickler = ScriptPickler()
def _serialize_coin(self):
    parts = list()
    parts.append(VarInt(self.version).serialize())
    parts.append(VarInt(compress_amount(self.amount)).serialize())
    parts.append(self._pickler.dumps(self.contract.serialize()))
    parts.append(VarInt(self.height).serialize())
    if self.version in (2,):
        parts.append(VarInt(self.reference_height).serialize())
    return b''.join(parts)
Coin.serialize = _serialize_coin
def _deserialize_coin(cls, file_):
    kwargs = dict()
    kwargs['version'] = VarInt.deserialize(file_)
    kwargs['amount'] = decompress_amount(VarInt.deserialize(file_))
    kwargs['contract'] = cls._pickler.load(file_)
    kwargs['height'] = VarInt.deserialize(file_)
    if kwargs['version'] in (2,):
        kwargs['reference_height'] = VarInt.deserialize(file_)
    return cls(**kwargs)
Coin.deserialize = classmethod(_deserialize_coin)
def _repr_coin(self):
    parts = list()
    parts.append('version=%d'  % self.version)
    parts.append('amount=%d'   % self.amount)
    parts.append('contract=%s' % repr(self.contract))
    parts.append('height=%d'   % self.height)
    if self.version in (2,):
        parts.append('reference_height=%d' % self.reference_height)
    return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))
Coin.__repr__ = _repr_coin

class BaseValidationIndex(object):
    key_class = OutPoint
    value_class = Coin

class MemoryValidationIndex(BaseValidationIndex, MemoryPatriciaAuthTree):
    pass

# ===----------------------------------------------------------------------===

ContractOutPoint = recordtype('ContractOutPoint', ['contract', 'hash', 'index'])
ContractOutPoint._pickler = ScriptPickler()
def _serialize_contract_outpoint(self):
    return b''.join([self._pickler.dumps(self.contract.serialize()),
                     hash256.serialize(self.hash),
                     BigCompactSize(self.index).serialize()])
ContractOutPoint.serialize = _serialize_contract_outpoint
def _deserialize_contract_outpoint(cls, file_):
    kwargs = dict()
    kwargs['contract'] = cls._pickler.load(file_)
    kwargs['hash'] = hash256.deserialize(file_)
    kwargs['index'] = BigCompactSize.deserialize(file_)
    return cls(**kwargs)
ContractOutPoint.deserialize = classmethod(_deserialize_contract_outpoint)
def _repr_contract_outpoint(self):
    return '%s(contract=%s, hash=%064x, index=%d)' % (
        self.__class__.__name__, repr(self.contract), self.hash, self.index)
ContractOutPoint.__repr__ = _repr_contract_outpoint

ContractCoin = recordtype('ContractCoin',
    ['version', 'amount', 'height', 'reference_height'])
def _serialize_contract_coin(self):
    parts = list()
    parts.append(VarInt(self.version).serialize())
    parts.append(VarInt(compress_amount(self.amount)).serialize())
    parts.append(VarInt(self.height).serialize())
    if self.version in (2,):
        parts.append(VarInt(self.reference_height).serialize())
    return b''.join(parts)
ContractCoin.serialize = _serialize_contract_coin
def _deserialize_contract_coin(cls, file_):
    kwargs = dict()
    kwargs['version'] = VarInt.deserialize(file_)
    kwargs['height'] = VarInt.deserialize(file_)
    kwargs['amount'] = decompress_amount(VarInt.deserialize(file_))
    if kwargs['version'] in (2,):
        kwargs['reference_height'] = VarInt.deserialize(file_)
    return cls(**kwargs)
ContractCoin.deserialize = classmethod(_deserialize_contract_coin)
def _repr_contract_coin(self):
    parts = list()
    parts.append('version=%d' % self.version)
    parts.append('amount=%d'  % self.amount)
    parts.append('height=%d'  % self.height)
    if self.version in (2,):
        parts.append('reference_height=%d' % self.reference_height)
    return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))
ContractCoin.__repr__ = _repr_contract_coin

class BaseContractIndex(object):
    key_class = ContractOutPoint
    value_class = ContractCoin

class MemoryContractIndex(BaseContractIndex, MemoryPatriciaAuthTree):
    pass
