import time
import sys
import math
import os
import re


def spin(times, interval=1):
    SPIN = '|\\-/'
    i = 0
    while i <= times:
        sys.stdout.write("\r%s" % SPIN[i % len(SPIN)])
        sys.stdout.flush()
        time.sleep(interval)
        i += 1


def layout(n, factor=1):

    def divisors(num):
        result = []
        step = 1
        while step <= math.ceil(num / 2):
            if num % step == 0:
                result.append(step)
            step += 1
        result.append(num)
        return result

    possibilities = [(n / d, d) for d in divisors(n) if n / d >= d]
    possibilities.sort(key=lambda x: abs(float(n / x[1] ** 2) - factor))
    return possibilities[0]


def get_output_files(cfg):
    """

        Example
        cfg = {'data_path': '/Tupa/simulations/exp048/dataout',
               'filename_pattern': 'cgcm2.2_currents_.*\.nc'}
    """
    # Create files list
    filenames = [f for f in os.listdir(cfg['data_path'])
            if re.match(cfg['filename_pattern'], f)]
    filenames.sort()
    # Include the path to the files
    ncfpaths = [os.path.join(cfg['data_path'], f) for f in filenames]
    return ncfpaths


def extract_namelist(filename):
    """ Extract the namelist and its parameters form a FORTRAN file

        Something like:
        n = extract_namelist('path/to/ocean_solo.F90')
        n['namelist'] -> ocean_solo_nml
        n['parameters'] -> ['date_init', 'calendar', 'months', 'days',...]
    """
    text = open(filename).read()
    r = '''
    (?:namelist|NAMELIST)
    \ +
    #/\ ?(?P<namelist>\w+)\ ?/
    /(?P<namelist>\w+)/
    \ +
    (?P<parameters>
        (?:
            \w+
            .*&
            \s*
        )*
        (?:
            \w+
            .*
        )
        |
        (?:
            \ *
        )
        \s*
    )
    '''

    content_re = re.compile(r, re.VERBOSE)
    out = {}
    if re.search(content_re, text):
        for nml in re.finditer(content_re, text):
            tmp = nml.groupdict()
            if tmp['namelist'] not in out.keys():
                out[tmp['namelist']] = {}

            tmp['parameters'] = re.findall('(\w+),?', tmp['parameters'])
            out[tmp['namelist']] = tmp['parameters']
    return out


def make_file_list(inputdir, inputpattern):
    """ Search inputdir recursively for inputpattern
    """
    inputfiles = []
    for dirpath, dirnames, filenames in os.walk(inputdir):
        for filename in filenames:
            if re.match(inputpattern, filename):
                inputfiles.append(os.path.join(dirpath, filename))
    inputfiles.sort()
    return inputfiles


def harvest_namelist(basepath, filepattern=".*F90"):
    """ Harvest namelist and its parameters from a dir of F90 files

        input:
           basepath: The base path to the MOM source code
           filepattern: The filename pattern in regexp to consider.
               default is ".*F90"
    """
    filenames = make_file_list(basepath, filepattern)
    data = {}
    for filename in filenames:
        nml = extract_namelist(filename)
        for n in nml.keys():
            data[n] = nml[n]
    return data

def check_namelist_exist(src_path, input_nml_path):
    """ Check if all nml exist in the src

        It loads inputnml, an input.nml file, parse all namelists
          and check if they exist in the MOM5 src code at srcpath
    """
    from mom_utils.mom4_namelist import nml_decode
    input_nml = nml_decode(open(input_nml_path).read())

    src_nml = harvest_namelist(src_path)

    nonexitent = {}
    for nml in input_nml:
        if nml not in src_nml:
            nonexitent[nml] = input_nml[nml]
        elif input_nml[nml] is not None:
            for p in input_nml[nml]:
                if p not in src_nml[nml]:
                    if nml not in nonexitent:
                        nonexitent[nml] = {}
                    # Temporary solution, set as None
                    nonexitent[nml][p] = None

    return nonexitent
