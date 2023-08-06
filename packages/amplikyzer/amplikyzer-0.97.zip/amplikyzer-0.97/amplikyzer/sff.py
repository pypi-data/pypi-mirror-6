"""
sff module 
provides a class SFFFile for 454/IonTorrent .sff files
(c) Sven Rahmann, 2011 -- 2012

Format documentation is at
http://www.ncbi.nlm.nih.gov/Traces/trace.cgi?cmd=show&f=formats&m=doc&s=format

"""

from struct import calcsize
from struct import unpack
from collections import Counter


class FormatError(Exception):
    pass

def _process_padding(f,p):
    if not (0 <= p < 8):
        raise FormatError("Padding mismatch, padding="+str(p))
    padder = f.read(p)
    if padder.count(b'\0') != p:
        raise FormatError("Padding seems to contain data")

def _fread(f, fmt):
    b = calcsize(fmt)
    data = f.read(b)
    if len(data) < b:
        raise FormatError("chunk for "+fmt+" too short: "+str(len(data))+"/"+str(b))
    return unpack(fmt,data)


class SFFFile():
    _MAGIC = 0x2E736666

    def __init__(self, filename):
        self.filename = filename
        with open(filename, mode="rb") as f:
            self._set_info_from_header(f)

    def _set_info_from_header(self,f):
        """read the sff header and store its information in self"""
        _FIXEDLEN = 31
        # Read file header (constant part), length 31 bytes, 9 fields
        # big endian encdoing        >
        # magic_number               I  == _MAGIC
        # version                    4B == (0,0,0,1)
        # index_offset               Q  
        # index_length               I
        # number_of_reads            I
        # header_length              H  divisble by 8
        # key_length                 H
        # number_of_flows_per_read   H
        # flowgram_format_code       B == 1
        headerformat = '>I4BQIIHHHB'
        assert calcsize(headerformat) == _FIXEDLEN
        (magic_number,
            ver0, ver1, ver2, ver3,
            index_offset, index_length,
            number_of_reads,
            header_length,
            key_length,
            number_of_flows_per_read,
            flowgram_format_code) = _fread(f,headerformat)
        if magic_number != SFFFile._MAGIC:
            raise FormatError("Magic number is {} instead of {}").format(magic_number, _MAGIC)
        if (ver0, ver1, ver2, ver3) != (0, 0, 0, 1):
            raise FormatError("Unsupported .sff version ({}.{}.{}.{})".format(ver0, ver1, ver2, ver3))
        if (index_offset!=0) ^ (index_length!=0):
            raise FormatError("Index offset is {}, but length is {}".format(index_offset,index_length))
        if (index_offset % 8 != 0) or (index_length % 8 != 0):
            #raise FormatError("Index (offset, length) must be divisible by 8"+str(index_offset)+","+str(index_length))
            pass
        if header_length %8 != 0:
            raise FormatError("Header length must be divisible by 8, but is {}".format(header_length))
        if flowgram_format_code != 1:
            raise FormatError("Flowgram format code {} not supported".format(flowgram_format_code))
        # Read variable part of header:
        # flow_chars     {number_of_flows_per_read}s
        # key_sequence   {key_length}s
        flow_chars = f.read(number_of_flows_per_read)
        key_sequence = f.read(key_length)
        # padding        *B
        padding = header_length - number_of_flows_per_read - key_length - _FIXEDLEN
        _process_padding(f,padding)
        # set attributes:
        self.magic_number = magic_number
        self.version = (ver0, ver1, ver2, ver3)
        self.has_index = (index_offset != 0) and (index_length != 0)
        self.index_offset = index_offset
        self.index_length = index_length
        self.number_of_reads = number_of_reads
        self.header_length = header_length
        self.key_sequence = key_sequence.decode()  # string
        self.number_of_flows_per_read = number_of_flows_per_read
        self.flow_chars = flow_chars.decode()  # string
        self.reverse_flow_chars = "".join(self.flow_chars[::-1])
        self.flowgram_format_code = flowgram_format_code

    # generator function to iterate over all reads
    def reads(self):
        """yields each read in this .sff file as a Read object."""
        header_length = self.header_length
        with open(self.filename, mode="rb") as f:
            f.read(header_length)
            fpos = header_length
            checkindex = self.has_index
            for r in range(self.number_of_reads):
                assert(fpos % 8 == 0), "file position {} not divisible by 8".format(fpos)
                if checkindex and fpos == self.index_offset:
                    f.read(index_length)
                    fpos += index.length
                    checkindex = False
                read = self._next_read(f,r)
                yield read
                
    def _next_read(self, f, readindex):
        """reads the next read record from an open .sff file f"""
        # Read fixed part of read header, 7 fields
        # read_header_length     H
        # name_length            H
        # seq_len                I
        # clip_qual_left         H
        # clip_qual_right        H
        # clip_adapter_left      H
        # clip_adapter_right     H
        header_fmt  = ">HHIHHHH"
        (read_header_length,
         name_length,
         seq_len,
         clip_qual_left, clip_qual_right,
         clip_adapter_left, clip_adapter_right) = _fread(f,header_fmt)
        # check format
        expected = ((16 + name_length + 7)//8)*8
        if read_header_length != expected:
            raise FormatError("read header length should be 16 + name length, rounded up mod 8")
        # name                 c * name_length
        # padding              B * [to fill] 
        name_fmt = ">"+str(name_length)+"s"
        (namebytes,) = _fread(f, name_fmt)
        name = namebytes.decode()
        padding = read_header_length - (16 + name_length)
        _process_padding(f,padding)
        # flowgram_values      H * nflows  [type may differ with future formats]
        # flow_index_per_base  B * seq_len
        # bases                c * seq_len
        # quality_scores       B * seq_len
        # padding              B * [to fill]
        datatypes = ".H"
        flow_fmt = ">"+str(self.number_of_flows_per_read) + datatypes[self.flowgram_format_code]
        byte_fmt = ">"+str(seq_len)+"B"
        char_fmt = ">"+str(seq_len)+"s"
        flowgram_values = _fread(f,flow_fmt)
        flow_index_per_base = _fread(f,byte_fmt)
        (bases,) = _fread(f,char_fmt)
        quality_scores = _fread(f,byte_fmt)        
        datalen = sum(map(calcsize,(flow_fmt,byte_fmt,char_fmt,byte_fmt)))
        padding = (-datalen) % 8
        _process_padding(f,padding)
        r = Read(readindex, name, self,  # self is the current sff file
                 clip_qual_left, clip_qual_right, clip_adapter_left, clip_adapter_right,
                 flowgram_values, bases, flow_index_per_base, quality_scores)
        return r

class Read():
    """represents a flowgram read by the following attributes:
    - index: int, 0-based running number of the read in the sff file
    - name: bytes, a unique id for the read
    - sff_origin: SFFFile, from which the read was obtained
    - flowvalues: tuple of ints
    - flowchars:  string, usually 'TACG'*n for some n
    - qual: tuple of ints, quality values (10log10-representation)
    - clip: 4-tuple with clipping information
    - key: bytes, the key sequence (usually b'TCAG')
    - bases: bytes, the 454-converted sequence representation of the flowvalues
    - flow_index_per_base: tuple of ints
    """
    def __init__(self, index, name, sff_origin,
                 clip_qual_left, clip_qual_right, clip_adapter_left, clip_adapter_right,
                 flowgram_values, bases, flow_index_per_base, quality_scores):
        self.index = index
        self.name = name
        self.sff = sff_origin
        self.clip = dict(ql=clip_qual_left, qr=clip_qual_right,
                         al=clip_adapter_left, ar=clip_adapter_right)
        self.flowchars = sff_origin.flow_chars
        self.rflowchars = sff_origin.reverse_flow_chars
        self.flowvalues = flowgram_values
        #self.intensities = tuple(v/100.0 for v in flowgram_values)
        self.key = sff_origin.key_sequence  # string
        # the following fields are in "base-space" (length depends on read)
        self.bases = bases
        self.flow_index_per_base = flow_index_per_base
        self.qual = quality_scores


#############################################################################
# END

information = """
SFF was designed by 454 Life Sciences, Whitehead Institute for Biomedical Research and Sanger Institute.

This document describes proposed changes which will allow the Trace Archive to efficiently incorporate data generated in formats such as those used by the 454 Life Sciences' system.

The definition of a Standard Flowgram Format (SFF), similar to the SCF format, to hold the "trace" data for 454 reads

The proposed SFF file format is a container file for storing one or many 454 reads. 454 reads differ from standard sequencing reads in that the 454 data does not provide individual base measurements from which basecalls can be derived. Instead, it provides measurements that estimate the length of the next homopolymer stretch in the sequence (i.e., in "AAATGG", "AAA" is a 3-mer stretch of A's, "T" is a 1-mer stretch of T's and "GG" is a 2-mer stretch of G's). A basecalled sequence is then derived by converting each estimate into a homopolymer stretch of that length and concatenating the homopolymers.

The file format consists of three sections, a common header section occurring once in the file, then for each read stored in the file, a read header section and a read data section. The data in each section consists of a combination of numeric and character data, where the specific fields for each section are defined below. The sections adhere to the following rules:

    The standard Unix types uint8_t, uint16_t, uint32_t and uint64_t are used to define 1, 2, 4 and 8 byte numeric values.
    All multi-byte numeric values are stored using big endian byteorder (same as the SCF file format).
    All character fields use single-byte ASCII characters.
    Each section definition ends with an "eight_byte_padding" field, which consists of 0 to 7 bytes of padding, so that the length of each section is divisible by 8 (and hence the next section is aligned on an 8-byte boundary).



Common Header Section

The common header section consists of the following fields:
    magic_number uint32_t
    version char[4]
    index_offset uint64_t
    index_length uint32_t
    number_of_reads uint32_t
    header_length uint16_t
    key_length uint16_t
    number_of_flows_per_read uint16_t
    flowgram_format_code uint8_t
    flow_chars char[number_of_flows_per_read]
    key_sequence char[key_length]
    eight_byte_padding uint8_t[*]

where the following properties are true for these fields:

    The magic_number field value is 0x2E736666, the uint32_t encoding of the string ".sff"
    The version number corresponding to this proposal is 0001, or the byte array "\0\0\0\1".
    The index_offset and index_length fields are the offset and length of an optional index of the reads in the SFF file. If no index is included in the file, both fields must be 0.
    The number_of_reads field should be set to the number of reads stored in the file.
    The header_length field should be the total number of bytes required by this set of header fields, and should be equal to "31 + number_of_flows_per_read + key_length" rounded up to the next value divisible by 8.
    The key_length and key_sequence fields should be set to the length and nucleotide bases of the key sequence used for these reads.
        Note: The key_sequence field is not null-terminated.
    The number_of_flows_per_read should be set to the number of flows for each of the reads in the file.
    The flowgram_format_code should be set to the format used to encode each of the flowgram values for each read.
        Note: Currently, only one flowgram format has been adopted, so this value should be set to 1.
        The flowgram format code 1 stores each value as a uint16_t, where the floating point flowgram value is encoded as "(int) round(value * 100.0)", and decoded as "(storedvalue * 1.0 / 100.0)".
    The flow_chars should be set to the array of nucleotide bases ('A', 'C', 'G' or 'T') that correspond to the nucleotides used for each flow of each read. The length of the array should equal number_of_flows_per_read.
        Note: The flow_chars field is not null-terminated.
    If any eight_byte_padding bytes exist in the section, they should have a byte value of 0.

If an index is included in the file, the index_offset and index_length values in the common header should point to the section of the file containing the index. To support different indexing methods, the index section should begin with the following two fields:

    index_magic_number uint32_t
    index_version char[4]

and should end with an eight_byte_padding field, so that the length of the index section is divisible by 8. The format of the rest of the index section is specific to the indexing method used. The index_length given in the common header should include the bytes of these fields and the padding.

Note: Currently, there are no officially supported indexing formats, however support for the io_lib hash table indexing and a simple sorted list indexing should be developed shortly.




Read Header Section

The rest of the file contains the information about the reads, namely number_of_reads entries consisting of read header and read data sections. The read header section consists of the following fields:

    read_header_length uint16_t
    name_length uint16_t
    number_of_bases uint32_t
    clip_qual_left uint16_t
    clip_qual_right uint16_t
    clip_adapter_left uint16_t
    clip_adapter_right uint16_t
    name char[name_length]
    eight_byte_padding uint8_t[*]

where these fields have the following properties:

    The read_header_length should be set to the length of the read header for this read, and should be equal to "16 + name_length" rounded up to the next value divisible by 8.
    The name_length and name fields should be set to the length and string of the read's accession or name.
        Note: The name field is not null-terminated.
    The number_of_bases should be set to the number of bases called for this read.
    The clip_qual_left and clip_adapter_left fields should be set to the position of the first base after the clipping point, for quality and/or an adapter sequence, at the beginning of the read. If only a combined clipping position is computed, it should be stored in clip_qual_left.
        The position values use 1-based indexing, so the first base is at position 1.
        If a clipping value is not computed, the field should be set to 0.
        Thus, the first base of the insert is "max(1, max(clip_qual_left, clip_adapter_left))".
    The clip_qual_right and clip_adapter_right fields should be set to the position of the last base before the clipping point, for quality and/or an adapter sequence, at the end of the read. If only a combined clipping position is computed, it should be stored in clip_qual_right.
        The position values use 1-based indexing.
        If a clipping value is computed, the field should be set to 0.
        Thus, the last base of the insert is "min( (clip_qual_right == 0 ? number_of_bases : clip_qual_right), (clip_adapter_right == 0 ? number_of_bases : clip_adapter_right) )".



Read Data Section

The read data section consists of the following fields:

    flowgram_values uint*_t[number_of_flows]
    flow_index_per_base uint8_t[number_of_bases]
    bases char[number_of_bases]
    quality_scores uint8_t[number_of_bases]
    eight_byte_padding uint8_t[*]

where the fields have the following properties:

    The flowgram_values field contains the homopolymer stretch estimates for each flow of the read. The number of bytes used for each value depends on the common header flowgram_format_code value (where the current value uses a uint16_t for each value).
    The flow_index_per_base field contains the flow positions for each base in the called sequence (i.e., for each base, the position in the flowgram whose estimate resulted in that base being called).
        These values are "incremental" values, meaning that the stored position is the offset from the previous flow index in the field.
        All position values (prior to their incremental encoding) use 1-based indexing, so the first flow is flow 1.
    The bases field contains the basecalled nucleotide sequence.
    The quality_scores field contains the quality scores for each of the bases in the sequence, where the values use the standard -log10 probability scale.


Computing Lengths and Scanning the File

The length of each read's section will be different, because of different length accession numbers and different length nucleotide sequences. However, the various flow, name and bases lengths given in the common and read headers can be used to scan the file, accessing each read's information or skipping read sections in the file. The following pseudocode gives an example method to scanning the file and accessing each read's data:

    Open the file and/or reset the file pointer position to the first byte of the file.
    Read the first 31 bytes of the file, confirm the magic_number value and version, then extract the number_of_reads, number_of_flows_per_read, flowgram_format_code, header_length, key_length, index_offset and index_length values.
        Convert the flowgram_format_code into a flowgram_bytes_per_flow value (currently with format_code 1, this value is 2 bytes).
    If the flow_chars and key_sequence information is required, read the next "header_length - 31" bytes, then extract that information. Otherwise, set the file pointer position to byte header_length.
    While the file contains more bytes, do the following:
        If the file pointer position equals index_offset, either read or skip index_length bytes in the file, processing the index if read.
        Otherwise,
            Read 16 bytes and extract the read_header_length, name_length and number_of_bases values.
            Read the next "read_header_length - 16" bytes to read the name.
            At this point, a test of the name field can be perform, to determine whether to read or skip this entry.
            Compute the read_data_length as "number_of_flows * flowgram_bytes_per_flow + 3 * number_of_bases" rounded up to the next value divisible by 8.
            Either read or skip read_data_length bytes in the file, processing the read data if the section is read.

"""
