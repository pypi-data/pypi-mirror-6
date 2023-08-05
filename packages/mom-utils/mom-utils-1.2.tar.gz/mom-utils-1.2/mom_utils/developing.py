
from mom_utils.utils import harvest_namelist, check_namelist_exist
from mom_utils.mom4_namelist import nml_decode

basepath = "/Users/castelao/work/projects/mom_namelist/src"
inputpattern = ".*F90"
input_nml_path = "/Users/castelao/work/inpe/repos/exp_dev/exp/expgui/input.nml"
input_nml_path = "/Users/castelao/work/inpe/repos/exp_dev/exp/GT4i_R2/input.nml"

input_nml = nml_decode(open(input_nml_path).read())

src_nml = harvest_namelist(basepath)

check_namelist_exist(basepath, input_nml)

missing = {}
for nml in input_nml:
    if nml not in src_nml:
        missing[nml] = input_nml[nml]
    elif input_nml[nml] is not None:
        for p in input_nml[nml]:
            if p not in src_nml[nml]:
                if nml not in missing:
                    missing[nml] = {}
                # Temporary solution, set as None
                missing[nml][p] = None


#text[43300:45300]
#print text[5150:5300]
