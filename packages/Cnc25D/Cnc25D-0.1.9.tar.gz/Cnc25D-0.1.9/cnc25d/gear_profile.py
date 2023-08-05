# gear_profile.py
# generates a gear_profile and simulates it.
# created by charlyoleg on 2013/08/20
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.


"""
gear_profile.py is a parametric generator of gear-profiles.
You can use the gear-profile to create gearwheel, gearring or gearbar.
The function gear_profile() returns an format B outline that can be easily included in other scripts.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

# Python standard library
import math
import sys, argparse
#from datetime import datetime
#import os, errno
#import re
import Tkinter # to display the outline in a small GUI
import time # for time.sleep to help Tkinter to finish properly
# FreeCAD
import Part
#from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
from gear_profile_outline import *

################################################################
# module variable
################################################################
#gp_radian_epsilon = math.pi/1000
g1_rotation_speed = 1 # rad/s
speed_scale = 0.2 #1

################################################################
# gear_profile dictionary-constraint-arguments default values
################################################################

def gear_profile_dictionary_init(ai_variant=0):
  """ create and initiate a gear_profile_dictionary with the default value
  """
  r_gpd = {}
  ### first gear
  # general
  r_gpd['gear_type'] = 'e'
  r_gpd['gear_tooth_nb'] = 0
  r_gpd['gear_module'] = 0.0
  r_gpd['gear_primitive_diameter'] = 0.0
  r_gpd['gear_addendum_dedendum_parity'] = 50.0
  # tooth height
  r_gpd['gear_tooth_half_height'] = 0.0
  r_gpd['gear_addendum_height_pourcentage'] = 100.0
  r_gpd['gear_dedendum_height_pourcentage'] = 100.0
  r_gpd['gear_hollow_height_pourcentage'] = 25.0
  r_gpd['gear_router_bit_radius'] = 0.1
  # positive involute
  r_gpd['gear_base_diameter'] = 0.0
  r_gpd['gear_force_angle'] = 0.0
  r_gpd['gear_tooth_resolution'] = 2
  r_gpd['gear_skin_thickness'] = 0.0
  # negative involute (if zero, negative involute'] = positive involute)
  r_gpd['gear_base_diameter_n'] = 0.0
  r_gpd['gear_force_angle_n'] = 0.0
  r_gpd['gear_tooth_resolution_n'] = 0
  r_gpd['gear_skin_thickness_n'] = 0.0
  ### second gear
  # general
  r_gpd['second_gear_type'] = 'e'
  r_gpd['second_gear_tooth_nb'] = 0
  r_gpd['second_gear_primitive_diameter'] = 0.0
  r_gpd['second_gear_addendum_dedendum_parity'] = 0.0
  # tooth height
  r_gpd['second_gear_tooth_half_height'] = 0.0
  r_gpd['second_gear_addendum_height_pourcentage'] = 100.0
  r_gpd['second_gear_dedendum_height_pourcentage'] = 100.0
  r_gpd['second_gear_hollow_height_pourcentage'] = 25.0
  r_gpd['second_gear_router_bit_radius'] = 0.0
  # positive involute
  r_gpd['second_gear_base_diameter'] = 0.0
  r_gpd['second_gear_tooth_resolution'] = 0
  r_gpd['second_gear_skin_thickness'] = 0.0
  # negative involute (if zero, negative involute'] = positive involute)
  r_gpd['second_gear_base_diameter_n'] = 0.0
  r_gpd['second_gear_tooth_resolution_n'] = 0
  r_gpd['second_gear_skin_thickness_n'] = 0.0
  ### gearbar specific
  r_gpd['gearbar_slope'] = 0.0
  r_gpd['gearbar_slope_n'] = 0.0
  ### position
  # first gear position
  r_gpd['center_position_x'] = 0.0
  r_gpd['center_position_y'] = 0.0
  r_gpd['gear_initial_angle'] = 0.0
  # second gear position
  r_gpd['second_gear_position_angle'] = 0.0
  r_gpd['second_gear_additional_axis_length'] = 0.0
  ### portion
  r_gpd['portion_tooth_nb'] = 0
  r_gpd['portion_first_end'] = 0
  r_gpd['portion_last_end'] = 0
  ### output
  r_gpd['gear_profile_height'] = 10.0
  r_gpd['simulation_enable'] = False
  r_gpd['output_file_basename'] = ''
  #### optional
  r_gpd['args_in_txt'] = ''
  r_gpd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object', 'figure_param_info'
  ###### return
  return(r_gpd)

################################################################
# gear_profile argparse
################################################################

def gear_profile_add_argument(ai_parser, ai_variant=0):
  """ Add the argparse switches relative to the gear_profile
      This function intends to be used by the gear_profile_cli, gear_profile_self_test and also gearwheel, gearring, gearbar ...
      ai_variant let's you remove some arguments:
      0:all for gear_profile_cli() and gear_profile_self_test()
      1:restriction for gearwheel
      2:restriction for gearring
      3:restriction for gearbar
      4:restriction for gearlever
  """
  r_parser = ai_parser
  ### first gear
  # general
  if((ai_variant!=1)and(ai_variant!=2)and(ai_variant!=3)and(ai_variant!=4)):
    r_parser.add_argument('--gear_type','--gt', action='store', default='e', dest='sw_gear_type',
      help="Select the type of gear. Possible values: 'e', 'i', 'l'. Default: 'e'")
  if(ai_variant!=4):
    r_parser.add_argument('--gear_tooth_nb','--gtn', action='store', type=int, default=0, dest='sw_gear_tooth_nb',
      help="Set the number of teeth of the first gear_profile.")
    r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=0.0, dest='sw_gear_module',
      help="Set the module of the gear. It influences the gear_profile diameters.")
  r_parser.add_argument('--gear_primitive_diameter','--gpd', action='store', type=float, default=0.0, dest='sw_gear_primitive_diameter',
    help="If not zero, redefine the gear module to get this primitive diameter of the first gear_profile. Default: 0. If gearbar, it redefines the length.")
  r_parser.add_argument('--gear_addendum_dedendum_parity','--gadp', action='store', type=float, default=50.0, dest='sw_gear_addendum_dedendum_parity',
    help="Set the addendum / dedendum parity of the first gear_profile. Default: 50.0%%")
  # tooth height
  r_parser.add_argument('--gear_tooth_half_height','--gthh', action='store', type=float, default=0.0, dest='sw_gear_tooth_half_height',
    help="If not zero, redefine the tooth half height of the first gear_profile. Default: 0.0")
  r_parser.add_argument('--gear_addendum_height_pourcentage','--gahp', action='store', type=float, default=100.0, dest='sw_gear_addendum_height_pourcentage',
    help="Set the addendum height of the first gear_profile in pourcentage of the tooth half height. Default: 100.0%%")
  r_parser.add_argument('--gear_dedendum_height_pourcentage','--gdhp', action='store', type=float, default=100.0, dest='sw_gear_dedendum_height_pourcentage',
    help="Set the dedendum height of the first gear_profile in pourcentage of the tooth half height. Default: 100.0%%")
  r_parser.add_argument('--gear_hollow_height_pourcentage','--ghhp', action='store', type=float, default=25.0, dest='sw_gear_hollow_height_pourcentage',
    help="Set the hollow height of the first gear_profile in pourcentage of the tooth half height. The hollow is a clear space for the top of the teeth of the other gearwheel. Default: 25.0%%")
  r_parser.add_argument('--gear_router_bit_radius','--grr', action='store', type=float, default=0.1, dest='sw_gear_router_bit_radius',
    help="Set the router_bit radius used to create the gear hollow of the first gear_profile. Default: 0.1")
  # positive involute
  r_parser.add_argument('--gear_base_diameter','--gbd', action='store', type=float, default=0.0, dest='sw_gear_base_diameter',
    help="If not zero, redefine the base diameter of the first gear involute. Default: 0")
  r_parser.add_argument('--gear_force_angle','--gfa', action='store', type=float, default=0.0, dest='sw_gear_force_angle',
    help="If not zero, redefine the gear_base_diameter to get this force angle at the gear contact. Default: 0.0")
  r_parser.add_argument('--gear_tooth_resolution','--gtr', action='store', type=int, default=2, dest='sw_gear_tooth_resolution',
    help="It sets the number of segments of the gear involute. Default: 2")
  r_parser.add_argument('--gear_skin_thickness','--gst', action='store', type=float, default=0.0, dest='sw_gear_skin_thickness',
    help="Add or remove radial thickness on the gear involute. Default: 0.0")
  # negative involute (if zero, negative involute = positive involute)
  r_parser.add_argument('--gear_base_diameter_n','--gbdn', action='store', type=float, default=0.0, dest='sw_gear_base_diameter_n',
    help="If not zero, redefine the base diameter of the first gear negative involute. Default: 0")
  r_parser.add_argument('--gear_force_angle_n','--gfan', action='store', type=float, default=0.0, dest='sw_gear_force_angle_n',
    help="If not zero, redefine the negative_gear_base_diameter to get this force angle at the gear contact. Default: 0.0")
  r_parser.add_argument('--gear_tooth_resolution_n','--gtrn', action='store', type=int, default=0, dest='sw_gear_tooth_resolution_n',
    help="If not zero, it sets the number of segments of the gear negative involute. Default: 0")
  r_parser.add_argument('--gear_skin_thickness_n','--gstn', action='store', type=float, default=0.0, dest='sw_gear_skin_thickness_n',
    help="If not zero, add or remove radial thickness on the gear negative involute. Default: 0.0")
  ### second gear
  # general
  if((ai_variant!=2)and(ai_variant!=3)):
    r_parser.add_argument('--second_gear_type','--sgt', action='store', default='e', dest='sw_second_gear_type',
      help="Select the type of gear. Possible values: 'e', 'i', 'l'. Default: 'e'")
  r_parser.add_argument('--second_gear_tooth_nb','--sgtn', action='store', type=int, default=0, dest='sw_second_gear_tooth_nb',
    help="Set the number of teeth of the second gear_profile.")
  r_parser.add_argument('--second_gear_primitive_diameter','--sgpd', action='store', type=float, default=0.0, dest='sw_second_gear_primitive_diameter',
    help="If not zero, redefine the gear module to get this primitive diameter of the second gear_profile. Default: 0.0. If gearbar, it redefines the length.")
  r_parser.add_argument('--second_gear_addendum_dedendum_parity','--sgadp', action='store', type=float, default=0.0, dest='sw_second_gear_addendum_dedendum_parity',
    help="Overwrite the addendum / dedendum parity of the second gear_profile if different from 0.0. Default: 0.0%%")
  # tooth height
  r_parser.add_argument('--second_gear_tooth_half_height','--sgthh', action='store', type=float, default=0.0, dest='sw_second_gear_tooth_half_height',
    help="If not zero, redefine the tooth half height of the second gear_profile. Default: 0.0")
  r_parser.add_argument('--second_gear_addendum_height_pourcentage','--sgahp', action='store', type=float, default=100.0, dest='sw_second_gear_addendum_height_pourcentage',
    help="Set the addendum height of the second gear_profile in pourcentage of the tooth half height. Default: 100.0%%")
  r_parser.add_argument('--second_gear_dedendum_height_pourcentage','--sgdhp', action='store', type=float, default=100.0, dest='sw_second_gear_dedendum_height_pourcentage',
    help="Set the dedendum height of the second gear_profile in pourcentage of the tooth half height. Default: 100.0%%")
  r_parser.add_argument('--second_gear_hollow_height_pourcentage','--sghhp', action='store', type=float, default=25.0, dest='sw_second_gear_hollow_height_pourcentage',
    help="Set the hollow height of the second gear_profile in pourcentage of the tooth half height. The hollow is a clear space for the top of the teeth of the other gearwheel. Default: 25.0%%")
  r_parser.add_argument('--second_gear_router_bit_radius','--sgrr', action='store', type=float, default=0.0, dest='sw_second_gear_router_bit_radius',
    help="If not zero, overwrite the router_bit radius used to create the gear hollow of the second gear_profile. Default: 0.0")
  # positive involute
  r_parser.add_argument('--second_gear_base_diameter','--sgbd', action='store', type=float, default=0.0, dest='sw_second_gear_base_diameter',
    help="If not zero, redefine the base diameter of the second gear involute. Default: 0.0")
  r_parser.add_argument('--second_gear_tooth_resolution','--sgtr', action='store', type=int, default=0, dest='sw_second_gear_tooth_resolution',
    help="If not zero, it sets the number of segments of the second gear involute. Default: 0")
  r_parser.add_argument('--second_gear_skin_thickness','--sgst', action='store', type=float, default=0.0, dest='sw_second_gear_skin_thickness',
    help="Add or remove radial thickness on the gear involute. Default: 0.0")
  # negative involute (if zero, negative involute = positive involute)
  r_parser.add_argument('--second_gear_base_diameter_n','--sgbdn', action='store', type=float, default=0.0, dest='sw_second_gear_base_diameter_n',
    help="If not zero, redefine the base diameter of the second gear negative involute. Default: 0.0")
  r_parser.add_argument('--second_gear_tooth_resolution_n','--sgtrn', action='store', type=int, default=0, dest='sw_second_gear_tooth_resolution_n',
    help="If not zero, it sets the number of segments of the second gear negative involute. Default: 0")
  r_parser.add_argument('--second_gear_skin_thickness_n','--sgstn', action='store', type=float, default=0.0, dest='sw_second_gear_skin_thickness_n',
    help="If not zero, add or remove radial thickness on the gear negative involute. Default: 0.0")
  ### gearbar specific (used by gearbar1 and gearbar2)
  if(ai_variant!=2):
    r_parser.add_argument('--gearbar_slope','--gbs', action='store', type=float, default=0.0, dest='sw_gearbar_slope',
      help="if not zero, set the tooth slope angle for the gearbar. Default 0.0")
    r_parser.add_argument('--gearbar_slope_n','--gbsn', action='store', type=float, default=0.0, dest='sw_gearbar_slope_n',
      help="if not zero, set the tooth negative slope angle for the gearbar. Default 0.0")
  ### position
  # first gear position
  if(ai_variant!=4):
    r_parser.add_argument('--center_position_x','--cpx', action='store', type=float, default=0.0, dest='sw_center_position_x',
      help="Set the x-position of the first gear_profile center. Default: 0.0")
    r_parser.add_argument('--center_position_y','--cpy', action='store', type=float, default=0.0, dest='sw_center_position_y',
      help="Set the y-position of the first gear_profile center. Default: 0.0")
    r_parser.add_argument('--gear_initial_angle','--gia', action='store', type=float, default=0.0, dest='sw_gear_initial_angle',
      help="Set the gear reference angle (in Radian). Default: 0.0")
  # second gear position
  r_parser.add_argument('--second_gear_position_angle','--sgpa', action='store', type=float, default=0.0, dest='sw_second_gear_position_angle',
    help="Angle in Radian that sets the postion on the second gear_profile. Default: 0.0")
  r_parser.add_argument('--second_gear_additional_axis_length','--sgaal', action='store', type=float, default=0.0, dest='sw_second_gear_additional_axis_length',
    help="Set an additional value for the inter-axis length between the first and the second gear_profiles. Default: 0.0")
  ### portion
  if((ai_variant!=1)and(ai_variant!=2)and(ai_variant!=4)):
    r_parser.add_argument('--cut_portion','--cp', action='store', nargs=3, type=int, default=(0, 0, 0), dest='sw_cut_portion',
      help="(N, first_end, last_end) If N>1, cut a portion of N tooth ofthe gear_profile. first_end and last_end defines in details where the profile stop (0: slope-top, 1: top-middle, 2: slope-bottom, 3: hollow-middle). Default: (0,0,0)")
  ### output
  # gear_profile extrusion (currently only linear extrusion is possible)
  if(ai_variant!=4):
    r_parser.add_argument('--gear_profile_height','--gwh', action='store', type=float, default=10.0, dest='sw_gear_profile_height',
      help="Set the height of the linear extrusion of the first gear_profile. Default: 10.0")
  # simulation
  r_parser.add_argument('--simulation_enable','--se', action='store_true', default=False, dest='sw_simulation_enable',
    help='It display a Tk window where you can observe the gear running. Check with your eyes if the geometry is working.')
  # output file : added later
  #r_parser.add_argument('--output_file_basename','--ofb', action='store', default='', dest='sw_output_file_basename',
  #  help="If not  the empty_string (the default value), it outputs the (first) gear in file(s) depending on your argument file_extension: .dxf uses mozman dxfwrite, .svg uses mozman svgwrite, no-extension uses FreeCAD and you get .brep and .dxf")
  # return_type
  #r_parser.add_argument('--return_type','--rt', action='store', default='int_status', dest='sw_return_type',
  #  help="Define the what the gear_profile() function should returns. Possible values: int_status, cnc25d_figure, freecad_object. Set it to freecad_object to use it with FreeCAD. Default: int_status")
  # return
  return(r_parser)
    
################################################################
# help functions 
################################################################

def gear_high_level_parameter_to_text(ai_prefix_txt, ai_param):
  """ Create a string that contains the gear high-level parameters
  """
  r_txt = "\n"
  r_txt += ai_prefix_txt+"\n"
  r_txt += "gear_type:                \t{:s}\t".format(ai_param['gear_type'])
  r_txt += "tooth_nb:                 \t{:d}\n".format(ai_param['full_tooth_nb'])
  r_txt += "gear_module:              \t{:0.3f}\n".format(ai_param['module'])
  r_txt += "primitive radius:         \t{:0.3f}   \tdiameter: {:0.3f}\n".format(ai_param['primitive_radius'], 2*ai_param['primitive_radius'])
  r_txt += "addendum-dedendum parity: \t{:0.2f} %\n".format(100*ai_param['addendum_dedendum_parity'])
  r_txt += "tooth half height:        \t{:0.3f}\n".format(ai_param['tooth_half_height'])
  if((ai_param['gear_type']=='e')or(ai_param['gear_type']=='i')):
    r_txt += "positive base radius:     \t{:0.3f}   \tdiameter: {:0.3f}\n".format(ai_param['positive_base_radius'], 2*ai_param['positive_base_radius'])
    r_txt += "negative base radius:     \t{:0.3f}   \tdiameter: {:0.3f}\n".format(ai_param['negative_base_radius'], 2*ai_param['negative_base_radius'])
  elif(ai_param['gear_type']=='l'):
    r_txt += "linear gear: inclination: {:0.3f} (radian)  {:0.3f} (degree)  positive slope: {:0.3f} (radian)  {:0.3f} (degree)  negative slope: {:0.3f} (radian)  {:0.3f}\n".format(ai_param['gearbar_inclination'], ai_param['gearbar_inclination']*180/math.pi, ai_param['positive_slope_angle'], ai_param['positive_slope_angle']*180/math.pi, ai_param['negative_slope_angle'], ai_param['negative_slope_angle']*180/math.pi)
  r_txt += "addendum radius:          \t{:0.3f}   \tdiameter: {:0.3f}\n".format(ai_param['addendum_radius'], 2*ai_param['addendum_radius'])
  r_txt += "dedendum radius:          \t{:0.3f}   \tdiameter: {:0.3f}\n".format(ai_param['dedendum_radius'], 2*ai_param['dedendum_radius'])
  r_txt += "gear hollow radius:       \t{:0.3f}   \tdiameter: {:0.3f}\n".format(ai_param['hollow_radius'], 2*ai_param['hollow_radius'])
  r_txt += "router-bit radius:        \t{:0.3f}   \tdiameter:  {:0.3f}\n".format(ai_param['gear_router_bit_radius'], 2*ai_param['gear_router_bit_radius'])
  r_txt += "gear center (x, y):       \t{:0.3f}   \t {:0.3f}\n".format(ai_param['center_ox'], ai_param['center_oy'])
  r_txt += "profile resolution (positive, negative):       \t{:d}     \t{:d}\n".format(ai_param['positive_involute_resolution'], ai_param['negative_involute_resolution'])
  r_txt += "profile skin thickness (positive, negative):   \t{:0.3f}  \t{:0.3f}\n".format(ai_param['positive_skin_thickness'], ai_param['negative_skin_thickness'])
  r_txt += "gear portion:   \ttooth_nb: {:d}   \tstart: {:d}  \tstop: {:d}\n".format(ai_param['portion_tooth_nb'], ai_param['portion_first_end'], ai_param['portion_last_end'])
  #r_txt += "first tooth position angle:   \t{:0.3f} (radian)  \t{:0.3f} (degree)\n".format(ai_param['initial_angle'], ai_param['initial_angle']*180/math.pi)
  return(r_txt)


################################################################
# the most important function to be used in other scripts
################################################################

def gear_profile(ai_constraints):
  """
  The main function of the script.
  It generates a gear_profile according to the function arguments
  """
  ### check the dictionary-arguments ai_constraints
  gpdi = gear_profile_dictionary_init()
  gp_c = gpdi.copy()
  gp_c.update(ai_constraints)
  #print("dbg155: gp_c:", gp_c)
  #print("dbg320: ai_constraints:", ai_constraints)
  if(len(gp_c.viewkeys() & gpdi.viewkeys()) != len(gp_c.viewkeys() | gpdi.viewkeys())): # check if the dictionary gp_c has exactly all the keys compare to gear_profile_dictionary_init()
    print("ERR157: Error, gp_c has too much entries as {:s} or missing entries as {:s}".format(gp_c.viewkeys() - gpdi.viewkeys(), gpdi.viewkeys() - gp_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new gear_profile constraints:")
  #for k in gp_c.viewkeys():
  #  if(gp_c[k] != gpdi[k]):
  #    print("dbg166: for k {:s}, gp_c[k] {:s} != gpdi[k] {:s}".format(k, str(gp_c[k]), str(gpdi[k])))
  ## log all input parameters
  input_parameter_info_txt = "### first gear\n# general\nggear_type {:s}\ngear_tooth_nb {:d}\ngear_module {:0.3f}\ngear_primitive_diameter {:0.3f}\ngear_addendum_dedendum_parity {:0.3f}\n".format(gp_c['gear_type'], gp_c['gear_tooth_nb'], gp_c['gear_module'], gp_c['gear_primitive_diameter'], gp_c['gear_addendum_dedendum_parity'])
  input_parameter_info_txt += "# tooth height\ngear_tooth_half_height {:0.3f}\ngear_addendum_height_pourcentage {:0.3f}\ngear_dedendum_height_pourcentage {:0.3f}\ngear_hollow_height_pourcentage {:0.3f}\ngear_router_bit_radius {:0.3f}\n".format(gp_c['gear_tooth_half_height'], gp_c['gear_addendum_height_pourcentage'], gp_c['gear_dedendum_height_pourcentage'], gp_c['gear_hollow_height_pourcentage'], gp_c['gear_router_bit_radius'])
  input_parameter_info_txt += "# positive involute\ngear_base_diameter {:0.3f}\ngear_force_angle {:0.3f}\ngear_tooth_resolution_n {:d}\ngear_skin_thickness {:0.3f}\n".format(gp_c['gear_base_diameter'], gp_c['gear_force_angle'], gp_c['gear_tooth_resolution'], gp_c['gear_skin_thickness'])
  input_parameter_info_txt += "# negative involute (if zero, negative involute = positive involute)\ngear_base_diameter_n {:0.3f}\ngear_force_angle_n {:0.3f}\ngear_tooth_resolution_n {:d}\ngear_skin_thickness_n {:0.3f}\n".format(gp_c['gear_base_diameter_n'], gp_c['gear_force_angle_n'], gp_c['gear_tooth_resolution_n'], gp_c['gear_skin_thickness_n'])
  input_parameter_info_txt += "### second gear\n# general\nsecond_gear_type {:s}\nsecond_gear_tooth_nb {:d}\nsecond_gear_primitive_diameter {:0.3f}\nsecond_gear_addendum_dedendum_parity {:0.3f}\n".format(gp_c['second_gear_type'], gp_c['second_gear_tooth_nb'], gp_c['second_gear_primitive_diameter'], gp_c['second_gear_addendum_dedendum_parity'])
  input_parameter_info_txt += "# tooth height\nsecond_gear_tooth_half_height {:0.3f}\nsecond_gear_addendum_height_pourcentage {:0.3f}\nsecond_gear_dedendum_height_pourcentage {:0.3f}\nsecond_gear_hollow_height_pourcentage {:0.3f}\nsecond_gear_router_bit_radius {:0.3f}\n".format(gp_c['second_gear_tooth_half_height'], gp_c['second_gear_addendum_height_pourcentage'], gp_c['second_gear_dedendum_height_pourcentage'], gp_c['second_gear_hollow_height_pourcentage'], gp_c['second_gear_router_bit_radius'])
  input_parameter_info_txt += "# positive involute\nsecond_gear_base_diameter {:0.3f}\nsecond_gear_tooth_resolution {:d}\nsecond_gear_skin_thickness {:0.3f}\n".format(gp_c['second_gear_base_diameter'], gp_c['second_gear_tooth_resolution'], gp_c['second_gear_skin_thickness'])
  input_parameter_info_txt += "# negative involute (if zero, negative involute = positive involute)\nsecond_gear_base_diameter_n {:0.3f}\nsecond_gear_tooth_resolution_n {:d}\nsecond_gear_skin_thickness_n {:0.3f}\n".format(gp_c['second_gear_base_diameter_n'], gp_c['second_gear_tooth_resolution_n'], gp_c['second_gear_skin_thickness_n'])
  input_parameter_info_txt += "### gearbar specific\ngearbar_slope {:0.3f}\ngearbar_slope_n {:0.3f}\n".format(gp_c['gearbar_slope'], gp_c['gearbar_slope_n'])
  input_parameter_info_txt += "### position\n# first gear position\ncenter_position_x {:0.3f}\ncenter_position_y {:0.3f}\ngear_initial_angle {:0.3f}\n# second gear position\nsecond_gear_position_angle {:0.3f}\nsecond_gear_additional_axis_length {:0.3f}\n".format(gp_c['center_position_x'], gp_c['center_position_y'], gp_c['gear_initial_angle'], gp_c['second_gear_position_angle'], gp_c['second_gear_additional_axis_length'])
  input_parameter_info_txt += "### portion\nportion_tooth_nb {:d}\nportion_first_end {:d}\nportion_last_end {:d}\n".format(gp_c['portion_tooth_nb'], gp_c['portion_first_end'], gp_c['portion_last_end'])
  ## epsilon for rounding
  #radian_epsilon = math.pi/1000
  ##### gear-profile high-level parameters
  g1_param = {}   # first gear high-level parameters
  g2_param = {}   # second gear high-level parameters
  sys_param = {}  # gear-system high-level parameters
  # gear_type
  # g1_type
  if((gp_c['gear_type']=='e')or(gp_c['gear_type']=='i')or(gp_c['gear_type']=='l')):
    g1_type = gp_c['gear_type']
  else:
    print("ERR111: Error, the gear_type {:s} is not valid!".format(gp_c['gear_type']))
    sys.exit(2)
  # g2_type
  if((gp_c['second_gear_type']=='e')or(gp_c['second_gear_type']=='i')or(gp_c['second_gear_type']=='l')):
    g2_type = gp_c['second_gear_type']
  else:
    print("ERR511: Error, the gear_type {:s} is not valid!".format(gp_c['second_gear_type']))
    sys.exit(2)
  # check of the type cross compatibility
  if((g1_type=='i')and(g2_type!='e')):
    print("ERR512: Error, internal gear is only compatible with external gear. g1_type: {:s}  g2_type: {:s}".format(g1_type, g2_type))
    sys.exit(2)
  if((g1_type=='l')and(g2_type!='e')):
    print("ERR512: Error, linear gear is only compatible with external gear. g1_type: {:s}  g2_type: {:s}".format(g1_type, g2_type))
    sys.exit(2)
  g1_param['gear_type'] = g1_type
  g2_param['gear_type'] = g2_type
  # tooth_nb
  g1_n = gp_c['gear_tooth_nb']
  if(g1_n==0):
    print("ERR112: Error, the gear_tooth_nb must be set!")
    sys.exit(2)
  if(g1_n<3):
    print("ERR113: Error, the gear_tooth_nb {:d} must be equal or bigger than 3!".format(g1_n))
    sys.exit(2)
  g2_n = gp_c['second_gear_tooth_nb']
  g2_exist = False
  if(g2_n!=0):
    g2_exist = True
  if(g2_exist and (g1_n<3)):
    print("ERR114: Error, the second_gear_tooth_nb {:d} must be equal or bigger than 3!".format(g2_n))
    sys.exit(2)
  #g1_param['gear_exist'] = True
  #g2_param['gear_exist'] = g2_exist
  sys_param['second_gear_exist'] = g2_exist
  g1_param['full_tooth_nb'] = g1_n
  g2_param['full_tooth_nb'] = g2_n
  # module
  g1_m = 1
  g1_m_set = False
  if(gp_c['gear_module']>0):
    g1_m = gp_c['gear_module']
    g1_m_set = True
  if(gp_c['gear_primitive_diameter']>0):
    if(g1_m_set):
      print("ERR115: Error, too much constraints! the gear_module is already set to {:0.2f}!".format(g1_m))
      sys.exit(2)
    else:
      if((g1_type=='i')or(g1_type=='e')):
        g1_m = float(gp_c['gear_primitive_diameter'])/g1_n
      elif(g1_type=='l'):
        g1_m = float(gp_c['gear_primitive_diameter'])/g1_n/math.pi
      g1_m_set = True
  if(gp_c['second_gear_primitive_diameter']>0):
    if(not g2_exist):
      print("ERR116: Error, set second_gear_tooth_nb to use second_gear_primitive_diameter")
      sys.exit(2)
    elif(g1_m_set):
      print("ERR117: Error, too much constraints! the gear_module is already set to {:0.2f}!".format(g1_m))
      sys.exit(2)
    else:
      if((g2_type=='i')or(g2_type=='e')):
        g1_m = float(gp_c['second_gear_primitive_diameter'])/g2_n
      elif(g2_type=='l'):
        g1_m = float(gp_c['second_gear_primitive_diameter'])/g2_n/math.pi
      g1_m_set = True
  g2_m = g1_m
  g1_param['module'] = g1_m
  g2_param['module'] = g2_m
  g1_pi_module = g1_m * math.pi
  g2_pi_module = g2_m * math.pi
  g1_param['pi_module'] = g1_pi_module
  g2_param['pi_module'] = g2_pi_module
  if((g1_type=='i')or(g1_type=='e')):
    g1_pi_module_angle = 2*math.pi/g1_n
    g1_param['pi_module_angle'] = g1_pi_module_angle
  if(g2_exist and ((g2_type=='i')or(g2_type=='e'))):
    g2_pi_module_angle = 2*math.pi/g2_n
    g2_param['pi_module_angle'] = g2_pi_module_angle
  # primitive radius
  g1_pr = 0
  if((g1_type=='i')or(g1_type=='e')):
    g1_pr = float(g1_m*g1_n)/2
  g2_pr = 0
  if((g2_type=='i')or(g2_type=='e')):
    g2_pr = float(g2_m*g2_n)/2
  g1_param['primitive_radius'] = g1_pr
  g2_param['primitive_radius'] = g2_pr
  # addendum_dedendum_parity
  g1_adp = float(gp_c['gear_addendum_dedendum_parity'])/100
  if((g1_adp<=0)or(g1_adp>=1)):
    print("ERR118: Error, the gear_addendum_dedendum_parity {:0.2f} must be set strictly between 0% and 100%!".format(gp_c['gear_addendum_dedendum_parity']))
    sys.exit(2)
  g2_adp = 1-g1_adp
  if(gp_c['second_gear_addendum_dedendum_parity']>0):
    if(not g2_exist):
      print("ERR119: Error, set second_gear_tooth_nb to use second_gear_addendum_dedendum_parity")
      sys.exit(2)
    else:
      #print("WARN211: Warning, second_gear_addendum_dedendum_parity is used for irregular cases.")
      g2_adp = float(gp_c['second_gear_addendum_dedendum_parity'])/100
  if((g2_adp<=0)or(g2_adp>=1)):
    print("ERR119: Error, the second_gear_addendum_dedendum_parity {:0.2f} must be set strictly between 0% and 100%!".format(gp_c['second_gear_addendum_dedendum_parity']))
    sys.exit(2)
  g1_param['addendum_dedendum_parity'] = g1_adp
  g2_param['addendum_dedendum_parity'] = g2_adp
  # inter-axis additional length
  aal = gp_c['second_gear_additional_axis_length']
  if(aal!=0):
    if(not g2_exist):
      print("ERR120: Error, set second_gear_tooth_nb to use second_gear_additional_axis_length")
      sys.exit(2)
    else:
      print("WARN212: Warning, second_gear_additional_axis_length is used for irregular cases.")
  sys_param['additional_inter_axis_length'] = aal
  ### tooth_height
  # external / linear :  hollow < dedendum < primitive < addendum
  # internal          :  addendum < primitive < dedendum < hollow
  # addendum_sign
  g1_as = -1 if(g1_type=='i') else 1
  g2_as = -1 if(g2_type=='i') else 1
  # position_coefficient
  g1_pc = 0 if(g1_type=='l') else 1
  g2_pc = 0 if(g2_type=='l') else 1
  g1_param['gear_sign'] = g1_as
  g2_param['gear_sign'] = g2_as
  g1_param['position_coefficient'] = g1_pc
  g2_param['position_coefficient'] = g2_pc
  g1_param['center_to_reference_length'] = g1_as * g1_pc * g1_pr
  g2_param['center_to_reference_length'] = g2_as * g2_pc * g2_pr
  # g1
  g1_thh = g1_m
  if(gp_c['gear_tooth_half_height']>0):
    g1_thh = gp_c['gear_tooth_half_height']
  g1_a_delta = g1_thh*float(gp_c['gear_addendum_height_pourcentage'])/100 # addendum delta
  g1_d_delta = g1_thh*float(gp_c['gear_dedendum_height_pourcentage'])/100 # dedendum delta
  g1_ar = g1_pr + g1_as*g1_a_delta # addendum radius
  g1_dr = g1_pr - g1_as*g1_d_delta # dedendum radius
  g1_small_r = min(g1_ar, g1_dr) # small radius
  g1_big_r = max(g1_ar, g1_dr) # big radius
  # g2
  g2_thh = g2_m
  if(gp_c['second_gear_tooth_half_height']>0):
    g2_thh = gp_c['second_gear_tooth_half_height']
  g2_a_delta = g2_thh*float(gp_c['second_gear_addendum_height_pourcentage'])/100 # addendum delta
  g2_d_delta = g2_thh*float(gp_c['second_gear_dedendum_height_pourcentage'])/100 # dedendum delta
  g2_ar = g2_pr + g2_as*g2_a_delta # addendum radius
  g2_dr = g2_pr - g2_as*g2_d_delta # dedendum radius
  g2_small_r = min(g2_ar, g2_dr) # small radius
  g2_big_r = max(g2_ar, g2_dr) # big radius
  if(g1_a_delta>aal+g2_d_delta):
    print("WARN213: Warning, the addendum {:0.2f} of the first gear is too big, other the dedendum {:0.2f} of the other gear is too small (second_gear_additional_axis_length={:0.2f})!".format(g1_a_delta, g2_d_delta, aal))
  if(g2_a_delta>aal+g1_d_delta):
    print("WARN214: Warning, the addendum {:0.2f} of the second gear is too big, other the dedendum {:0.2f} of the other gear is too small (second_gear_additional_axis_length={:0.2f})!".format(g2_a_delta, g1_d_delta, aal))
  if(g1_a_delta+g2_a_delta<aal):
    print("WARN215: Warning, the (second_gear_additional_axis_length {:0.2f} is too big compare to the addendum {:0.2f} and {:0.2f}!".format(aal, g1_a_delta, g2_a_delta))
  g1_param['tooth_half_height'] = g1_thh # g1
  g1_param['addendum_height']   = g1_a_delta
  g1_param['dedendum_height']   = g1_d_delta
  g1_param['addendum_radius']   = g1_ar
  g1_param['dedendum_radius']   = g1_dr
  g1_param['smaller_radius']    = g1_small_r
  g1_param['bigger_radius']     = g1_big_r
  g1_param['real_tooth_hight']  = g1_a_delta + g1_d_delta
  g2_param['tooth_half_height'] = g2_thh # g2
  g2_param['addendum_height']   = g2_a_delta
  g2_param['dedendum_height']   = g2_d_delta
  g2_param['addendum_radius']   = g2_ar
  g2_param['dedendum_radius']   = g2_dr
  g2_param['smaller_radius']    = g2_small_r
  g2_param['bigger_radius']     = g2_big_r
  g2_param['real_tooth_hight']  = g2_a_delta + g2_d_delta
  ### base radius
  g1_brp = 0
  g1_brn = 0
  g1_sp = 0
  g1_sn = 0
  if((g1_type=='e')or(g1_type=='i')):
    # positive involute : positive_base_radius
    g1_brp = g1_small_r # default value
    if(g2_exist and (g2_type=='e') and (g2_n<g1_n)):
      g1_brp = float(g2_small_r*g1_n)/g2_n # default value when running with a smaller gear
    g1_brp_set = False
    if(gp_c['gear_base_diameter']>0):
      g1_brp = float(gp_c['gear_base_diameter'])/2
      g1_brp_set = True
    if(gp_c['second_gear_base_diameter']>0):
      if(not g2_exist):
        print("ERR121: Error, set second_gear_tooth_nb to use second_gear_base_diameter")
        sys.exit(2)
      elif(g2_type=='l'):
        print("ERR921: Error, the second gear type {:s} is a gearbar".format(g2_type))
        sys.exit(2)
      elif(g1_brp_set):
        print("ERR122: Error, too much constraints! gear_base_diameter is already set to {:0.2f}".format(g1_brp*2))
        sys.exit(2)
      else:
        g1_brp = float(gp_c['second_gear_base_diameter']*g1_n)/(2*g2_n)
        g1_brp_set = True
    if(gp_c['gearbar_slope']>0):
      if(not g2_exist):
        print("ERR811: Error, set second_gear_tooth_nb to use gearbar_slope")
        sys.exit(2)
      elif((g2_type=='e')or(g2_type=='i')):
        print("ERR812: Error, the second gear type {:s} is not a gearbar".format(g2_type))
        sys.exit(2)
      elif(g1_brp_set):
        print("ERR813: Error, too much constraints! gear_base_diameter is already set to {:0.2f}".format(g1_brp*2))
        sys.exit(2)
      else:
        g1_brp = g1_pr*math.cos(gp_c['gearbar_slope'])
        g1_brp_set = True
    if(gp_c['gear_force_angle']>0):
      if(g1_brp_set):
        print("ERR123: Error, too much constraints! gear_base_diameter is already set to {:0.2f}".format(g1_brp*2))
        sys.exit(2)
      else:
        g1_brp = g1_pr*math.cos(gp_c['gear_force_angle'])
        g1_brp_set = True
    # negative involute : negative_base_radius
    g1_brn = g1_brp
    g1_brn_set = False
    if(gp_c['gear_base_diameter_n']>0):
      g1_brn = float(gp_c['gear_base_diameter_n'])/2
      g1_brn_set = True
    if(gp_c['second_gear_base_diameter_n']>0):
      if(not g2_exist):
        print("ERR121: Error, set second_gear_tooth_nb to use second_gear_base_diameter_n")
        sys.exit(2)
      elif(g2_type=='l'):
        print("ERR922: Error, the second gear type {:s} is a gearbar".format(g2_type))
        sys.exit(2)
      elif(g1_brn_set):
        print("ERR122: Error, too much constraints! gear_base_diameter_n is already set to {:0.2f}".format(g1_brn*2))
        sys.exit(2)
      else:
        g1_brn = float(gp_c['second_gear_base_diameter_n']*g1_n)/(2*g2_n)
        g1_brn_set = True
    if(gp_c['gearbar_slope_n']>0):
      if(not g2_exist):
        print("ERR821: Error, set second_gear_tooth_nb to use gearbar_slope_n")
        sys.exit(2)
      elif((g2_type=='e')or(g2_type=='i')):
        print("ERR822: Error, the second gear type {:s} is not a gearbar".format(g2_type))
        sys.exit(2)
      elif(g1_brn_set):
        print("ERR823: Error, too much constraints! gear_base_diameter is already set to {:0.2f}".format(g1_brn*2))
        sys.exit(2)
      else:
        g1_brn = g1_pr*math.cos(gp_c['gearbar_slope_n'])
        g1_brn_set = True
    if(gp_c['gear_force_angle_n']>0):
      if(g1_brn_set):
        print("ERR123: Error, too much constraints! gear_base_diameter is already set to {:0.2f}".format(g1_brn*2))
        sys.exit(2)
      else:
        g1_brn = g1_pr*math.cos(gp_c['gear_force_angle_n'])
        g1_brn_set = True
  elif(g1_type=='l'):
    g1_sp_set = False
    if((gp_c['gear_base_diameter']>0)or(gp_c['gear_base_diameter_n']>0)):
      print("ERR331: Error, for gearbar use gearbar_slope and gearbar_slope_n instead of gear_base_diameter {:0.3f}  and gear_base_diameter_n {:0.3f}".format(gp_c['gear_base_diameter'], gp_c['gear_base_diameter_n']))
      sys.exit(2)
    if(gp_c['gearbar_slope']>0):
      g1_sp = gp_c['gearbar_slope']
      g1_sp_set = True
    if(gp_c['gear_force_angle']>0):
      if(not g1_sp_set):
        g1_sp = gp_c['gear_force_angle']
        g1_sp_set = True
    if(gp_c['second_gear_base_diameter']>0):
      if(not g2_exist):
        print("ERR521: Error, set second_gear_tooth_nb to use second_gear_base_diameter")
        sys.exit(2)
      elif(g1_sp_set):
        print("ERR523: Error, too much constraints! gearbar_slope_angle is already set to {:0.2f}".format(g1_sp))
        sys.exit(2)
      else:
        g1_sp = math.acos(float(gp_c['second_gear_base_diameter'])/(2*g2_pr))
        g1_sp_set = True
    if(not g1_sp_set):
      print("ERR541: Error, the slope angle of the linear gear 1 is not set!")
      sys.exit(2)
    g1_sn = g1_sp
    g1_sn_set = False
    if(gp_c['gearbar_slope_n']>0):
      g1_sn = gp_c['gearbar_slope_n']
      g1_sn_set = True
    if(gp_c['gear_force_angle_n']>0):
      if(not g2_sn_set):
        g1_sn = gp_c['gear_force_angle_n']
        g1_sn_set = True
    if(gp_c['second_gear_base_diameter_n']>0):
      if(not g2_exist):
        print("ERR531: Error, set second_gear_tooth_nb to use second_gear_base_diameter_n")
        sys.exit(2)
      elif(g1_sn_set):
        print("ERR532: Error, too much constraints! gearbar_slope_angle_n is already set to {:0.2f}".format(g1_sp))
        sys.exit(2)
      else:
        g1_sn = math.acos(float(gp_c['second_gear_base_diameter_n'])/(2*g2_pr))
        g1_sn_set = True
  # now we have: g1_brp, g1_brn, g1_sp, g1_sn
  g2_brp = 0
  g2_brn = 0
  g2_sp = 0
  g2_sn = 0
  if((g2_type=='e')or(g2_type=='i')):
    if((g1_type=='e')or(g1_type=='i')):
      g2_brp = g1_brp*g2_n/g1_n
      g2_brn = g1_brn*g2_n/g1_n
    elif(g1_type=='l'):
      g2_brp = g2_pr*math.cos(g1_sp)
      g2_brn = g2_pr*math.cos(g1_sn)
  elif(g2_type=='l'):
    g2_sp = math.acos(float(g1_brp)/g1_pr)
    g2_sn = math.acos(float(g1_brn)/g1_pr)
  # base radius check
  if((g1_type=='e')or(g1_type=='i')):
    if(g1_brp>g1_small_r):
      print("WARN216: Warning, g1_brp {:0.2f} is bigger than g1_small_r {:0.2f}".format(g1_brp, g1_small_r))
    if(g1_brn>g1_small_r):
      print("WARN246: Warning, g1_brn {:0.2f} is bigger than g1_small_r {:0.2f}".format(g1_brn, g1_small_r))
    if(g1_brp!=g1_brn):
      print("WARN218: Warning, g1_brp {:0.2f} and g1_brn {:0.2f} are different. The gear_tooth are asymmetrical!".format(g1_brp, g1_brn))
    if(g1_brp>g1_big_r):
      print("ERR616: Error, g1_brp {:0.2f} is bigger than g1_big_r {:0.2f}".format(g1_brp, g1_big_r))
      sys.exit(2)
    if(g1_brn>g1_big_r):
      print("ERR646: Error, g1_brn {:0.2f} is bigger than g1_big_r {:0.2f}".format(g1_brn, g1_big_r))
      sys.exit(2)
  if((g2_type=='e')or(g2_type=='i')):
    if(g2_exist and (g2_brp>g2_small_r)):
      print("WARN217: Warning, g2_brp {:0.2f} is bigger than g2_small_r {:0.2f}".format(g2_brp, g2_small_r))
    if(g2_exist and (g2_brn>g2_small_r)):
      print("WARN247: Warning, g2_brn {:0.2f} is bigger than g2_small_r {:0.2f}".format(g2_brn, g2_small_r))
    if(g2_exist and (g2_brp>g2_big_r)):
      print("ERR617: Error, g2_brp {:0.2f} is bigger than g2_big_r {:0.2f}".format(g2_brp, g2_big_r))
      sys.exit(2)
    if(g2_exist and (g2_brn>g2_big_r)):
      print("ERR647: Error, g2_brn {:0.2f} is bigger than g2_big_r {:0.2f}".format(g2_brn, g2_big_r))
      sys.exit(2)
  g1_param['positive_base_radius'] = g1_brp
  g1_param['negative_base_radius'] = g1_brn
  g1_param['positive_slope_angle'] = g1_sp
  g1_param['negative_slope_angle'] = g1_sn
  g2_param['positive_base_radius'] = g2_brp
  g2_param['negative_base_radius'] = g2_brn
  g2_param['positive_slope_angle'] = g2_sp
  g2_param['negative_slope_angle'] = g2_sn
  # initial position
  g1_ia = gp_c['gear_initial_angle']
  g1_ix = gp_c['center_position_x']
  g1_iy = gp_c['center_position_y']
  g1g2_a = gp_c['second_gear_position_angle']
  g2_ia = 0 # will be computed later
  inter_axis_length = g1_pc*g1_pr+(g1_as*g2_as)*g2_pc*g2_pr+g1_as*aal
  g2_ix = g1_ix + inter_axis_length*math.cos(g1g2_a)
  g2_iy = g1_iy + inter_axis_length*math.sin(g1g2_a)
  g1_param['center_ox']     = g1_ix
  g1_param['center_oy']     = g1_iy
  g1_param['initial_angle'] = g1_ia
  g2_param['center_ox']     = g2_ix
  g2_param['center_oy']     = g2_iy
  g2_param['initial_angle'] = g2_ia
  sys_param['g1g2_angle'] = g1g2_a
  sys_param['inter_axis_length'] = inter_axis_length
  # router_bit radius
  g1_rbr = gp_c['gear_router_bit_radius']
  g2_rbr = g1_rbr
  if(gp_c['second_gear_router_bit_radius']>0):
    if(not g2_exist):
      print("ERR124: Error, set second_gear_tooth_nb to use second_gear_router_bit_radius")
      sys.exit(2)
    else:
      g2_rbr = gp_c['second_gear_router_bit_radius']
  g1_param['gear_router_bit_radius'] = g1_rbr
  g2_param['gear_router_bit_radius'] = g2_rbr
  #print("dbg728: g1_rbr {:0.3f}  g2_rbr {:0.3f}".format(g1_rbr, g2_rbr))
  #print("dbg729: gp_c['gear_router_bit_radius'] {:0.3f}".format(gp_c['gear_router_bit_radius']))
  # hollow
  g1_h_delta = g1_thh*float(gp_c['gear_hollow_height_pourcentage'])/100
  if(g1_h_delta<1.05*g1_rbr):
    print("WARN218: Warning, g1_h_delta {:0.2f} is smaller than the router_bit_radius {:0.2f}. gear_hollow_height_pourcentage {:0.2f} should be set to {:0.2f}".format(g1_h_delta, g1_rbr, gp_c['gear_hollow_height_pourcentage'], 100.0*g1_rbr/g1_thh))
    g1_h_delta = 1.05*g1_rbr
  g2_h_delta = g2_thh*float(gp_c['second_gear_hollow_height_pourcentage'])/100
  if(g2_exist):
    if(g2_h_delta<1.05*g2_rbr):
      print("WARN219: Warning, g2_h_delta {:0.2f} is smaller than the second_router_bit_radius {:0.2f}. second_gear_hollow_height_pourcentage {:0.2f} should be set to {:0.2f}".format(g2_h_delta, g2_rbr, gp_c['second_gear_hollow_height_pourcentage'], 100.0*g2_rbr/g2_thh))
      g2_h_delta = 1.05*g2_rbr
  g1_hr = g1_dr - g1_as*g1_h_delta
  g2_hr = g2_dr - g2_as*g2_h_delta
  g1_param['hollow_height'] = g1_h_delta
  g1_param['hollow_radius'] = g1_hr
  g2_param['hollow_height'] = g2_h_delta
  g2_param['hollow_radius'] = g2_hr
  # involute resolution
  g1_irp = gp_c['gear_tooth_resolution']
  g1_irn = g1_irp
  if(gp_c['gear_tooth_resolution_n']>0):
    g1_irn = gp_c['gear_tooth_resolution_n']
  g2_irp = g1_irp
  if(gp_c['second_gear_tooth_resolution']>0):
    g2_irp = gp_c['second_gear_tooth_resolution']
  g2_irn = g2_irp
  if(gp_c['second_gear_tooth_resolution_n']>0):
    g2_irn = gp_c['second_gear_tooth_resolution_n']
  g1_param['positive_involute_resolution'] = g1_irp
  g1_param['negative_involute_resolution'] = g1_irn
  g2_param['positive_involute_resolution'] = g2_irp
  g2_param['negative_involute_resolution'] = g2_irn
  # skin_thickness
  g1_stp = gp_c['gear_skin_thickness']
  g1_stn = g1_stp
  if(gp_c['gear_skin_thickness_n']!=0):
    g1_stn = gp_c['gear_skin_thickness_n']
  g2_stp = gp_c['second_gear_skin_thickness']
  #g2_stp = g1_stp
  #if(gp_c['second_gear_skin_thickness!=0):
  #  g2_stp = gp_c['second_gear_skin_thickness']
  g2_stn = g2_stp
  if(gp_c['second_gear_skin_thickness_n']!=0):
    g2_stn = gp_c['second_gear_skin_thickness_n']
  g1_param['positive_skin_thickness'] = g1_stp
  g1_param['negative_skin_thickness'] = g1_stn
  g2_param['positive_skin_thickness'] = g2_stp
  g2_param['negative_skin_thickness'] = g2_stn
  #print("dbg972: gp_c['second_gear_skin_thickness'] {:0.3f}  g2_stp {:0.3f}  g2_param_positive_skin_thickness {:0.3f}".format(gp_c['second_gear_skin_thickness'], g2_stp, g2_param['positive_skin_thickness']))
  # portion
  g1_ptn = 0 # 0: full first gear
  g1_pfe = 0
  g1_ple = 0
  if(gp_c['portion_tooth_nb']>0): # cut a portion of the first gear
    if(((g1_type=='e')or(g1_type=='i'))and(gp_c['portion_tooth_nb']>=g1_n)):
      print("ERR553: Error, the portion {:d} of gearwheel is bigger than the maximal number of teeth {:d}!".format(gp_c['portion_tooth_nb'], g1_n))
      sys.exit(2)
    g1_ptn = gp_c['portion_tooth_nb']
    g1_pfe = gp_c['portion_first_end']
    g1_ple = gp_c['portion_last_end']
  g2_ptn = 0 # full second gear
  g2_pfe = 0
  g2_ple = 0
  #print("dbg763: g1_ptn {:d}  portion_tooth_nb {:d}".format(g1_ptn, gp_c['portion_tooth_nb']))
  g1_param['portion_tooth_nb']  = g1_ptn
  g1_param['portion_first_end'] = g1_pfe
  g1_param['portion_last_end']  = g1_ple
  g2_param['portion_tooth_nb']  = g2_ptn
  g2_param['portion_first_end'] = g2_pfe
  g2_param['portion_last_end']  = g2_ple
  # bar inclination (make only sense for the gearbar)
  g1_bi = g1g2_a
  g2_bi = g1g2_a + math.pi
  g1_param['gearbar_inclination']  = g1_bi
  g2_param['gearbar_inclination']  = g2_bi
  g1_param['gearbar_length']  = g1_n * g1_m * math.pi
  g2_param['gearbar_length']  = g2_n * g2_m * math.pi
  #
  #print("dbg341: g1_param:", g1_param)
  #print("dbg342: g2_param:", g2_param)
  #print("dbg343: sys_param:", sys_param)
  ## end of the construction of the high-level parameters

  ## compute the real_force_angle and the tooth_contact_path
  if(g2_exist):
    (real_force_info_p, positive_rotation_action_line_outline) = info_on_real_force_angle(g1_param, g2_param, sys_param,  1)
    (real_force_info_n, negative_rotation_action_line_outline) = info_on_real_force_angle(g1_param, g2_param, sys_param, -1)
    real_force_info = "Real force info:\n" + real_force_info_p + real_force_info_n

  ### generate the first gear outline
  (g1_make_low_param, g1_info_low) = calc_low_level_gear_parameters(g1_param)
  g1_outline_B = gear_profile_outline(g1_make_low_param, g1_ia)
  # output info
  g1_info_txt = gear_high_level_parameter_to_text("Gear-profile 1:", g1_param)
  g1_info_txt += g1_info_low
  #print(g1_info_txt)
  g1g2_info_txt = g1_info_txt
  exhaustive_info_txt = '\n\nstart of gear_profile info\n\n' + gp_c['args_in_txt'] + '\n\n' + g1_info_txt + '\n\n' + input_parameter_info_txt + '\nend of gear_profile info\n\n'
  
  ### generate the second gear outline
  g1g2_info_txt = g1_info_txt
  if(g2_exist):
    ### g2
    #print("dbg369: Prepare the second gear ..")
    #print("dbg521: g2_high_parameters:", g2_high_parameters)
    g2_ia = 0
    (g2_make_low_param, g2_info_low) = calc_low_level_gear_parameters(g2_param)
    #print("dbg653: g2_make_low_param:", g2_make_low_param)
    #g2_outline_B = gear_profile_outline(g2_make_low_param, g2_ia)
    ### g2_position
    (place_low_parameters, place_info) = pre_g2_position_calculation(g1_param, g2_param, aal, g1g2_a, g1_rotation_speed, speed_scale)
    (g2_iap, g2_rotation_speed_p, tmp_tangential_friction, tmp_c1_speed_outline, tmp_c2_speed_outline) = g2_position_calculation(place_low_parameters, 1, g1_ia)
    (g2_ian, g2_rotation_speed_n, tmp_tangential_friction, tmp_c1_speed_outline, tmp_c2_speed_outline) = g2_position_calculation(place_low_parameters,-1, g1_ia)
    if((g2_type=='e')or(g2_type=='i')):
      g2_ia_modulo = g2_pi_module_angle
    elif(g2_type=='l'):
      g2_ia_modulo = g2_pi_module
    #print("dbg847: g2_iap {:0.8f}".format(g2_iap))
    g2_iap_ox = math.fmod(g2_iap+2*math.pi+0.5*g2_ia_modulo, g2_ia_modulo) - 0.5*g2_ia_modulo
    g2_ian_ox = math.fmod(g2_ian+2*math.pi+0.5*g2_ia_modulo, g2_ia_modulo) - 0.5*g2_ia_modulo
    slack_sign = 1
    if((g1_type=='i')or(g2_type=='i')or(g2_type=='l')):
      slack_sign = -1
    g2_ia_slack = math.fmod(slack_sign*(g2_iap_ox - g2_ian_ox) + 4.5*g2_ia_modulo, g2_ia_modulo) - 0.5*g2_ia_modulo
    initial_position_info_txt = "Initial position: "
    initial_speed_info_txt = "Initial speed: "
    if((g1_type=='e')or(g1_type=='i')):
      initial_position_info_txt += "g1_ia: {:0.3f} (radian)  {:0.3f} (degree)\n".format(g1_ia, g1_ia*180/math.pi)
      initial_speed_info_txt += "g1_initial_speed: {:0.3f} (radian/s)  {:0.3f} (revolution/s)\n".format(g1_rotation_speed, g1_rotation_speed/math.pi)
    elif(g1_type=='l'):
      initial_position_info_txt += "g1_ia: {:0.3f} (mm)\n".format(g1_ia)
      initial_speed_info_txt += "g1_initial_speed: {:0.3f} (mm/s)\n".format(g1_rotation_speed)
    if((g2_type=='e')or(g2_type=='i')):
      initial_position_info_txt += "g2_iap: {:0.3f} (radian)  {:0.3f} (degree)  g2_iap_ox: {:0.3f} (radian)  {:0.3f} (degree)\n".format(g2_iap, g2_iap*180/math.pi, g2_iap_ox, g2_iap_ox*180/math.pi)
      initial_position_info_txt += "g2_ian: {:0.3f} (radian)  {:0.3f} (degree)  g2_ian_ox: {:0.3f} (radian)  {:0.3f} (degree)\n".format(g2_ian, g2_ian*180/math.pi, g2_ian_ox, g2_ian_ox*180/math.pi)
      initial_position_info_txt += "g2_ia_slack: {:0.5f} (radian)  {:0.5f} (degree)\n".format(g2_ia_slack, g2_ia_slack*180/math.pi)
      initial_speed_info_txt += "g2_initial_speed: positive:  {:0.3f} (rad/s)  {:0.3f} (rev/s)  negative:  {:0.3f} (rad/s)  {:0.3f} (rev/s)\n".format(g2_rotation_speed_p, g2_rotation_speed_p/math.pi, g2_rotation_speed_n, g2_rotation_speed_n/math.pi)
    elif(g2_type=='l'):
      initial_position_info_txt += "g2_iap: {:0.3f} (mm)  g2_iap_ox: {:0.3f} (mm)\n".format(g2_iap, g2_iap_ox)
      initial_position_info_txt += "g2_ian: {:0.3f} (mm)  g2_ian_ox: {:0.3f} (mm)\n".format(g2_ian, g2_ian_ox)
      initial_position_info_txt += "g2_ia_slack: {:0.5f} (mm)\n".format(g2_ia_slack)
      initial_speed_info_txt += "g2_initial_speed: positive:  {:0.3f} (mm/s)  negative: {:0.3f} (mm/s)\n".format(g2_rotation_speed_p, g2_rotation_speed_n)
    g2_param['initial_angle'] = g2_iap
    g1_param['second_positive_initial_angle'] = g2_iap_ox     # hack for epicyclic_gearing
    g1_param['second_negative_initial_angle'] = g2_ian_ox     # hack for epicyclic_gearing
    g1_param['second_pi_module_angle'] = g2_ia_modulo #g2_pi_module_angle   # hack for epicyclic_gearing
    # output info
    sys_info_txt = "\nGear system: ratio: {:0.3f}\n g1g2_a: {:0.3f}  \tadditional inter-axis length: {:0.3f}\n".format(float(g1_n)/g2_n, g1g2_a, aal)
    sys_info_txt += real_force_info
    sys_info_txt += place_info
    sys_info_txt += initial_position_info_txt
    sys_info_txt += initial_speed_info_txt
    g2_info_txt = gear_high_level_parameter_to_text("Gear-profile 2:", g2_param)
    g2_info_txt += g2_info_low
    #print(sys_info_txt + g2_info_txt)
    g1g2_info_txt += sys_info_txt + g2_info_txt
    #print("dbg689: g2_outline_B is ready")
    exhaustive_info_txt = '\n\nstart of gear_profile info\n\n' + gp_c['args_in_txt'] + '\n\n' + g1g2_info_txt + '\n\n' + input_parameter_info_txt + '\nend of gear_profile info\n\n'

  ### simulation
  if(gp_c['simulation_enable']):
    print("Launch the simulation with Tkinter ..")
    # initialization
    #g1_ideal_involute = ideal_tooth_outline(g1_make_low_param, 0, 0)
    #g1_ideal_tooth = ideal_tooth_outline(g1_make_low_param, 0, 1)
    #if(g2_exist):
    #  g2_outline_B = gear_profile_outline(g2_make_low_param, 0)
    #  g2_ideal_involute = ideal_tooth_outline(g2_make_low_param, 0, 0)
    #  g2_ideal_tooth = ideal_tooth_outline(g2_make_low_param, 0, 1)
    ### gear_profile parameter info in the log
    print(g1g2_info_txt)
    ### static figure
    inter_axis_outline = ((g1_ix, g1_iy), (g2_ix, g2_iy))
    ### matplotlib curve table
    g1_position_curve_table = []
    g2_position_curve_table = []
    g2_rotation_speed_curve_table = []
    tangential_friction_curve_table = []
    ### start Tkinter
    tk_root = Tkinter.Tk()
    my_canvas = cnc25d_api.Two_Canvas(tk_root)
    # callback functions for display_backend
    def sub_canvas_graphics(ai_rotation_direction, ai_angle_position):
      """ create the graphics and fill-up the matplotlib curve tables
      """
      #global g1_position_curve_table, g2_position_curve_table, g2_rotation_speed_curve_table, tangential_friction_curve_table # no need of global because just append element to lists
      ## gear position
      # g1_position : assuming that ai_angle_position is incremented by 1.0 in fast_speed
      if((g1_type=='e')or(g1_type=='i')):
        g1_position = g1_ia+ai_angle_position*float(g1_pi_module_angle)/20 # 20th of pi_module_angle (angular tooth pitch)
      elif(g1_type=='l'):
        g1_position = g1_ia-ai_angle_position*float(g1_pi_module)/20 # 20th of pi_module (linear tooth pitch)
      # g2_position
      if(g2_exist):
        #g2_position = g2_ia-ai_angle_position # completely wrong, just waiting for the good formula
        (g2_position, g2_rotation_speed, tangential_friction, c1_speed_outline, c2_speed_outline) = g2_position_calculation(place_low_parameters, ai_rotation_direction, g1_position)
      ## get outline_B
      lg1_outline_B = gear_profile_outline(g1_make_low_param, g1_position)
      lg1_ideal_involute = ideal_tooth_outline(g1_make_low_param, g1_position, 0)
      lg1_ideal_tooth = ideal_tooth_outline(g1_make_low_param, g1_position, 1)
      if(g2_exist):
        lg2_outline_B = gear_profile_outline(g2_make_low_param, g2_position)
        lg2_ideal_involute = ideal_tooth_outline(g2_make_low_param, g2_position, 0)
        lg2_ideal_tooth = ideal_tooth_outline(g2_make_low_param, g2_position, 1)
      ## alternative to get outline_B
      #lg1_outline_B = cnc25d_api.outline_rotate(g1_outline_B, g1_ix, g1_iy, g1_position-g1_ia)
      #lg1_ideal_involute = cnc25d_api.outline_rotate(g1_ideal_involute, g1_ix, g1_iy, g1_position)
      #lg1_ideal_tooth = cnc25d_api.outline_rotate(g1_ideal_tooth, g1_ix, g1_iy, g1_position)
      #if(g2_exist):
      #  lg2_outline_B = cnc25d_api.outline_rotate(g2_outline_B, g2_ix, g2_iy, g2_position)
      #  lg2_ideal_involute = cnc25d_api.outline_rotate(g2_ideal_involute, g2_ix, g2_iy, g2_position)
      #  lg2_ideal_tooth = cnc25d_api.outline_rotate(g2_ideal_tooth, g2_ix, g2_iy, g2_position)
      # action_line
      if(g2_exist):
        if(ai_rotation_direction==1):
          action_line_outline = positive_rotation_action_line_outline
        else:
          action_line_outline = negative_rotation_action_line_outline
      ## make graphic
      r_canvas_graphics = []
      r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(lg1_outline_B, 'tkinter'), 'red', 1))
      r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(lg1_ideal_involute, 'tkinter'), 'green', 1))
      r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(lg1_ideal_tooth, 'tkinter'), 'blue', 1))
      if(g2_exist):
        r_canvas_graphics.append(('graphic_lines', cnc25d_api.outline_arc_line(lg2_outline_B, 'tkinter'), 'grey', 1))
        r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(lg2_ideal_involute, 'tkinter'), 'green', 1))
        r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(lg2_ideal_tooth, 'tkinter'), 'blue', 1))
        # speed overlay
        r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(c1_speed_outline, 'tkinter'), 'yellow', 1))
        r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(c2_speed_outline, 'tkinter'), 'orange', 1))
        # action line
        r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(action_line_outline, 'tkinter'), 'brown', 1))
        # debug
        #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g1_ix, g1_iy, g1_brp), 'tkinter'), 'brown', 1))
        #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g1_ix, g1_iy, g1_brn), 'tkinter'), 'brown', 1))
        #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g2_ix, g2_iy, g2_brp), 'tkinter'), 'brown', 1))
        #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g2_ix, g2_iy, g2_brn), 'tkinter'), 'brown', 1))
        #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g1_ix, g1_iy, g1_ar), 'tkinter'), 'green', 1))
        #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g2_ix, g2_iy, g2_ar), 'tkinter'), 'green', 1))
      # g1 debug circle
      #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g1_ix, g1_iy, g1_dr), 'tkinter'), 'green', 1))
      #r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line((g1_ix, g1_iy, g1_hr), 'tkinter'), 'green', 1))
      # inter-axis
      r_canvas_graphics.append(('overlay_lines', cnc25d_api.outline_arc_line(inter_axis_outline, 'tkinter'), 'green', 1))
      ## update matplotlib curve_table
      if(g2_exist):
        #print("dbg554: g1_position: {:0.3f}  g2_position: {:0.3f}  g2_rotation_speed: {:0.3f}  tangential_friction: {:0.3f}".format(g1_position, g2_position, g2_rotation_speed, tangential_friction))
        g1_position_curve_table.append(g1_position)
        g2_position_curve_table.append(g2_position)
        g2_rotation_speed_curve_table.append(g2_rotation_speed)
        tangential_friction_curve_table.append(tangential_friction)
        # to avoid the matplotlib exponential scale
        if(len(g2_rotation_speed_curve_table)==1):
          g2_rotation_speed_curve_table[0] = 1.01*g2_rotation_speed_curve_table[0]
      return(r_canvas_graphics)
    # matplotlib stuff
    gear_profile_mpl_curves = (('gear-profile analysis\n(with g1_rotation_speed = 1 radian/s)', 'g1_position_angle (simulation iteration)', 1),
      ('g1\nposition\n(radian)', g1_position_curve_table, 'gx'),
      ('g2\nposition\n(radian)', g2_position_curve_table, 'r+'),
      ('g2\nrotation_speed\n(radian/s)', g2_rotation_speed_curve_table, 'y.'),
      ('tangential\nfriction\n(mm/s)', tangential_friction_curve_table, 'bo'))
    # end of callback functions
    my_canvas.add_canvas_graphic_function(sub_canvas_graphics)
    my_canvas.add_parameter_info(g1g2_info_txt)
    my_canvas.add_curve_graphic_table(gear_profile_mpl_curves)
    tk_root.mainloop()
    del (my_canvas, tk_root) # because Tkinter could be used again later in this script
    time.sleep(1) # delay to help Tkinter to close properly

  ### output files
  gp_figure = [g1_outline_B] # select the outlines to be writen in files
  cnc25d_api.generate_output_file(gp_figure, gp_c['output_file_basename'], gp_c['gear_profile_height'], exhaustive_info_txt)

  ### return
  if(gp_c['return_type']=='int_status'):
    r_gp = 1
  elif(gp_c['return_type']=='cnc25d_figure'):
    r_gp = gp_figure
  elif(gp_c['return_type']=='freecad_object'):
    r_gp = cnc25d_api.figure_to_freecad_25d_part(gp_figure, gp_c['gear_profile_height'])
  elif(gp_c['return_type']=='figure_param_info'):
    r_gp = (g1_outline_B, g1_param, exhaustive_info_txt)
  else:
    print("ERR346: Error the return_type {:s} is unknown".format(gp_c['return_type']))
    sys.exit(2)
  return(r_gp)

################################################################
# gear_profile wrapper dance
################################################################

def gear_profile_argparse_to_dictionary(ai_gp_args, ai_variant=0):
  """ convert a gear_profile_argparse into a gear_profile_dictionary
  """
  r_gpd = {}
  ### first gear
  # general
  if((ai_variant!=1)and(ai_variant!=2)and(ai_variant!=3)and(ai_variant!=4)):
    r_gpd['gear_type'] = ai_gp_args.sw_gear_type
  if(ai_variant!=4):
    r_gpd['gear_tooth_nb'] = ai_gp_args.sw_gear_tooth_nb
    r_gpd['gear_module'] = ai_gp_args.sw_gear_module
  r_gpd['gear_primitive_diameter'] = ai_gp_args.sw_gear_primitive_diameter
  r_gpd['gear_addendum_dedendum_parity'] = ai_gp_args.sw_gear_addendum_dedendum_parity
  # tooth height
  r_gpd['gear_tooth_half_height'] = ai_gp_args.sw_gear_tooth_half_height
  r_gpd['gear_addendum_height_pourcentage'] = ai_gp_args.sw_gear_addendum_height_pourcentage
  r_gpd['gear_dedendum_height_pourcentage'] = ai_gp_args.sw_gear_dedendum_height_pourcentage
  r_gpd['gear_hollow_height_pourcentage'] = ai_gp_args.sw_gear_hollow_height_pourcentage
  r_gpd['gear_router_bit_radius'] = ai_gp_args.sw_gear_router_bit_radius
  # positive involute
  r_gpd['gear_base_diameter'] = ai_gp_args.sw_gear_base_diameter
  r_gpd['gear_force_angle'] = ai_gp_args.sw_gear_force_angle
  r_gpd['gear_tooth_resolution'] = ai_gp_args.sw_gear_tooth_resolution
  r_gpd['gear_skin_thickness'] = ai_gp_args.sw_gear_skin_thickness
  # negative involute (if zero, negative involute = positive involute)
  r_gpd['gear_base_diameter_n'] = ai_gp_args.sw_gear_base_diameter_n
  r_gpd['gear_force_angle_n'] = ai_gp_args.sw_gear_force_angle_n
  r_gpd['gear_tooth_resolution_n'] = ai_gp_args.sw_gear_tooth_resolution_n
  r_gpd['gear_skin_thickness_n'] = ai_gp_args.sw_gear_skin_thickness_n
  ### second gear
  # general
  if((ai_variant!=2)and(ai_variant!=3)and(ai_variant!=4)):
    r_gpd['second_gear_type'] = ai_gp_args.sw_second_gear_type
  r_gpd['second_gear_tooth_nb'] = ai_gp_args.sw_second_gear_tooth_nb
  r_gpd['second_gear_primitive_diameter'] = ai_gp_args.sw_second_gear_primitive_diameter
  r_gpd['second_gear_addendum_dedendum_parity'] = ai_gp_args.sw_second_gear_addendum_dedendum_parity
  # tooth height
  r_gpd['second_gear_tooth_half_height'] = ai_gp_args.sw_second_gear_tooth_half_height
  r_gpd['second_gear_addendum_height_pourcentage'] = ai_gp_args.sw_second_gear_addendum_height_pourcentage
  r_gpd['second_gear_dedendum_height_pourcentage'] = ai_gp_args.sw_second_gear_dedendum_height_pourcentage
  r_gpd['second_gear_hollow_height_pourcentage'] = ai_gp_args.sw_second_gear_hollow_height_pourcentage
  r_gpd['second_gear_router_bit_radius'] = ai_gp_args.sw_second_gear_router_bit_radius
  # positive involute
  r_gpd['second_gear_base_diameter'] = ai_gp_args.sw_second_gear_base_diameter
  r_gpd['second_gear_tooth_resolution'] = ai_gp_args.sw_second_gear_tooth_resolution
  r_gpd['second_gear_skin_thickness'] = ai_gp_args.sw_second_gear_skin_thickness
  # negative involute (if zero, negative involute = positive involute)
  r_gpd['second_gear_base_diameter_n'] = ai_gp_args.sw_second_gear_base_diameter_n
  r_gpd['second_gear_tooth_resolution_n'] = ai_gp_args.sw_second_gear_tooth_resolution_n
  r_gpd['second_gear_skin_thickness_n'] = ai_gp_args.sw_second_gear_skin_thickness_n
  ### gearbar specific
  if(ai_variant!=2):
    r_gpd['gearbar_slope'] = ai_gp_args.sw_gearbar_slope
    r_gpd['gearbar_slope_n'] = ai_gp_args.sw_gearbar_slope_n
  ### position
  # first gear position
  if(ai_variant!=4):
    r_gpd['center_position_x'] = ai_gp_args.sw_center_position_x
    r_gpd['center_position_y'] = ai_gp_args.sw_center_position_y
    r_gpd['gear_initial_angle'] = ai_gp_args.sw_gear_initial_angle
  # second gear position
  r_gpd['second_gear_position_angle'] = ai_gp_args.sw_second_gear_position_angle
  r_gpd['second_gear_additional_axis_length'] = ai_gp_args.sw_second_gear_additional_axis_length
  ### portion
  if((ai_variant!=1)and(ai_variant!=2)and(ai_variant!=4)):
    r_gpd['portion_tooth_nb'] = ai_gp_args.sw_cut_portion[0]
    r_gpd['portion_first_end'] = ai_gp_args.sw_cut_portion[1]
    r_gpd['portion_last_end'] = ai_gp_args.sw_cut_portion[2]
  ### output
  if(ai_variant!=4):
    r_gpd['gear_profile_height'] = ai_gp_args.sw_gear_profile_height
  r_gpd['simulation_enable'] = ai_gp_args.sw_simulation_enable
  r_gpd['output_file_basename'] = ai_gp_args.sw_output_file_basename
  r_gpd['return_type'] = ai_gp_args.sw_return_type
  ###### return
  return(r_gpd)

def gear_profile_argparse_wrapper(ai_gp_args, ai_args_in_txt=''):
  """
  wrapper function of gear_profile() to call it using the gear_profile_parser.
  gear_profile_parser is mostly used for debug and non-regression tests.
  """
  # run the simulation as default action
  run_simulation = False
  if(ai_gp_args.sw_simulation_enable or (ai_gp_args.sw_output_file_basename=='')):
    run_simulation = True
  #
  #print("dbg865: ai_gp_args.sw_second_gear_skin_thickness:", ai_gp_args.sw_second_gear_skin_thickness)
  # wrapper
  gpd = {}
  gpd.update(gear_profile_argparse_to_dictionary(ai_gp_args))
  gpd['args_in_txt'] = ai_args_in_txt
  gpd['simulation_enable'] = run_simulation
  #gpd['return_type'] = 'int_status'
  r_gp = gear_profile(gpd)
  return(r_gp)

################################################################
# self test
################################################################

def gear_profile_self_test():
  """
  This is the non-regression test of gear_profile.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"                    , "--gear_tooth_nb 17"],
    ["external-external simple"         , "--gear_tooth_nb 17 --second_gear_tooth_nb 21 --gear_module 10.0 --gear_skin_thickness 1.0 --gear_router_bit_radius 2.0 --simulation_enable"],
    ["external-internal simple"         , "--gear_tooth_nb 17 --second_gear_tooth_nb 23 --gear_module 10.0 --second_gear_type i --gear_router_bit_radius 1.2"],
    ["internal-external simple"         , "--gear_tooth_nb 30 --gear_type i --second_gear_tooth_nb 15 --gear_module 10 --gear_router_bit_radius 1.4"],
    ["external-linear simple"           , "--gear_tooth_nb 20 --gear_module 10 --second_gear_type l --gearbar_slope 0.3 --gearbar_slope_n 0.6 --gear_router_bit_radius 3 --second_gear_tooth_nb 5 --second_gear_router_bit_radius 2"],
    ["linear-external simple"             , "--gear_tooth_nb 17 --gear_type l --second_gear_tooth_nb 17 --gear_module 10  --second_gear_base_diameter 150 --gear_router_bit_radius 1.6"],
    ["simple reduction (ratio<1)"       , "--gear_tooth_nb 20 --second_gear_tooth_nb 25 --gear_module 10.0 --gear_skin_thickness 0.0 --gear_router_bit_radius 1.5 --gear_base_diameter 182.0 --gear_base_diameter_n 165.0"],
    ["simple transmission (ratio=1)"    , "--gear_tooth_nb 13 --second_gear_tooth_nb 13"],
    ["simple multiplication (ratio>1)"  , "--gear_tooth_nb 19 --second_gear_tooth_nb 16"],
    ["big ratio and zoom"               , "--gear_tooth_nb 19 --second_gear_tooth_nb 137"],
    ["single gear with same primitive and base circle"  , "--gear_tooth_nb 17 --gear_base_diameter 16.9"],
    ["single gear with small base circle"               , "--gear_tooth_nb 27 --gear_base_diameter 23.5"],
    ["with first and second angle and inter-axis length" , "--gear_tooth_nb 17 --second_gear_tooth_nb 21 --gear_initial_angle {:0.3f} --second_gear_position_angle {:0.3f} --second_gear_additional_axis_length 0.2".format(15*math.pi/180, 40.0*math.pi/180)],
    ["other with first and second angle"       , "--gear_tooth_nb 17 --second_gear_tooth_nb 15 --gear_initial_angle  {:0.3f} --second_gear_position_angle  {:0.3f}".format(-5*math.pi/180, 170.0*math.pi/180)],
    ["with force angle constraint"             , "--gear_tooth_nb 17 --second_gear_tooth_nb 27 --gear_force_angle {:0.3f}".format(20*math.pi/180)],
    ["first base radius constraint"            , "--gear_tooth_nb 26 --second_gear_tooth_nb 23 --gear_base_diameter 23.0"],
    ["second base radius constraint"           , "--gear_tooth_nb 17 --second_gear_tooth_nb 23 --second_gear_primitive_diameter 20.3"],
    ["fine draw resolution"                    , "--gear_tooth_nb 17 --second_gear_tooth_nb 19 --gear_tooth_resolution 10"],
    ["ratio 1 and dedendum at 30%%"            , "--gear_tooth_nb 17 --second_gear_tooth_nb 17 --gear_dedendum_height_pourcentage 30.0 --second_gear_addendum_height_pourcentage 30.0"],
    ["ratio > 1 and dedendum at 40%%"          , "--gear_tooth_nb 17 --second_gear_tooth_nb 23 --gear_dedendum_height_pourcentage 40.0 --second_gear_addendum_height_pourcentage 40.0"],
    ["ratio > 1 and addendum at 80%%"          , "--gear_tooth_nb 17 --second_gear_tooth_nb 17 --gear_addendum_height_pourcentage 80.0 --second_gear_dedendum_height_pourcentage 80.0"],
    ["ratio > 1 and dedendum at 140%%"         , "--gear_tooth_nb 17 --second_gear_tooth_nb 21 --gear_dedendum_height_pourcentage 140.0"],
    ["ratio > 1 and small tooth height"        , "--gear_tooth_nb 17 --second_gear_tooth_nb 29 --gear_tooth_half_height 0.7 --second_gear_tooth_half_height 0.8"],
    ["ratio > 1 and big tooth height"          , "--gear_tooth_nb 17 --second_gear_tooth_nb 29 --gear_tooth_half_height 1.15 --second_gear_tooth_half_height 1.17"],
    ["ratio > 1 and addendum-dedendum parity"  , "--gear_tooth_nb 30 --second_gear_tooth_nb 37 --gear_addendum_dedendum_parity 60.0 --second_gear_addendum_dedendum_parity 40.0"],
    ["slack because of addendum-dedendum parity", "--gear_tooth_nb 18 --second_gear_tooth_nb 23 --gear_addendum_dedendum_parity 48.0 --second_gear_addendum_dedendum_parity 40.0"],
    ["file generation"                         , "--gear_tooth_nb 17 --center_position_x 100 --center_position_y 50 --output_file_basename test_output/gear_profile_run_self_test.dxf"],
    ["interior gear"                           , "--gear_tooth_nb 17 --second_gear_tooth_nb 14 --gear_type i"],
    ["interior gear"                           , "--gear_tooth_nb 25 --second_gear_tooth_nb 17 --gear_type i --second_gear_position_angle {:0.3f}".format(30.0*math.pi/180)],
    ["interior second gear"                    , "--gear_tooth_nb 17 --second_gear_tooth_nb 29 --second_gear_type i"],
    ["interior second gear"                    , "--gear_tooth_nb 17 --second_gear_tooth_nb 24 --second_gear_type i --second_gear_position_angle {:0.3f}".format(-75*math.pi/180)],
    ["interior gear"                           , "--gear_tooth_nb 17 --second_gear_tooth_nb 14 --gear_type i --gear_addendum_height_pourcentage 75.0"],
    ["gearbar"                                 , "--gear_type l --gear_tooth_nb 3 --second_gear_tooth_nb 20 --gear_primitive_diameter 15 --gearbar_slope 0.3"],
    ["gearbar with angle"                      , "--gear_type l --gear_tooth_nb 12 --second_gear_tooth_nb 20 --gear_primitive_diameter 40 --gearbar_slope 0.3 --gear_initial_angle {:0.3f}".format(40*math.pi/180)],
    ["external-external asymmetric"            , "--gear_tooth_nb 18 --second_gear_tooth_nb 24 --gear_module 10.0 --gear_router_bit_radius 2.0 --gear_force_angle 0.25 --gear_force_angle 0.35"],
    ["external-internal asymmetric"            , "--gear_tooth_nb 20 --second_gear_tooth_nb 40 --gear_module 10.0 --second_gear_type i --gear_router_bit_radius 1.1 --gear_base_diameter 180 --gear_base_diameter_n 165"],
    ["internal-external asymmetric"            , "--gear_tooth_nb 32 --gear_type i --second_gear_tooth_nb 19 --gear_module 10.0 --gear_router_bit_radius 1.05 --second_gear_base_diameter 160 --second_gear_base_diameter_n 170"],
    ["external-linear asymmetric"              , "--gear_tooth_nb 22 --gear_module 10 --second_gear_type l --gearbar_slope 0.5 --gearbar_slope_n 0.2 --gear_router_bit_radius 2 --second_gear_tooth_nb 6"],
    ["linear-external asymmetric"              , "--gear_tooth_nb 8 --gear_type l --second_gear_tooth_nb 18 --gear_module 10.0 --second_gear_base_diameter 150 --second_gear_base_diameter_n 160 --gear_router_bit_radius 1.2"],
    ["external-external with angle and aal" , "--gear_tooth_nb 21 --second_gear_tooth_nb 19 --gear_module 10.0 --second_gear_position_angle 0.7 --second_gear_additional_axis_length 1.5"],
    ["external-internal with angle and aal" , "--gear_tooth_nb 20 --second_gear_type i --second_gear_tooth_nb 31 --gear_module 10.0 --second_gear_position_angle -0.5 --second_gear_additional_axis_length 2.1"],
    ["internal-external with angle and aal" , "--gear_tooth_nb 29 --gear_type i --second_gear_tooth_nb 18 --gear_module 10.0 --second_gear_position_angle 1.8 --second_gear_additional_axis_length 1.3"],
    ["external-linear with angle and aal"   , "--gear_tooth_nb 23 --second_gear_type l --second_gear_tooth_nb 8 --gear_module 10.0 --second_gear_position_angle 0.3 --second_gear_additional_axis_length 1.2"],
    ["linear-external with angle and aal"   , "--gear_tooth_nb 10 --gear_type l --second_gear_tooth_nb 19 --gear_module 10.0 --second_gear_base_diameter 160 --gear_router_bit_radius 1.3 --second_gear_position_angle 1.5708 --second_gear_additional_axis_length 1.5"],
    ["external-external with angle and negative aal" , "--gear_tooth_nb 21 --second_gear_tooth_nb 19 --gear_module 10.0 --second_gear_position_angle 2.1 --second_gear_additional_axis_length -1.8"],
    ["gear_portion 0 1"                    , "--gear_tooth_nb 24 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --cut_portion 10 0 1"],
    ["gear_portion 1 2 with big base"      , "--gear_tooth_nb 24 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --cut_portion 10 1 2 --gear_base_diameter 460"],
    ["gear_portion 2 3"                    , "--gear_tooth_nb 24 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --cut_portion 10 2 3"],
    ["gear_portion 3 0"                    , "--gear_tooth_nb 24 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --cut_portion 10 3 0"],
    ["gear_portion 3 2"                    , "--gear_tooth_nb 24 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --cut_portion 10 3 2 --gear_base_diameter 460"],
    ["gear_portion 2 3"                    , "--gear_tooth_nb 24 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 3.0 --cut_portion 10 2 3 --gear_base_diameter 400"],
    ["skin_thickness >0"                   , "--gear_tooth_nb 25 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --gear_skin_thickness 1.0"],
    ["skin_thickness >0 asymmetric"        , "--gear_tooth_nb 25 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --gear_skin_thickness 1.0 --gear_skin_thickness_n 1.5 --second_gear_skin_thickness 1"],
    ["skin_thickness <0 asymmetric"        , "--gear_tooth_nb 25 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --gear_skin_thickness -1.0 --gear_skin_thickness_n -1.5 --second_gear_skin_thickness 0"],
    ["skin_thickness full asymmetric"      , "--gear_tooth_nb 25 --second_gear_tooth_nb 18 --gear_module 20.0 --gear_router_bit_radius 2.0 --gear_skin_thickness -1.0 --gear_skin_thickness_n 1.5 --second_gear_skin_thickness 0"]]

  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gear_profile_parser = argparse.ArgumentParser(description='Command line interface for the function gear_profile().')
  gear_profile_parser = gear_profile_add_argument(gear_profile_parser, 0)
  gear_profile_parser = cnc25d_api.generate_output_file_add_argument(gear_profile_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gear_profile_parser.parse_args(l_args)
    r_gpst = gear_profile_argparse_wrapper(st_args)
  return(r_gpst)

################################################################
# gear_profile command line interface
################################################################

def gear_profile_cli(ai_args=""):
  """ command line interface of gear_profile.py when it is used in standalone
  """
  # gear_profile parser
  gear_profile_parser = argparse.ArgumentParser(description='Command line interface for the function gear_profile().')
  gear_profile_parser = gear_profile_add_argument(gear_profile_parser, 0)
  gear_profile_parser = cnc25d_api.generate_output_file_add_argument(gear_profile_parser, 1)
  # add switch for self_test
  gear_profile_parser.add_argument('--run_self_test','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "gear_profile arguments: " + ' '.join(effective_args)
  #print("dbg557: effective_args:", effective_args)
  gp_args = gear_profile_parser.parse_args(effective_args)
  print("dbg111: start making gear_profile")
  if(gp_args.sw_run_self_test):
    r_gp = gear_profile_self_test()
  else:
    r_gp = gear_profile_argparse_wrapper(gp_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_gp)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gear_profile.py says hello!\n")
  #my_gp = gear_profile_cli()
  #my_gp = gear_profile_cli("--gear_tooth_nb 17")
  #my_gp = gear_profile_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0")
  #my_gp = gear_profile_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --second_gear_tooth_nb 20 --return_type freecad_object")
  my_gp = gear_profile_cli("--gear_tooth_nb 17 --gear_module 10 --gear_router_bit_radius 3.0 --second_gear_tooth_nb 20")
  #my_gp = gear_profile_cli("--gear_tooth_nb 17 --output_file_basename test_output/toto1")
  #my_gp = gear_profile_cli("--gear_tooth_nb 17 --output_file_basename gear_profile_example_1.svg")
  #my_gp = gear_profile_cli("--gear_tooth_nb 17 --cut_portion 7 3 3 --output_file_basename gear_profile_example_2.svg")
  #my_gp = gear_profile_cli("--gear_tooth_nb 20 --gear_force_angle {:0.3f} --gear_force_angle_n {:0.3f} --output_file_basename gear_profile_example_3.svg".format(25*math.pi/180, 35*math.pi/180,))
  try: # depending on gp_c['return_type'] it might be or not a freecad_object
    Part.show(my_gp)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")


