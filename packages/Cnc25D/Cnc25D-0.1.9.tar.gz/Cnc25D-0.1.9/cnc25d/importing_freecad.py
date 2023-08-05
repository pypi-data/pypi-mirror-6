# importing_freecad.py
# a function that replace in a more sophisticated way the import FreeCAD.
# created by charlyoleg on 2013/05/17
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


'''
importing_freecad.py finds out where is located FreeCAD on a host and import it to be used in Python script.
If FreeCAD is not found, you may want to edit this file and add the appropriate path to the FREECADPATH list.
'''

################################################################
# settings
################################################################

FREECADPATH=['/usr/lib/freecad/lib'] # add the path to the file FreeCAD.so to this list
#FREECADPATH=['/uuu/lib/freecad/lib', '/usr/lib/freecad/lib'] 
#FREECADPATH=['/uuu/lib/freecad/lib'] 

################################################################
# import
################################################################

import sys, os

################################################################
# function
################################################################

def importing_freecad():
  ''' This function looks for the FreeCAD library and import it if needed
      just call this function where you want to import FreeCAD
  '''
  # choose your favorite test to check if you are running with FreeCAD GUI or traditional Python
  freecad_gui = True
  #if not(FREECADPATH in sys.path): # test based on PYTHONPATH
  if not("FreeCAD" in dir()):       # test based on loaded module
    freecad_gui = False
  #print("dbg102: freecad_gui:", freecad_gui)
  
  if not(freecad_gui):
    freecad_path=''
    for p in FREECADPATH:
      if(os.path.isfile("%s/FreeCAD.so"%(p))):
        freecad_path=p
    if(freecad_path==''):
      print("ERR070: Error, the FreeCAD library path has not been found!")
      print("Add the path of the directory containing FreeCAD.so to the variable FREECADPATH in the file {:s}".format(__FILE__))
      sys.exit(2)
    #print("dbg101: add FREECADPATH to sys.path")
    sys.path.append(freecad_path)
    try:
      import FreeCAD
    except:
      print("ERR080: Error, the FreeCAD library can not be imported by cnc25d!")
      sys.exit(2)

################################################################
# main : only useful for debug
################################################################

if(__name__ == "__main__"):
  importing_freecad()
  print("FreeCAD.Version:", FreeCAD.Version())
  FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n")

