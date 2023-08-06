''' Various utilities when dealing with files, ndarrays

This module defines a set of utility functions to be used by individual 
formats as well as exceptions.

.. Created on Oct 10, 2010
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
from type_utility import is_float_int
import collections
import operator
import functools
import os, logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

__header_seperators = (',', ';', os.sep)

class FormatError(StandardError):
    """Exception raised for errors in parsing/writing a format
    """
    pass

class ParseFormatError(FormatError):
    """Exception raised for errors in parsing a format
    """
    pass

class WriteFormatError(FormatError):
    """Exception raised for errors in writing a format
    """
    pass

class FormatUtilityError(StandardError):
    """Exception raised for errors in parsing values in the utility
    """
    pass

class MultipleEntryException(StandardError):
    """Exception raised when multiple tables are in a file
    """
    pass
    

def combine(vals):
    ''' Combine values from different files (only include common columns)
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> combine([NTuple(id=1, select=2, order=0), NTuple(id=5, select=0)])
    [CombinedArray(id=1, select=2), CombinedArray(id=5, select=0)]
    
    Args:
    
        vals : list
               List of lists of values
    
    Returns:
    
        vals : list
               List of combined values
    '''
    
    header = {}
    for v in vals:
        for h in v[0]._fields:
            header.setdefault(h, 0)
            header[h] += 1
    for key in header.keys():
        if header[key] < len(vals): del header[key]
    header = header.keys()
    Tuple = collections.namedtuple("CombinedArray", header)
    retvals = []
    for curr in vals:
        for v in curr:
            retvals.append(Tuple._make([getattr(v, h) for h in header]))
    return retvals



def new_filename(filename, prefix=None, suffix=None, ext=None, subdir=None):
    '''Add a prefix, suffix and/or extension to the given filename
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> print add_prefix('output.txt', 'new')
        'new_output.txt'
    
    Args:
    
        filename : str
                   Name of the file to prefix
        prefix : str
                 Prefix to add to a filename
        suffix : str
                 Suffix to add to a filename
        ext : str
              Extension to add to a filename
        subdir : str
                 New subdirectory
    
    Returns:
    
        filename : str
                   Filename with prefix
    '''
    
    if subdir is not None: filename = os.path.join(os.path.dirname(filename), subdir, os.path.basename(filename))
    if prefix is not None: filename = add_prefix(filename, prefix)
    if suffix is not None: filename = add_suffix(filename, suffix)
    if ext is not None:
        if len(ext) > 0 and ext[0] != '.': ext = "."+ext
        filename = os.path.splitext(filename)[0]+ext
    return filename

def add_prefix(filename, prefix):
    '''Add a prefix to the given filename
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> print add_prefix('output.txt', 'new')
        'new_output.txt'
    
    Args:
    
        filename : str
                   Name of the file to prefix
        prefix : str
                 Prefix to add to a filename
    
    Returns:
    
        filename : str
                   Filename with prefix
    '''
    
    if prefix is not None and prefix != "":
        base = os.path.basename(filename)
        path = os.path.dirname(filename)
        filename = os.path.join(path, prefix+base)
    return filename

def add_suffix(filename, suffix):
    '''Add a suffix to the given filename
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> print add_prefix('output.txt', 'new')
        'new_output.txt'
    
    Args:
    
        filename : str
                   Name of the file to suffix
        suffix : str
                 Suffix to add to a filename
    
    Returns:
        
        filename : str
                   Filename with suffix
    '''
    
    if suffix is not None and suffix != "":
        base, ext = os.path.splitext(filename)
        return base+suffix+ext
    return filename

def create_namedtuple_list(values, name, header, label=None, good=None):
    ''' Create a list of namedtuples from a collection of values
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> values = [ [1,0], [2,1], [3,1] ]
    >>> create_collections.namedtuple_list(values, "Selection", "id,select")
    [ Selection(id=1, select=0), Selection(id=2, select=1) Selection(id=3, select=1) ]
    
    Args:
    
        val : collection
              Iterable 2D collection of values
        name : str
                Name of collections.namedtuple class
        header : str
                 Header of collections.namedtuple
        label : collection
                Iterable collection of identifiers
        good : collection
                Iterable collection of selections
    
    Returns:

        val : list
              List of collections.namedtuples
    '''
    
    Tuple = collections.namedtuple(name, header)
    retvals = []
    
    if label is not None:
        if hasattr(label, 'ndim'):
            n = label.shape[1] if label.ndim > 1 else 1
        else:
            n = len(label[1]) if isinstance(label, list) or isinstance(label, tuple) else 1
        n += values.shape[1] if values.ndim > 1 else 1
        if good is not None: n += 1
        cat_label = len(Tuple._fields) != n
    if label is not None:
        for i in xrange(len(label)):
            vals = []
            if cat_label:
                try: id = "/".join([str(v) for v in label[i]])
                except: id = label[i]
                vals.append(id)
            else:
                try: vals.extend(label[i])
                except: vals.append(label[i])
            if good is not None: vals.append(good[i])
            try: vals.extend(values[i])
            except: vals.append(values[i])
            retvals.append(Tuple._make(vals))
    else:
        for val in values:
            try: retvals.append(Tuple._make(val))
            except: retvals.append(Tuple._make([val]))
    return retvals

def convert(val):
    '''Try to convert string value to numeric
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> convert("2.0")
    2
    >>> convert("2.1")
    2.1
    
    Args:
    
        val : string
              Value for conversion
    
    Returns:

        val : numeric
              Numeric (float or int) converted from string
    '''
    
    if val == '-': return None
    try: val = int(val)
    except:
        try: 
            val = float(val)
            if is_float_int(val): 
                val = int(val)
        except: pass
    return val

def parse_header(filename, header=None):
    ''' Parse a header specified at the end of the given filename
    
    This function takes a header at the end of a filename, converts it
    to a list of strings and returns the list.
    
    The filename and header must be separated by an equal sign, and each
    header elements must be separated by either: 
    ',', ';', or a '/' ('\' on windows).
    
    Example usage of the parse header function: 
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> filename1='/path/to/file/filename=header1,header2,header3'
    >>> parse_header(filename1)
    ('/path/to/file/filename', ['header1', 'header2', 'header3'])
    >>> filename2='/path/to/file/filename'
    >>> default_header=["field1", "field2", "field3"]
    >>> parse_header(filename2, default_header)
    ('/path/to/file/filename', ['field1', 'field2', 'field3'])
    
    Args:
    
        val : string
              Filename with header to parse
        header : list
              List of strings describing a header
    
    Returns:

        val : str
              New filename 
        header : list
                 List of strings describing the header
    '''
    
    if filename.find('=') != -1: 
        filename, header = filename.split('=', 1)
    elif header is None: header = []
    if isinstance(header, str):
        for sep in __header_seperators: header = header.replace(sep, " ")
        header = header.split()
        if isinstance(header, str): 
            header = [header] if header != "" else []
    if len(header) > 0 and header[0].find(':') != -1:
        header = dict([h.split(':', 1) for h in header])
    return filename, header

def create_id(objid, fileid):
    '''Create a new id from an object id and a file id
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> create_id('1', '2')
    "2/1"
    
    Args:
    
        objid : integer
              ID of the object to be converted to a string
        fileid : integer
              ID of the file to be converted to a string
    
    Returns:

        val : string
              Concatenated string identifier separated by an '/'
    '''
    
    if fileid is None: return str(object_id(objid))
    return str(file_id(fileid))+"/"+str(object_id(objid))

def split_id(id, numeric=False):
    '''Split the ID string into two individual IDs
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> split_id("2/1")
    ['2', '1']
    
    Args:
    
        id : string
             String ID containing two IDs separated by an '/'
    
    Returns:

        file_id : str
                  File ID
        object_id : str
                    Object ID
    '''
    
    ids = id.replace('/', ' ').replace(':', ' ').replace(',', ' ').replace('@', ' ').split()
    if numeric: ids = [int(i) for i in ids]
    return ids

def file_id(id):
    '''Extract the file id from a full string id
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> file_id("2/1")
    2
    >>> file_id("1")
    1
    
    Args:
    
        id : id-like object
             String full ID or integer partial ID
    
    Returns:

        val : integer
              Integer ID
    '''
    
    try:
        try:
            return int(float(id))
        except:
            return int(float(split_id(id)[0]))
    except:
        logging.error("Failed to split: %s"%(str(id)))
        raise

def object_id(id):
    '''Extract the object id from a full string id
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> object_id("2/1")
    1
    >>> object_id("1")
    1
    
    Args:
    
        id : id-like object
             String full ID or integer partial ID
    
    Returns:
    
        val : integer
              Integer ID
    '''
    
    try:
        try:
            return int(float(id))
        except:
            return int(float(split_id(id)[1]))
    except:
        logging.error("Failed to split: %s"%(str(id)))
        raise

def has_file_id(val):
    '''Test if ID, value or collection has a file ID
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> has_file_id("2/1")
    True
    >>> has_file_id("1")
    False
    >>> has_file_id(["2/1"])
    True
    >>> TestTuple = collections.namedtuple("TestTuple", "id,select")
    >>> has_file_id(TestTuple("1", 0))
    False
    
    Args:
    
        val : object
             ID, value or collection
    
    Returns:

        val : bool
              True if ID is not an integer
    '''
    
    if isinstance(val, tuple):
        try:
            return has_file_id(val.id)
        except: 
            try:return has_file_id(val.rlnImageName)
            except: return False
    elif isinstance(val, list):
        return has_file_id(val[0])
    else:
        try: float(val)
        except: return True
        else: return False

def get_header(value, key=None):
    '''Get the header of a named tuple or collection of named tuples
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple = collections.namedtuple("TestTuple", "id,select")
    >>> get_header(TestTuple("1", 0))
    ('id', 'select')
    >>> get_header([TestTuple("1", 0)])
    ('id', 'select')
    >>> get_header(TestTuple("1", 0), "id")
    0
    
    Args:

        value : object
                Namedtuple or collection of collections.namedtuples
        key : str, optional
              If not None, return index of header column
    
    Returns:
    
        val1 : tuple
              If key is not specified, tuple of strings describing a header
        val2 : integer
               If key is specified, index of column
    '''
    
    if isinstance(value, dict): return get_header(value[value.keys()[0]], key)
    if isinstance(value, list) and not isinstance(value[0], str): return get_header(value[0], key)
    if key is not None:
        try:    return int(key)
        except: 
            if hasattr(value, "_fields"): value = list(value._fields)
            try: return value.index(key)
            except: raise FormatUtilityError, "Cannot find key in collections.namedtuple: "+str(key)
    return value._fields

def has_field(val, key):
    ''' Test if the collections.namedtuple or collection of collections.namedtuples has the specific field
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> has_field([Select(id=1)], 'id')
    True
    
    Args:
    
        val : collections.namedtuple
              Value to test
        key : str
              Name of the field
    
    Returns:
    
        ret : bool
              True if val has field of name key
    '''
    
    try: get_header(val, key)
    except: return False
    else: return True

def map_object_list(vals, key="id"):
    '''Map the list of named tuples to a dictionary
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple = collections.namedtuple("TestTuple", "id,select")
    >>> testlist = [TestTuple(1,1), TestTuple(20,1)]
    >>> map_object_list(testlist)
    {1: TestTuple(id=1, select=1), 20: TestTuple(id=20, select=1)}
    
    Args:

        vals : list
               List of values
        key : index-like object, optional
              Column integer or string to map
    
    Returns:
    
        val : dict
               Dictionary of mapped values
    '''
    
    idx = get_header(vals, key)
    try:
        object_id(vals[0][idx])
    except:
        def pair1(idx, t): return t[idx], t
        pair=pair1
    else:
        def pair2(idx, t): return object_id(t[idx]), t
        pair=pair2
    return dict(map(functools.partial(pair, idx), vals))

def map_file_list(vals, replace=False, key="id"):
    '''Map the list of named tuples to a dictionary
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple = collections.namedtuple("TestTuple", "id,select")
    >>> testlist = [TestTuple("1/1",1), TestTuple("20/1",1)]
    >>> map_file_list(testlist)
    collections.defaultdict(<type 'list'>, {1: [TestTuple(id='1/1', select=1)], 20: [TestTuple(id='20/1', select=1)]})
    
    Args:

        vals : list
               List of values
        replace : bool, optional
                  If True, script the file id form the object
        key : index-like object, optional
              Column integer or string to map
    
    Returns:
    
        val : dict
               Dictionary of mapped values
    '''
    
    idx = get_header(vals, key)
    d = collections.defaultdict(list)
    if replace:
        for v in vals:
            d[file_id(v[idx])].append(v._replace(id=object_id(v[idx])))
    else:
        for v in vals:
            d[file_id(v[idx])].append(v)
    return d

def map_list(vals, key="id", replace=True):
    '''Map the list of named tuples to a dictionary
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple = collections.namedtuple("TestTuple", "id,select")
    >>> testlist = [TestTuple("1/1",1), TestTuple("1/2",0), TestTuple("20/1",1)]
    >>> map_list(testlist)
    collections.defaultdict(<type 'list'>, {1: {1: TestTuple(id='1/1', select=1), 2: TestTuple(id='1/2', select=0)}, 20: {1: TestTuple(id='20/1', select=1)}})
    
    Args:

        vals : list
               List of values
        key : index-like object, optional
              Column integer or string to map
        replace : bool
                  If True, replace the id of the output dict 
                  with the object id
    
    Returns:
    
        val : dict
               Dictionary of mapped values
    '''
    
    idx = get_header(vals, key)
    d = collections.defaultdict(list)
    if replace:
        for v in vals:
            d[file_id(v[idx])].append(v._replace(id=object_id(v[idx])))
    else:
        for v in vals:
            d[file_id(v[idx])].append(v)
    for k in d.iterkeys():
        d[k] = map_object_list(d[k], key)
    return d

def concat_tuple(t1, t2, NamedTuple):
    '''Concatenate two collections.namedtuples
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple1 = collections.namedtuple("TestTuple1", "id,select")
    >>> TestTuple2 = collections.namedtuple("TestTuple2", "id,peak")
    >>> CatTuple = collections.namedtuple("CatTuple", "id,select,peak")
    
    >>> concat_tuple(TestTuple1(1, 1), TestTuple2(1,0.9), CatTuple)
    CatTuple(id=1, select=1, peak=0.90)
    
    Args:

        t1 : collections.namedtuple
             First collections.namedtuple
        t2 : collections.namedtuple
             Second collections.namedtuple
        NamedTuple : class
                     Class of collections.namedtuple
    
    Returns:
    
        val : collections.namedtuple
              Concatenated collections.namedtuple
    '''
    
    vals = []
    if t2 is None:
        for h in NamedTuple._fields: 
            vals.append(getattr(t1, h) if hasattr(t1, h) else 0)
    else:
        for h in NamedTuple._fields:
            if h == "id":  vals.append(getattr(t1, h))
            else: vals.append(getattr(t2, h) if hasattr(t2, h) else getattr(t1, h))
    return NamedTuple._make(vals)

def stack(tlist1, tlist2, classname="StackTuple"):
    '''Stack two lists of tuples into a single tuple
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple1 = collections.namedtuple("TestTuple1", "id,select")
    >>> TestTuple2 = collections.namedtuple("TestTuple2", "id,peak")
    >>> testlist1 = [TestTuple1(2,0)]
    >>> testlist2 = [TestTuple1(2,0.5)]
    >>> stack(testlist1, testlist2)
    [StackTuple(id=2, select=0.5)]
    
    Args:

        tlist1 : container
                 List or dictionary containing collections.namedtuples
        tlist2 : collections.namedtuple
                 List or dictionary containing collections.namedtuples
        classname : string, optional
                    Name of collections.namedtuple class
    
    Returns:
    
        val : list
              List of collections.namedtuples
    '''
    
    if len(tlist1) == 0: return tlist2
    NamedTuple = collections.namedtuple(classname, ",".join(set(get_header(tlist1)+get_header(tlist2))))
    if not isinstance(tlist2, dict): tlist2 = map_object_list(tlist2)
    def stack_tuple(t):
        try: t2 = tlist2.get(object_id(t.id), None)
        except:
            logging.error("Problem stacking: "+str(t))
            raise
        return concat_tuple(t, t2, NamedTuple)
    if isinstance(tlist1, dict): tlist1 = tlist1.values()
    return map(functools.partial(stack_tuple), tlist1)
    
def column_offsets(vals, column):
    '''Get the column offsets of a header (or list of headers) from the specified named tuple (or list of named tuples).
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple1 = collections.namedtuple("TestTuple1", "id,select")
    >>> column_offsets([TestTuple1(2,0)], "select")
    1
    
    Args:

        vals : object
                 A collections.namedtuple (or collection of collections.namedtuples) with a header
        column : object
                 Columns to search for: Integer, string or list of integers or strings
    
    Returns:
    
        val : int or list
              Column offset or list of column offsets
    '''
    
    header = list(get_header(vals))
    if isinstance(column, list):
        return [get_header(header, col) for col in column]
    else:
        return get_header(header, column)

def flatten(values):
    ''' Flatten a collection of collection of collections.namedtuples

    >>> from arachnid.core.metadata.format_utility import *
    >>> TestTuple1 = collections.namedtuple("TestTuple1", "id,select")
    >>> flatten([TestTuple1(2,0)])
    [TestTuple1(id=2, select=0)]
    >>> flatten([[TestTuple1(2,0)],[TestTuple1(3,0)]])
    [TestTuple1(id=2, select=0), TestTuple1(id=3, select=0)]
    >>> flatten({1: [TestTuple1(2,0)], 2: [TestTuple1(3,0)]})
    [TestTuple1(id=2, select=0), TestTuple1(id=3, select=0)]
    
    Args:

        values : collection
                 A collection of collections of collections.namedtuples
    
    Returns:
    
        val : list
              List of collections.namedtuples
    '''
    
    if isinstance(values, dict): values = values.values()
    if len(values) > 0:
        if isinstance(values[0], dict):
            tmp = values
            values = []
            for t in tmp: values.extend(t.values())
        elif isinstance(values[0], list):
            tmp = values
            values = []
            for t in tmp: values.extend(t)
    return values

def order(values, index, keep_old=False):
    ''' Order values in a list using the ordered indices
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> order([TestTuple1(id=2, select=0), TestTuple1(id=3, select=1)], (1,0))
    [TestTuple1(id=1, select=1), TestTuple1(id=2, select=0)]
    
    Args:
    
        values : list
                 List to reorder
        index : array
                Array of sorted indices
        keep_old : bool
                   If True, maintain the old id, otherwise create a new
                   id based on the order
    
    Returns:
            
        vals : list
               Ordered list   
    '''
    
    vals = []
    if keep_old:
        header = ",".join(values[0]._fields)+",oldid"
        Tuple = collections.namedtuple('OrderTuple', header)
        for id, i in enumerate(index):
            old = values[i]._asdict()
            old['id'] = id+1
            vals.append(Tuple(oldid=values[i].id, **old))
    else:
        for id, i in enumerate(index):
            vals.append( values[i]._replace(id=id+1) )
    return vals

def add_file_id(values, fid):
    ''' Add a micrograph id to the id-field of each value in a list, in place
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> add_file_id([TestTuple1(id=2, select=0), TestTuple1(id=3, select=1)], 10)
    [TestTuple1(id='10/2', select=0), TestTuple1(id='10/3', select=1)]
    
    Args:
    
        values : list
                 List of collections.namedtuples to alter, in place
        fid : int
              Micrograph id
    
    Returns:
    
        values : list
                 List with replaced ids
    '''
    
    if not has_file_id(values):
        values = flatten(values)
        for i in xrange(len(values)):
            values[i] = values[i]._replace(id=create_id(values[i].id, fid))
    return values

def renumber(values):
    '''Renumber the ids in a list of values
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> renumber([TestTuple1(id=2, order=1), TestTuple1(id=4, order=2), TestTuple1(id=1, order=3)])
    [TestTuple1(id=1, order=3), TestTuple1(id=2, order=1), TestTuple1(id=3, order=2)]
    
    Args:

        values : list
                 List of values
    
    Returns:
    
        output : list
                 List of output values
    '''
    
    output = flatten(values)
    idx = get_header(output, 'id')
    output.sort(key=operator.itemgetter(idx))
    for i in xrange(len(output)):
        output[i] = output[i]._replace(id=i+1)
    return output

def fileid(fileset):
    ''' Extract a single filename from the set
    
    >>> from arachnid.core.metadata.format_utility import *
    >>> fileid([TestTuple1(id='10/2', select=0), TestTuple1(id='10/3', select=1)], 10)
    '10'
    
    .. deprecated:: 0.1.3
    
    Args:
        
        fileset : object
                  Tuple, list or string describing the file names
    
    Returns:
    
        val : str
              Filename ID
    '''
    
    if isinstance(fileset, list):  fileset = fileset[0]
    if isinstance(fileset, tuple): fileset = fileset[0]
    if isinstance(fileset, list):  fileset = fileset[0]
    return fileset



            

