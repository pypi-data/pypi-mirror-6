# -*- coding: utf-8
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.

from unicodedata import category
from datetime import datetime
from collections import defaultdict
import os.path as osp
import re
import io

from cubicweb.dataimport import ucsvreader


def _init_rdflib():
    try:
        import rdflib
    except ImportError:
        raise NotImplementedError('rdflib does not seem to be available.')
    return rdflib

def _init_librdf():
    try:
        import RDF
    except ImportError:
        raise NotImplementedError('librdf does not seem to be available.')
    return RDF


###############################################################################
### GLOBAL VARIABLES ##########################################################
###############################################################################

EXTENSION_MAPPING = {'.nt':  'ntriples',
                     '.ttl': 'n3',
                     '.n3':  'n3',
                     '.xml': 'rdfxml',
                     '.rdf': 'rdfxml',
                     }

LIBRDF_FORMATS_MAPPING = {'ntriples': 'ntriples',
                          'n3':       'turtle',
                          'rdfxml':   'rdfxml',
                          }

RDFLIB_FORMATS_MAPPING = {'ntriples': 'nt',
                          'n3':       'n3',
                          'rdfxml':   'xml',
                          }

SEPARATOR_MAPPING = {'space': ' ', 'comma': ',', 'tab': '\t'}

DEFAULT_NAMESPACE = 'http://ns.cubicweb.org/cubicweb/0.0/'

NAMESPACES = {
    'cw': DEFAULT_NAMESPACE,

    'bnf-onto': 'http://data.bnf.fr/ontology/',
    'cc': 'http://creativecommons.org/ns#',
    'dc': 'http://purl.org/dc/terms/',
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'dbpedia': 'http://dbpedia.org/',
    'dbpediaowl': 'http://dbpedia.org/ontology/',
    'dbprop': 'http://dbpedia.org/property/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'frbr': 'http://rdvocab.info/uri/schema/FRBRentitiesRDA/',
    'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
    'og': 'http://ogp.me/ns#',
    'ore': 'http://www.openarchives.org/ore/terms/',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdagroup1elements': 'http://RDVocab.info/Elements/',
    'rdagroup2elements': 'http://RDVocab.info/ElementsGr2/',
    'rdarelationships': 'http://rdvocab.info/RDARelationshipsWEMI/',
    'rdarole': 'http://rdvocab.info/roles/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'swvs': 'http://www.w3.org/2003/06/sw-vocab-status/ns#',
    'xfoaf': 'http://www.foafrealm.org/xfoaf/0.1/',
    }

REVERSE_NAMESPACES = dict([(v,k) for k,v in NAMESPACES.items()])

NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
ALLOWED_NAME_CHARS = [u"\u00B7", u"\u0387", u"-", u".", u"_"]
XMLNS = "http://www.w3.org/XML/1998/namespace"

# RDF property used to store uri
URI_RDF_PROP = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#about'


################################################################################
### READER CLASS ###############################################################
################################################################################

class AbstractRdfReader(object):
    """ Abstract class for readers """

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def detect_file_format(self, filename):
        try:
            return EXTENSION_MAPPING[osp.splitext(filename)[-1]]
        except KeyError:
            raise ValueError("can't detect format of %s" % filename)

    def iterate_triples_from_file(self, filename, rdf_format=None):
        """ Iterate triples over the given file
        """
        if rdf_format is None:
            rdf_format = self.detect_file_format(filename)
        with open(filename) as fobj:
            # don't return the generator, file will be closed before being
            # parsed...
            for data in self._iterate_triples(fobj, rdf_format):
                yield data

    def _iterate_triples(self, fobj, rdf_format):
        """ Iterate triples over the given open file
        """
        raise NotImplementedError()


class RawNtRdfReader(AbstractRdfReader):
    """ Raw nt reader class """
    BASE_RESOURCE_REGEXP = r'^<(.*)>\s+<(.*)>\s+<(.*)>\s*.\s*$'
    BASE_LITERAL_REGEXP = r'^<(.*)>\s+<(.*)>\s+"(.*)"(?:\@.*)*\s*.\s*'

    def __init__(self, resource_regexp=None, literal_regexp=None, encoding='utf-8'):
        """ Init the Raw nt rdf reader with a resource regexp and a literal
        regexp (and optionaly an encoding).  If not specified, use the regexp
        specified by the BASE_RESOURCE_REGEXP and BASE_LITERAL_REGEXP class
        attributes.
        """
        super(RawNtRdfReader, self).__init__(encoding=encoding)
        resource_regexp = resource_regexp or self.BASE_RESOURCE_REGEXP
        literal_regexp = literal_regexp or self.BASE_LITERAL_REGEXP
        self.literal_regexp = re.compile(literal_regexp)
        self.resource_regexp = re.compile(resource_regexp)

    def _iterate_triples(self, fobj, rdf_format):
        """ Iterate triples using rawnt format (e.g. from split function)
        """
        if rdf_format not in ('ntriples', 'n3'):
            raise ValueError('Only ntriples/n3 formats are usable with the rawnt reader, not %s'
                             % rdf_format)
        for line in fobj:
            data = []
            match = self.resource_regexp.match(line)
            if match:
                data = [m.decode(self.encoding) for m in match.groups()]
                data.append('resource')
                yield tuple(data)
                continue
            match = self.literal_regexp.match(line)
            if match:
                data = [m.decode(self.encoding) for m in match.groups()]
                data.append('literal')
                yield tuple(data)


class LibRdfReader(AbstractRdfReader):
    """ RDF based reader class """

    def __init__(self, *args, **kwargs):
        super(LibRdfReader, self).__init__(*args, **kwargs)
        self._RDF = _init_librdf()

    def iterate_triples_from_file(self, filename, rdf_format=None):
        """ Iterate triples over the given file
        """
        if rdf_format is None:
            rdf_format = self.detect_file_format(filename)
        parser = self._RDF.Parser(name=LIBRDF_FORMATS_MAPPING[rdf_format])
        for triple in parser.parse_as_stream('file://' + osp.realpath(filename)):
            if triple.subject.is_blank() or triple.object.is_blank():
                continue
            _subject = unicode(triple.subject.uri)
            _predicate = unicode(triple.predicate.uri)
            if triple.object.is_resource():
                otype = u'resource'
                _object = unicode(triple.object.uri)
            else:
                otype = u'literal'
                _object = unicode(triple.object.literal_value['string'])
            yield _subject, _predicate, _object, otype


class RdfLibReader(AbstractRdfReader):
    """ rdflib based reader class """

    def __init__(self, *args, **kwargs):
        super(RdfLibReader, self).__init__(*args, **kwargs)
        self._RDF = _init_rdflib()

    def _iterate_triples(self, fobj, rdf_format):
        """ Iterate triples using rdflib
        """
        URIRef = self._RDF.URIRef # copy to locals
        rdfgraph = self._RDF.ConjunctiveGraph()
        rdfgraph.parse(fobj, format=RDFLIB_FORMATS_MAPPING[rdf_format])
        for _subject, _predicate, _object in rdfgraph:
            if isinstance(_object, URIRef):
                otype = 'resource'
            else:
                otype = 'literal'
            _object = _object.format()
            yield unicode(_subject.format()), unicode(_predicate), _object, otype


class CSVRdfReader(AbstractRdfReader):
    """ CSV reader mimicking RDF """

    def __init__(self, fields=None, encoding='utf-8'):
        super(CSVRdfReader, self).__init__(encoding=encoding)
        self.fields = fields or {}

    # XXX rdf_format argument makes no sense and CSVRdfReader isn't exposed,
    # should it support this API?
    def iterate_triples_from_file(self, filename, rdf_format=None,
                                  separator=',',
                                  null_value='NULL',
                                  uri_ind=None, _header=0,
                                  limit=None, ignore_errors=False):
        """ Iterate triples over the given file """
        if separator in SEPARATOR_MAPPING:
            separator = SEPARATOR_MAPPING[separator]
        fobj = ucsvreader(open(filename), separator=separator,
                          ignore_errors=ignore_errors)
        for data in self.iterate_triples(fobj, uri_ind=uri_ind,
                                         null_value='NULL',
                                         _header=_header, limit=limit):
            yield data

    def iterate_triples(self, fobj, uri_ind=None, null_value='NULL',
                        _header=0, limit=None):
        """ Iterate triples using librdf """
        for row_ind, row in enumerate(fobj):
            #XXX We should take care from line skipping, because ucsvreader() with
            #    ignore_errors=True already skips the first line !
            if _header and row_ind < _header:
                continue
            if limit and row_ind > limit:
                break
            _subject = row[uri_ind] if uri_ind is not None else 'row %s' % row_ind
            for col_ind, _object in enumerate(row):
                if not self.fields:
                    _predicate = 'col %s' % col_ind
                elif self.fields and col_ind in self.fields:
                    _predicate = self.fields[col_ind]
                else:
                    continue
                if _object != null_value:
                    otype = 'literal' if not _object.startswith('http') else 'resource'
                    yield _subject, _predicate, _object, otype



################################################################################
### WRITER CLASS  ##############################################################
################################################################################

class AbstractRdfWriter(object):
    """ Abstract class for writer """

    def __init__(self, encoding='utf-8'):
        self.triples_counter = 0
        self.graph = None
        self.encoding = encoding
        self._init_graph()

    def _init_graph(self):
        """ Init a empty graph
        """
        raise NotImplementedError()

    def do_add_triple(self, _s, _p, _o, _ot):
        """ Add a triple to the current graph
        """
        raise NotImplementedError()

    def write(self, buff, rdf_format=None):
        """ Write the graph into a given file-like buffer
        """
        raise NotImplementedError()

    def add_triple(self, _s, _p, _o, _ot):
        """ Add a triple to the current graph
        """
        self.triples_counter += 1
        self.do_add_triple(_s, _p, _o, _ot)

    def autodetect_type(self, _o, _ot=None):
        """ Try to autodetect data type
        """
        if _ot:
            return _ot
        return 'literal' if not _o.startswith('http') else 'resource'

    def write_file(self, filename, rdf_format=None):
        """ Write the graph into the given file
        """
        with open(filename, 'w') as fobj:
            self.write(fobj, rdf_format)


class RawNtRdfWriter(AbstractRdfWriter):
    """ Raw nt writer class """

    def __init__(self, *args, **kwargs):
        super(RawNtRdfWriter, self).__init__(*args, **kwargs)

    def _init_graph(self):
        self.graph = []

    def do_add_triple(self, _s, _p, _o, _ot=None):
        _ot = self.autodetect_type(_o, _ot)
        if _ot == 'literal':
            self.graph.append(u'<%s> <%s> "%s" .' % (_s, _p, _o))
        if _ot == 'resource':
            self.graph.append(u'<%s> <%s> <%s> .' % (_s, _p, _o))

    def write(self, buff, rdf_format=None):
        if self.graph:
            buff.write('\n'.join(self.graph).encode(self.encoding))


class LibRdfWriter(AbstractRdfWriter):
    """ RDF based writer class """

    def __init__(self, xy=None, encoding='utf-8'):
        self.xyreg = xy
        self._RDF = _init_librdf()
        self._Uri = self._RDF.Uri
        super(LibRdfWriter, self).__init__(encoding)

    def _init_graph(self):
        self.graph = self._RDF.Model()

    def do_add_triple(self, _s, _p, _o, _ot=None):
        _ot = self.autodetect_type(_o, _ot)
        if _ot == 'resource':
            _o = self._Uri(_o.encode(self.encoding))
        else:
            _o = _o.encode(self.encoding)
        self.graph.append(self._RDF.Statement(self._Uri(_s.encode(self.encoding)),
                                              self._Uri(_p.encode(self.encoding)),
                                              _o))

    def write(self, buff, rdf_format=None):
        rdf_format = LIBRDF_FORMATS_MAPPING.get(rdf_format, 'rdfxml')
        serializer = self._RDF.Serializer(name=rdf_format)
        if self.xyreg:
            for rdfns, vocab in self.xyreg.reverse_ns.iteritems():
                serializer.set_namespace(vocab, rdfns)
        buff.write(serializer.serialize_model_to_string(self.graph))


class RdfLibWriter(AbstractRdfWriter):
    """ rdflib based writer class """

    def __init__(self, xy=None, encoding='utf-8'):
        self.xyreg = xy
        self._RDF = _init_rdflib()
        self._Uri = self._RDF.URIRef
        super(RdfLibWriter, self).__init__(encoding)

    def _init_graph(self):
        self.graph = self._RDF.ConjunctiveGraph()
        if self.xyreg:
            for rdfns, vocab in self.xyreg.reverse_ns.iteritems():
                self.graph.bind(vocab, rdfns)

    def do_add_triple(self, _s, _p, _o, _ot=None):
        _ot = self.autodetect_type(_o, _ot)
        if _ot == 'resource':
            _o = self._Uri(_o.encode(self.encoding))
        else:
            _o = self._RDF.Literal(_o.encode(self.encoding))
        self.graph.add((self._Uri(_s), self._Uri(_p), _o))

    def write(self, buff, rdf_format=None):
        rdf_format = RDFLIB_FORMATS_MAPPING.get(rdf_format, 'xml')
        buff.write(self.graph.serialize(format=rdf_format))
        self.graph.close()


class CSVRdfWriter(AbstractRdfWriter):
    """ CSV writer mimicing RDF """

    def __init__(self, separator=',', null_value='NULL', encoding='utf-8'):
        super(CSVRdfWriter, self).__init__(encoding)
        self.separator = ','
        self.null_value = null_value

    def _init_graph(self):
        self.graph = defaultdict(dict)
        self.fields = set()

    def do_add_triple(self, _s, _p, _o, _ot=None):
        _o.encode(self.encoding)
        self.graph[_s][_p] = _o
        self.fields.add(_p)

    def write(self, buff, rdf_format=None):
        fields = list(self.fields)
        for uri, objects in self.graph.iteritems():
            data = [uri,]
            for field in fields:
                data.append(objects.get(field, self.null_value))
            buff.write(self.separator.join(data).encode(self.encoding)+'\n')


################################################################################
### UTILITY FUNCTIONS ##########################################################
################################################################################
def build_rdf_reader(library, encoding='utf-8'):
    """ Build and return a reader object given a library, a rdf_format and an
    encoding.

    Possible libraries are 'rdflib', 'librdf' and 'rawnt'.
    """
    if library == 'rdflib':
        return RdfLibReader(encoding=encoding)
    elif library == 'librdf':
        return LibRdfReader(encoding=encoding)
    elif library == 'rawnt':
        return RawNtRdfReader(encoding=encoding)
    raise NotImplementedError('Unknown library %s: should be rdflib, librdf '
                              'or rawnt' % library)

def build_rdf_writer(library='rdflib', encoding='utf-8', xy=None):
    """ Build and return a writer object given a library, an encoding and a xy
    object.

    Possible libraries are 'rdflib', 'librdf' and 'rawnt'.
    """
    if library == 'rdflib':
        return RdfLibWriter(xy=xy, encoding=encoding)
    elif library == 'librdf':
        return LibRdfWriter(xy=xy, encoding=encoding)
    elif library == 'rawnt':
        return RawNtRdfWriter(encoding=encoding)
    raise NotImplementedError('Unknown library %s: should be rdflib, librdf '
                              'or rawnt' % library)


###############################################################################
### CONVERTER FUNCTIONS #######################################################
###############################################################################

def convert_string(_object,  **kwargs):
    """ Convert an rdf value to a String """
    return _object

def convert_int(_object, **kwargs):
    """ Convert an rdf value to an int """
    try:
        return int(_object)
    except:
        return None

def convert_float(_object, **kwargs):
    """ Convert an rdf value to a float """
    try:
        return float(_object.replace(',', '.'))
    except:
        return None

def convert_date(_object, datetime_format='%d-%m-%Y', **kwargs):
    """ Convert an rdf value to a date """
    try:
        return datetime.strptime(_object, datetime_format)
    except:
        return None

def convert_geo(_object, **kwargs):
    """ Convert an rdf value to a geo
    XXX GEO DOES NOT EXIST FOR NOW IN YAMS
    """
    try:
        # XXX Bad conversion
        _object = _object.replace(' ', '').replace("'", '').replace(u'°', '.').strip().lower()
        if not _object.isdigit():
            for a in ascii_lowercase:
                _object = _object.replace(a, '')
            _object = _object.strip()
        return float(_object)
    except:
        return None

DEFAULT_CONVERTERS = {'String': convert_string,
                      'Int': convert_int,
                      'BigInt': convert_int,
                      'Float': convert_float,
                      'Date': convert_date,
                      'Geo': convert_geo}


###############################################################################
### RDF UTILITY FUNCTIONS #####################################################
###############################################################################

def normalize_xml(uri, namespaces=REVERSE_NAMESPACES):
    """ Return an clean RDF node from an uri, e.g.
    http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation -> rdf:Manifestation
    """
    uri_ns, uri_part = split_uri(uri)
    return ':'.join([namespaces.get(uri_ns, uri_ns), uri_part])

def split_uri(uri):
    """ Split an uri between the namespace and the property, ie.
    http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation
    ->
    (http://rdvocab.info/uri/schema/FRBRentitiesRDA/ , Manifestation)

    This is a backport from rdflib, as we don't want a hard dependancy on it
    """
    if uri.startswith(XMLNS):
        return (XMLNS, uri.split(XMLNS)[1])
    length = len(uri)
    uri = unicode(uri)
    for i in xrange(0, length):
        c = uri[-i-1]
        if not category(c) in NAME_CATEGORIES:
            if c in ALLOWED_NAME_CHARS:
                continue
            for j in xrange(-1-i, length):
                if category(uri[j]) in NAME_START_CATEGORIES or uri[j]=="_":
                    ns = uri[:j]
                    if not ns:
                        break
                    ln = uri[j:]
                    return (ns, ln)
            break
    raise Exception("Can't split '%s'" % uri)

def build_uri_dict(filenames, library='librdf', rdf_format=None, encoding='utf-8', limit=None):
    """ Build a dictionary (ns:part, (predicate, object)) for each uri, from an rdf file """
    reader = build_rdf_reader(library=library, encoding=encoding)
    # Construct the URI dictionary
    uri_dictionary = {}
    count = 0
    for filename in filenames:
        for uri, _predicate, _object, _type in reader.iterate_triples_from_file(filename, rdf_format):
            uri_dictionary.setdefault(uri, {})[URI_RDF_PROP] = [(uri, 'resource'),]
            uri_dictionary[uri].setdefault(_predicate, []).append((_object, _type))
            if limit is not None:
                count += 1
                if count > limit:
                    break
        if limit is not None and count > limit:
            break
    return uri_dictionary


###############################################################################
### FILE UTILITY FUNCTIONS ####################################################
###############################################################################

class DictFobj(object):
    """ Class for file-based dictionary, use for large file conversion based
    on a mapping.
    Learn the mapping (index, offset), where the key of interest
    is given by its value in the splitted line (index_key).
    The mapping gets, for a key, the offset in the file, and store it in an internal dict.
    It will re-read the line of corresponding offset on get() and return the
    line splitted on the separator (i.e. a list)

    >>>  filename = osp.join(HERE, 'data/mmap.csv')
    >>>  mmap = DictFobj(filename, separator=',', cast_type=int)
    >>>  mmap.fit()
    >>>  print mmap.get(1)[1]
    'Toto'

    """

    def __init__(self, fname, separator='\t', cast_type=None):
        """ Class for file-based dictionary, use for large file conversion based
        on a mapping.

        fname: name of the file
        separator: separator of the csv file
        cast_type: cast callback for the key of the dictionary (e.g. int)
        """
        self.fname = fname
        self.fobj = io.open(self.fname, 'rb', buffering=0)
        self.separator = separator
        self.cast_type = cast_type
        self.internal_dict = {}

    def __del__(self):
        self.fobj.close()

    def fit(self, index_key=0):
        """ Learn the mapping (index, offset), where the key of interest
        is given by its value in the splitted line (index_key).
        The mapping gets, for a key, the offset in the file, and store it in an internal dict
        """
        self.fobj.seek(0)
        pos = self.fobj.tell()
        while True:
            # Read the line
            line = self.fobj.readline()
            if not line:
                break
            # Get the key of the line (and eventually cast it)
            key = line.split(self.separator)[index_key]
            if self.cast_type:
                key = self.cast_type(key)
            # Store the result in an internal dict
            self.internal_dict[key] = pos
            pos = self.fobj.tell()

    def get(self, key):
        """Re-read the line of corresponding offset on get() and return the
        line splitted on the separator (i.e. a list)"""
        pos = self.internal_dict.get(key)
        if pos is None:
            return
        self.fobj.seek(pos)
        line = self.fobj.readline()
        return line.strip().split(self.separator)

