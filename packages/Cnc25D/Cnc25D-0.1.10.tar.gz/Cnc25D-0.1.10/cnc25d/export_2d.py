# export_2d.py
# functions to help to generate 2D dxf and svg plan.
# created by charlyoleg on 2013/05/31
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
export_2d.py provides functions to create DXF file from a FreeCAD Part Oject
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import Part
from FreeCAD import Base
import importDXF
import Drawing
#import FreeCADGui

################################################################
# export_2d sub-functions
################################################################

def draw_rectangle(ai_position_x, ai_position_y, ai_size_x, ai_size_y):
  p1 = Base.Vector(ai_position_x+0*ai_size_x, ai_position_y+0*ai_size_y, 0)
  p2 = Base.Vector(ai_position_x+1*ai_size_x, ai_position_y+0*ai_size_y, 0)
  p3 = Base.Vector(ai_position_x+1*ai_size_x, ai_position_y+1*ai_size_y, 0)
  p4 = Base.Vector(ai_position_x+0*ai_size_x, ai_position_y+1*ai_size_y, 0)
  r_rectangle_outline=[]
  r_rectangle_outline.append(Part.makeLine(p1, p2))
  r_rectangle_outline.append(Part.makeLine(p2, p3))
  r_rectangle_outline.append(Part.makeLine(p3, p4))
  r_rectangle_outline.append(Part.makeLine(p4, p1))
  #r_rectangle = Part.Face(Part.Wire(r_rectangle_outline))
  r_rectangle = r_rectangle_outline
  return(r_rectangle)

def draw_gauge(ai_drawing_length, ai_drawing_height, ai_representation_max, ai_representation_value, ai_position_x, ai_position_y):
  l_gauge_value = ai_drawing_length*ai_representation_value/float(ai_representation_max)
  #print("dbg067: l_gauge_value:", l_gauge_value)
  r_gauge = []
  r_gauge.extend(draw_rectangle(ai_position_x-ai_drawing_height/2.0, ai_position_y, ai_drawing_length+ai_drawing_height, ai_drawing_height))
  r_gauge.extend(draw_rectangle(ai_position_x, ai_position_y+ai_drawing_height/4.0, l_gauge_value, ai_drawing_height/2.0))
  return(r_gauge)

################################################################
# export_2d API
################################################################

def export_to_dxf_abandoned(ai_solid, ai_vector, ai_depth, ai_output_file): # it works only the FreeCAD Gui
  """ [Obsolete] create a DXF of a slice of FreeCAD Part Object
  """
  l_slices = ai_solid.slice(ai_vector, ai_depth)
  l_doc = App.newDocument("tmp_doc")
  i=0
  for l_shape in l_slices:
    i += 1
    l_obj = l_doc.addObject("Part::Feature","MyShape{:02d}".format(i))
    #l_doc.MyShape.Shape = l_shape
    #App.ActiveDocument.MyShape.Shape = l_shape
    l_obj.Shape = l_shape
  #l_doc.recompute()
  l_objects = App.ActiveDocument.Objects
  #l_objects = FreeCAD.ActiveDocument.Objects
  # this work with the gui but not in pure python script
  # Suspect root cause:
  # /usr/lib/freecad/Mod/Draft/importDXF.py line:49
  # it seems it doesn't detect the gui is off
  importDXF.export(l_objects, ai_output_file) 
  return(1)

def export_to_dxf(ai_solid, ai_vector, ai_depth, ai_output_file):
  """ create a DXF of a slice of FreeCAD Part Object
  """
  l_slice = Part.makeCompound(ai_solid.slice(ai_vector, ai_depth)) # slice the plank in the ai_vector plan at a the height ai_depth
  r_dxf = Drawing.projectToDXF(l_slice, ai_vector)
  #r_dxf = Drawing.projectToDXF(ai_solid, ai_vector) # works also :)
  fh_output = open(ai_output_file, 'w')
  fh_output.write(r_dxf)
  fh_output.close()
  return(1)
    
def export_to_svg(ai_solid, ai_vector, ai_depth, ai_output_file):
  """ create a SVG of a slice of FreeCAD Part Object. The generated SVG is incomplete. SVG header must be added to it to be opened by Inkscape
  """
  l_slice = Part.makeCompound(ai_solid.slice(ai_vector, ai_depth)) # slice the plank in the ai_vector plan at a the height ai_depth
  r_dxf = Drawing.projectToSVG(l_slice, ai_vector) # it generates a snippet of svg not directly usable by Inkscape. It needs the svg head and document markers.
  #r_dxf = Drawing.projectToSVG(ai_solid, ai_vector) # works also :)
  fh_output = open(ai_output_file, 'w')
  fh_output.write(r_dxf)
  fh_output.close()
  return(1)

def export_xyz_to_dxf(ai_solid, ai_size_x, ai_size_y, ai_size_z, ai_xy_slice_list, ai_xz_slice_list, ai_yz_slice_list, ai_output_file):
  """ Cut a FreeCAD Part Object in many slices in the three directions X, Y and Z and put all those slices in a DXF file
  """
  # calculate the space between two drawings
  l_space = max(ai_size_x/5.0, ai_size_y/5.0, ai_size_z/5.0)
  #
  vec_z_unit = Base.Vector(0,0,1)
  #
  l_slice_list = []
  l_pos_y = 0
  for lo in ['xy','xz','yz']:
    #l_solid = ai_solid
    l_solid = ai_solid.copy()
    l_depth_list = []
    l_shift_x = 0
    l_gauge_max = 0
    if(lo=='xy'):
      l_solid.rotate(Base.Vector(ai_size_x/2.0, ai_size_y/2.0, ai_size_z/2.0), Base.Vector(0,0,1), 0)
      l_solid.translate(Base.Vector(0,0,0)) # place the module corner at origin (0,0,0)
      l_solid.translate(Base.Vector(0,2*ai_size_z+7*l_space,0))
      l_pos_y = 2*ai_size_z+6*l_space
      l_depth_list = ai_xy_slice_list
      l_shift_x = ai_size_x
      l_gauge_max = ai_size_z
    elif(lo=='xz'):
      l_solid.rotate(Base.Vector(ai_size_x/2.0, ai_size_y/2.0, ai_size_z/2.0), Base.Vector(1,0,0), -90)
      l_solid.translate(Base.Vector((ai_size_x-ai_size_x)/2.0, (ai_size_z-ai_size_y)/2.0, (ai_size_y-ai_size_z)/2.0)) # place the module corner at origin (0,0,0)
      l_solid.translate(Base.Vector(0,1*ai_size_z+4*l_space,0))
      l_pos_y = 1*ai_size_z+3*l_space
      l_depth_list = ai_xz_slice_list
      l_shift_x = ai_size_x
      l_gauge_max = ai_size_y
    elif(lo=='yz'):
      l_solid.rotate(Base.Vector(ai_size_x/2.0, ai_size_y/2.0, ai_size_z/2.0), Base.Vector(0,0,1), -90)
      l_solid.rotate(Base.Vector(ai_size_x/2.0, ai_size_y/2.0, ai_size_z/2.0), Base.Vector(1,0,0), -90)
      l_solid.translate(Base.Vector((ai_size_y-ai_size_x)/2.0, (ai_size_z-ai_size_y)/2.0, (ai_size_x-ai_size_z)/2.0)) # place the module corner at origin (0,0,0)
      l_solid.translate(Base.Vector(0,l_space,0))
      l_pos_y = 0*ai_size_z+0*l_space
      l_depth_list = ai_yz_slice_list
      l_shift_x = ai_size_y
      l_gauge_max = ai_size_x
    l_pos_x = 0
    for l_depth in l_depth_list:
      #print("dbg163: l_shift_x l_space l_gauge_max l_depth l_pos_x l_pos_y", l_shift_x, l_space, l_gauge_max, l_depth, l_pos_x, l_pos_y)
      l_slice_list.extend(draw_gauge(l_shift_x, l_space/2.0, l_gauge_max, l_depth, l_pos_x, l_pos_y))
      l_pos_x += l_shift_x+2*l_space
      ll_depth = l_depth
      if(lo=='xz'):
        ll_depth = ai_size_y-l_depth
      #print("dbg168: ll_depth:", ll_depth)
      l_slice_list.extend(l_solid.slice(vec_z_unit, ll_depth))
      l_solid.translate(Base.Vector(l_shift_x+2*l_space,0,0))
  l_slice = Part.makeCompound(l_slice_list)
  r_dxf = Drawing.projectToDXF(l_slice, vec_z_unit)
  #r_dxf = Drawing.projectToDXF(ai_solid, ai_vector)
  fh_output = open(ai_output_file, 'w')
  fh_output.write(r_dxf)
  fh_output.close()
  return(1)
    
