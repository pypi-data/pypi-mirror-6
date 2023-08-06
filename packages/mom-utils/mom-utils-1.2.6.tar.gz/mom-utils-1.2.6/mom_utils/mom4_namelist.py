#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# vim: tabstop=4 shiftwidth=4 expandtab


import yaml
import re


def nml_decode(text):
    """ Decode a MOM's namelist as a YAML

        Input: A nml content as a string
        Output: A YAML object

        f = open('input.nml', 'r')
        nml = nml_decode(r.read())
    """
    text = re.sub("\t", " ", text)

    # dummy way to deal with comments. Need to improve it
    text = re.sub("\s*!.*\n", "\n", text)

    r_nml = r"""&
        (?P<namelist>\w+)\ *\n # namelist tag, like: ocean_model_nml
        (?P<parameters>(?:.*\n)*?)
        \s*/"""
    r_param = r"""
        (?P<parameter>
            \s*
            (?P<pname>\w+)  # The parameter name
            \ *=
            )
        \ *
        (?P<pvalue>        # The parameter value
            .*\n
            (?:\s*.*\n)*?       # Can be multiple lines
            #.*               # At least one line of value
            )# ,? \n          #
        (?=                  # Goes until:
            #(?:\s*\w+\ *=)   #   next line has a new parameter
            (?:\s*\w+\s*=)
            |
            $               #   or is the end of the namelist
            )
        """

    output = []
    for nml in re.finditer(r_nml, text, re.VERBOSE):
        nml = nml.groupdict()
        output.append("%s:\n" % nml['namelist'])
        for p in re.finditer(r_param, nml['parameters'], re.VERBOSE):
            p = p.groupdict()
            tmp = parse_nmlparameter(p['pvalue'])
            output.append("  %s: %s\n" % (p['pname'], tmp))
    textout = "".join(output)
    return yaml.safe_load(textout)

def parse_nmlparameter(pvalue):
    # Remove the last comma, spaces after and line break
    tmp = re.sub("(,?\s*)$", "", pvalue)
    if re.search('^\s*\.(?:(?:false)|(?:FALSE))\.\s*$', tmp):
        return False
    elif re.search('^\s*\.(?:(?:true)|(?:TRUE))\.\s*$', tmp):
        return True
    # BAD BAD temporary solution
    if re.search('("\w+",\s*)+', tmp):
        tmp = "[%s]" % tmp
    tmp = tmp.replace("\n", r"\n").replace('"', r'\"').replace("'", r"\'")
    return tmp

def yaml2nml(cfg, key_order=None):
    """
    """
    output = []
    keys = cfg.keys()

    if key_order:
        key_order = list(key_order)
        if set(key_order) <= set(keys):
            key_order += (set(keys) - set(key_order))
        else:
            raise KeyError
    else:
        key_order = sorted(keys)

    for k in key_order:
        output.append(" &%s\n" % k)
        if cfg[k] is not None:
            parameters = cfg[k].keys()
            parameters.sort()
            for kk in parameters:
                v = cfg[k][kk]
                if v is False:
                    v = '.FALSE.'
                elif v is True:
                    v = '.TRUE.'
                elif type(v) is list:
                    v = ", ".join(v).decode('string_escape')
                elif type(v) is str:
                    v = v.decode('string_escape')
                else:
                    try:
                        if abs(int(v) - float(v)) == 0:
                            v = int(v)
                        else:
                            v = float(v)
                    except ValueError:
                        try:
                            v = float(v)
                        except ValueError:
                            try:
                                v.split(',')[1]
                            except ValueError:
                                v = "'%s'" % v
                            except IndexError:
                                v = "'%s'" % v
                            else:
                                v = "%s" % v
                output.append("    %s = %s,\n" % (kk, v))
        output.append("/\n\n")
    return "".join(output)


# Under work.
#filename = "/Users/castelao/work/projects/INPE/repos/Modelos/MOM4p1/src/mom4p1/ocean_diag/ocean_drifters.F90"
#filename = "/Users/castelao/work/projects/INPE/repos/Modelos/MOM4p1/src/mom4p1/ocean_core/ocean_barotropic.F90"
#f = open(filename)
#text = f.read()
#f.close()

charref = re.compile(r"""
    namelist\ +/(?P<namelist>\w*)/   # Name of the namelist
    (?P<parameters>
      (?:
        (?:           # Along one line
          \t?\ *
          (\w+)       # The Parameter
          ,?          # Comma and space if there is more than one
        )+
        \ *\&\ *
        \s
      )+
    )
""", re.VERBOSE)

#charref = re.compile(r'''namelist\ /(?P<namelist>\w*)/\ (?P<parameters>.*?)[^\&\ *]$''', re.DOTALL)
#parameters = map(strip, parameters)
#parameters = parameters.replace('&', '').split(',')
#parameters = map(strip, parameters)

charref = re.compile(r"""
        .*\n\t.*
        """, re.VERBOSE)


#charref.search(text).groupdict()
