# gear_profile_macro.py
# the macro to generate a gear_profile.
# created by charlyoleg on 2013/08/27
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


################################################################
# this file intends being included in the file bin/cnc25d_example_generator.py
# for this purpose, there is some syntaxe restrictions
# don't use triple single-quotes (') and return character ('\'.'n') in this file
# but you can still use triple double-quote (")
################################################################

"""
this piece of code is an example of how to use the parametric design gear_profile
You can also use this file as a FreeCAD macro from the GUI
You can also copy-paste this code in your own design files
If you don't know which value to set to a constraint-parameter, just comment it. Default value is used, if you don't set a constraint explicitly.
"""

################################################################
# Installation pre-request
################################################################
# This script needs freecad and Cnc25D installed on your system
# visit those sites for more information:
# http://www.freecadweb.org/
# https://pypi.python.org/pypi/Cnc25D
#
# To install FreeCAD on Ubuntu, run the following command:
# > sudo apt-get install freecad
# or to get the newest version:
# > sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
# > sudo apt-get update
# > sudo apt-get install freecad
# and optionally:
# >  sudo apt-get install freecad-doc freecad-dev
# To install the python package cnc25d, run the following command:
# > sudo pip install Cnc25D
# or
# > sudo pip install Cnc25D -U


################################################################
# header for Python / FreeCAD compatibility
################################################################

try: # when working with an installed Cnc25D package
  from cnc25d import cnc25d_api
except:    # when working on the source files
  import importing_cnc25d # give access to the cnc25d package
  from cnc25d import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())

################################################################
# import
################################################################

#
import math
#
from cnc25d import gear_profile
#
import Part

    
################################################################
# parameters value
################################################################
#
# choose the values of the parameters by editing this file
# feature request : create a GUI with PyQt4 to edit those parameter values

gp_constraint = {}
### first gear
# general
gp_constraint['gear_type']                      = 'e'
gp_constraint['gear_tooth_nb']                  = 18
gp_constraint['gear_module']                    = 10.0
gp_constraint['gear_primitive_diameter']        = 0
gp_constraint['gear_addendum_dedendum_parity']  = 50.0
# tooth height
gp_constraint['gear_tooth_half_height']           = 0 # 10.0
gp_constraint['gear_addendum_height_pourcentage'] = 100.0
gp_constraint['gear_dedendum_height_pourcentage'] = 100.0
gp_constraint['gear_hollow_height_pourcentage']   = 25.0
gp_constraint['gear_router_bit_radius']           = 3.0
# positive involute
gp_constraint['gear_base_diameter']       = 0
gp_constraint['gear_force_angle']         = 0
gp_constraint['gear_tooth_resolution']    = 2
gp_constraint['gear_skin_thickness']      = 0
# negative involute (if zero, negative involute = positive involute)
gp_constraint['gear_base_diameter_n']     = 0
gp_constraint['gear_force_angle_n']       = 0
gp_constraint['gear_tooth_resolution_n']  = 0
gp_constraint['gear_skin_thickness_n']    = 0
### second gear
# general
gp_constraint['second_gear_type']                     = 'e'
gp_constraint['second_gear_tooth_nb']                 = 25
gp_constraint['second_gear_primitive_diameter']       = 0
gp_constraint['second_gear_addendum_dedendum_parity'] = 0 # 50.0
# tooth height
gp_constraint['second_gear_tooth_half_height']            = 0
gp_constraint['second_gear_addendum_height_pourcentage']  = 100.0
gp_constraint['second_gear_dedendum_height_pourcentage']  = 100.0
gp_constraint['second_gear_hollow_height_pourcentage']    = 25.0
gp_constraint['second_gear_router_bit_radius']            = 0
# positive involute
gp_constraint['second_gear_base_diameter']      = 0
gp_constraint['second_gear_tooth_resolution']   = 0
gp_constraint['second_gear_skin_thickness']     = 0
# negative involute (if zero, negative involute = positive involute)
gp_constraint['second_gear_base_diameter_n']    = 0
gp_constraint['second_gear_tooth_resolution_n'] = 0
gp_constraint['second_gear_skin_thickness_n']   = 0
### gearbar specific
gp_constraint['gearbar_slope']                  = 0.0
gp_constraint['gearbar_slope_n']                = 0.0
### position
# first gear position
gp_constraint['center_position_x']                    = 0.0
gp_constraint['center_position_y']                    = 0.0
gp_constraint['gear_initial_angle']                   = 0.0
# second gear position
gp_constraint['second_gear_position_angle']           = 0.0
gp_constraint['second_gear_additional_axis_length']   = 0.0
### portion
gp_constraint['cut_portion']     = (10, 3, 3) # (portion_tooth_nb, portion_first_end, portion_last_end)
### z-dimension
gp_constraint['gear_profile_height']  = 20.0



################################################################
# action
################################################################

my_gp = gear_profile.gear_profile(gp_constraint)
my_gp.outline_display()
my_gp.write_figure_svg("test_output/gear_profile_macro")
my_gp.write_figure_dxf("test_output/gear_profile_macro")
my_gp.write_figure_brep("test_output/gear_profile_macro")
my_gp.write_assembly_brep("test_output/gear_profile_macro")
my_gp.write_freecad_brep("test_output/gear_profile_macro")
my_gp.run_simulation("")
my_gp.view_design_configuration()
#my_gp.run_self_test("")
#my_gp.cli("--output_file_basename test_output/gpm.dxf") # Warning: all constraint values are reset to their default values

if(cnc25d_api.interpretor_is_freecad()):
  Part.show(my_gp.get_fc_obj_3dconf('gp_assembly_conf1'))


