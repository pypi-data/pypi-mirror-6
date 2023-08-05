from itertools import chain
import re
from ..constants import *
from .. utils import util, nested_array
from .. utils.missing import Missing
from ..itypes import detector, rtypes, dimpaths, dimensions
from .. import repops_multi
import wrapper
from .. import ops
import python
from pyparsing import *


class OBORepresentor(wrapper.SourceRepresentor):
    def __init__(self, filename):
        parser = OBOParser(filename)
        records = [r for r in parser]

        feats_dim = dimensions.Dim(name='feats',shape=UNDEFINED, dependent=(True,))    
        records_dim = dimensions.Dim(name='records',shape=len(records))


        seq = self._getSequenceRep([r.get('sequence',Missing) for r in records], records_dim)
        loc_type = self._getFeatRep([r.get('feat_loc_type',[]) for r in records], feats_dim, records_dim, name='loc_type')
        feat_key = self._getFeatRep([r.get('feat_key',[]) for r in records], feats_dim, records_dim, name='feat_key')
        loc = self._getLocsRep([r.get('feat_locs',[]) for r in records], feats_dim, records_dim)
        rec = self._getRecordRep([r.get('record') for r in records], records_dim)
        attr = self._getAttrRep([r.get('feat_attr',[]) for r in records], feats_dim, records_dim)

        if any(['contig' in r for r in records]):
            clocs = self._getContigsRep([r.get('contig', Missing) for r in records], records_dim)
            res = repops_multi.Combine(rec, clocs, loc_type, loc, feat_key, attr, seq).Copy()
        else:
            res = repops_multi.Combine(rec, loc_type, loc, feat_key, attr, seq).Copy()

        self._initialize(tuple(res._slices))

    rectypes = {'length':int, 'alt_accessions':('alt_accessions',str), 'keywords':('keywords',str), 'organism_class':('organism_class',str), 'database':('references',str), 'database_identifier':('references',str)}

    def _getRecordRep(self, records, records_dim):
        keys = list(set(chain(*[r.keys() for r in records])))
        keys.sort()
        types = []
        dims = {}
        for key in keys:
            if key in self.rectypes:
                t = self.rectypes[key]
                if isinstance(t, tuple):
                    s = rtypes.createType(t[-1])
                    for pos, d in enumerate(t[::-1][1:]):
                        if not d in dims:
                            dim = dimensions.Dim(name=d,shape=UNDEFINED, dependent=(True,) * (len(t) - 1 - pos) )
                            dims[d] = dim
                        s = rtypes.TypeArray(dims=dimpaths.DimPath(dims[d]), subtypes=(s,))
                    t = s
                else:
                    t = rtypes.createType(t)
            else:
                t = rtypes.createType(str)
            types.append(t)

        rectype = rtypes.TypeRecordDict(fieldnames=tuple(keys), subtypes=tuple(types))
        rectype = rtypes.TypeArray(dims=dimpaths.DimPath(records_dim), subtypes=(rectype,))
        return python.Rep(records, dtype=rectype)

    attrtypes = {'transl_table':int, 'xref_database': ('feat_ref',str), 'xref_identifier' : ('feat_ref', str),'note' : ('notes', str),
                'codon_start': int, 'environmental_sample':bool, 'locus_tag':str, 'id':str,'gene':str,
                'organism': str, 'product':str, 'protein_id':str, 'mol_type':str, 'virion': bool, 'translation':'protein'}
                
    def _getAttrRep(self, records, feats_dim, records_dim):
        keys = set()
        for feats in records:
            for attr in feats:
                keys.update(attr)
        keys = list(keys)
        keys.sort()
        
        types = []
        dims = {}
        for key in keys:
            if not key in self.attrtypes:
                t = rtypes.createType('any')
            else:
                t = self.attrtypes[key]
                if isinstance(t, tuple):
                    s = rtypes.createType(t[-1])
                    for pos, d in enumerate(t[::-1][1:]):
                        if not d in dims:
                            dim = dimensions.Dim(name=d,shape=UNDEFINED, dependent=(True,) * (len(t) - pos) )
                            dims[d] = dim
                        s = rtypes.TypeArray(dims=dimpaths.DimPath(dims[d]), subtypes=(s,))
                    s.dims[0].has_missing=True
                    t = s
                else:
                    t = rtypes.createType(t)
            t.has_missing=True
            types.append(t)
         
        attrtype = rtypes.TypeRecordDict(fieldnames=tuple(keys), subtypes=tuple(types))
        attrtype = rtypes.TypeArray(dims=dimpaths.DimPath(feats_dim), subtypes=(attrtype,))
        attrtype = rtypes.TypeArray(dims=dimpaths.DimPath(records_dim), subtypes=(attrtype,))
        return python.Rep(records, dtype=attrtype, unpack=False, name='attr').Elems().Elems()
       

    def _getSequenceRep(self, seq, records_dim):
        dna = rtypes.createType('DNA')
        seqtype = rtypes.TypeArray(dims=dimpaths.DimPath(records_dim), subtypes=(dna,))
        return python.Rep(seq,dtype=seqtype, name='sequence')

    locnames = ['loc_name','start','stop','complement','type','fuzzy_before','fuzzy_after']
    loctypes = [str, int, int, bool, str, bool, bool]
    def _getLocsRep(self, data, feats_dim, records_dim):
        types = [rtypes.createType(t) for t in self.loctypes]
        loctype = rtypes.TypeRecordDict(fieldnames=tuple(self.locnames), subtypes=tuple(types))
        dim = dimensions.Dim(name='loc_elems',shape=UNDEFINED, dependent=(True,True))
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(dim), subtypes=(loctype,))
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(feats_dim), subtypes=(loctype,))
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(records_dim), subtypes=(loctype,))
        return python.Rep(data,dtype=loctype)
    
    def _getContigsRep(self, data, records_dim):
        types = [rtypes.createType(t) for t in self.loctypes]
        loctype = rtypes.TypeRecordDict(fieldnames=tuple(self.locnames), subtypes=tuple(types))
        dim = dimensions.Dim(name='contig_elems',shape=UNDEFINED, dependent=(True,),  has_missing=True)
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(dim), subtypes=(loctype,), has_missing=True)
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(records_dim), subtypes=(loctype,))
        return python.Rep(data,dtype=loctype, name='contigs',unpack=False).Elems().Elems()

    def _getFeatRep(self, data, feats_dim, records_dim, name):
        loctype = rtypes.createType(str)
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(feats_dim), subtypes=(loctype,))
        loctype = rtypes.TypeArray(dims=dimpaths.DimPath(records_dim), subtypes=(loctype,))
        return python.Rep(data,dtype=loctype,name=name)
       


featrec = ZeroOrMore(Group((LineStart() | Word('\n')) +  Suppress('/') + Word(alphas + '_') + Optional(Suppress('=') + (Word(nums).setParseAction(lambda x: map(int,x)) | QuotedString(quoteChar='"',  escQuote='""', multiline=True).setParseAction(lambda x: [e.replace('\n',' ') for e in x])))))

num = Word(nums)
date = num + Suppress('-') + Word(alphas) + Suppress('-') + num 
date_created = date + Suppress('(Rel.') + num + Suppress(', Created)')
date_updated = date + Suppress('(Rel.') + num + Suppress(', Last updated, Version') + num + Suppress(')')
organism = Group(OneOrMore(Word(alphas))) + Group(Optional('(' + OneOrMore(Word(alphas)) + ')'))


#location
number = Word(nums).setParseAction(lambda x: map(int,x))
start_number = Optional(Literal('<').setResultsName('fuzzybefore')) + number.setResultsName('start')
stop_number = Literal('>').setResultsName('fuzzyafter') + number.setResultsName('stop')
gap = Literal('gap(unk100)').setResultsName('gap')

name = CharsNotIn(':,')
identifier1 =  (Optional('<').setResultsName('fuzzybefore') + number.setResultsName('start'))
identifier2 = (Optional('>').setResultsName('fuzzyafter') + number.setResultsName('stop'))
loc = Group(Optional(name.setResultsName('name') + ':') + (identifier1 + oneOf('.. . ^').setResultsName('operator') + identifier2 | start_number | stop_number | gap))

loc_expression = Forward()
lparen = Literal("(").suppress()
rparen = Literal(")").suppress()

arg = loc | loc_expression
args = delimitedList(arg)
functor = (Literal('complement') | Literal('join') | Literal('order')).setResultsName('function')
loc_expression << (Group(functor + Group(lparen + Optional(args) + rparen)) | loc)



class OBOParser(object):
    stanza_header = re.compile(r'^\[[^\]]+\]$')

    def __init__(self, filename):
        self.reader = util.PeekAheadFileReader(filename)
        self.parseHeader()

    def __iter__(self):
        return self
    
    def next(self):
        r = self.parseRecord()
        if r is None:
            raise StopIteration
        return r

    def parseHeader(self):
        pass

    def startRecord(self):
        self.record = {}
        self.record['record'] = {}

    def finishRecord(self):
        return self.record

    def parseRecord(self):
        self.reader.skipWhite()
        if self.reader.eof():
            return None

        pos = self.reader.tell()

        m = None
        while m is None:
            line = self.reader.next()
            m = self.stanza_header.match(line.strip())

        if m is None:
            return None
        else:                
            rc = self.record
            self.startRecord()

        return self.finishRecord()

