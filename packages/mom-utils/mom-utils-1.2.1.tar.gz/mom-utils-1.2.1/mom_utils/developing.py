
from mom_utils.utils import harvest_namelist, check_namelist_exist
from mom_utils.utils import convert_inputnml_mom4_to_mom5
from mom_utils.mom4_namelist import nml_decode

basepath = "/Users/castelao/work/projects/mom_namelist/src"
inputpattern = ".*F90"
input_nml_path = "/Users/castelao/work/inpe/repos/exp_dev/exp/expgui/input.nml"
input_nml_path = "/Users/castelao/work/inpe/repos/exp_dev/exp/GT4i_R2/input.nml"

input_nml = nml_decode(open(input_nml_path).read())

print check_namelist_exist(basepath, input_nml)
input_nml = convert_inputnml_mom4_to_mom5(input_nml)
print check_namelist_exist(basepath, input_nml)

src_nml = harvest_namelist(basepath)


inputnml = convert_inputnml_mom4_to_mom5(inputnml)

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


MOM4p1 -> MOM5

mom4_to_mom5 = {
    #ocean_density_nml
    "linear_eos": "eos_linear",
    "ocean_vert_kpp_nml": "ocean_vert_kpp_mom4p1",
    #ocean_frazil_nml
    "freezing_temp_accurate": "freezing_temp_teos10",  # To reproduce, probably use freezing_temp_preteos10, but the best option might be freezing_temp_teos10
    #ocean_barotropic_nml
    "barotropic_time_stepping_mom4p0": "barotropic_time_stepping_A",
    "barotropic_time_stepping_mom4p1": "barotropic_time_stepping_B",
    "barotropic_pred_corr": False,
    "barotropic_leap_frog": False,
    #
    "ocean_vert_kpp_iow_nml": False,
    #
    "ocean_polar_filter_nml": False,
    #
    "ocean_time_filter_nml": False,
    }


out = inputnml.copy()

nmls = inputnml.keys()
for m in nmls:
    if m in mom4_to_mom5.keys():
        out[mom4_to_mom5[m]] = inputnml[m]
        del(out[m])
    elif type(inputnml[m]) == dict:
        for p in inputnml[m]:
            if p in mom4_to_mom5.keys():
                out[m][mom4_to_mom5[p]] = inputnml[m][p]
                del(out[m][p])

#text[43300:45300]
#print text[5150:5300]
