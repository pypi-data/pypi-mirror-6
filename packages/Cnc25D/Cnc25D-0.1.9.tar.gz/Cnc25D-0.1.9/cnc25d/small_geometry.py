# small_geometry.py
# a help module for cnc_cut_outline.py, just to avoid to get too big files
# created by charlyoleg on 2013/07/30
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
small_geometry.py provides sub functions for cnc_cut_outline.py related to the Euclid geometry
"""

################################################################
# python behavior
################################################################

from __future__ import division # to get float division


################################################################
# import
################################################################

#import outline_backends # for testing only
#
import math
import sys, argparse

################################################################
# functions to be used by cnc_cut_outline.py
################################################################

def rotate_point(ai_point, ai_ox, ai_oy, ai_rotation_angle):
  """ Rotation of the point ai_point of center (ai_ox, ai_oy) and angle ai_rotation_angle
  """
  ix = ai_point[0]-ai_ox
  iy = ai_point[1]-ai_oy
  pt_x = ai_ox+ix*math.cos(ai_rotation_angle)-iy*math.sin(ai_rotation_angle)
  pt_y = ai_oy+ix*math.sin(ai_rotation_angle)+iy*math.cos(ai_rotation_angle)
  r_point = [pt_x, pt_y]
  return(r_point)

def arc_center_radius(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_error_msg_id):
  """ Compute the center of the arc defined by the three points A,B and C
  """
  #print("dbg197: ai_error_msg_id: {:s}".format(ai_error_msg_id))
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the arc three points A,B,C
  AX = ai_arc_pt1[0]
  AY = ai_arc_pt1[1]
  BX = ai_arc_pt2[0]
  BY = ai_arc_pt2[1]
  CX = ai_arc_pt3[0]
  CY = ai_arc_pt3[1]
  # check of the lenght AB, BC, AC
  AB = math.sqrt((BX-AX)**2+(BY-AY)**2)
  BC = math.sqrt((CX-BX)**2+(CY-BY)**2)
  AC = math.sqrt((CX-AX)**2+(CY-AY)**2)
  if((AB<radian_epsilon)or(BC<radian_epsilon)or(AC<radian_epsilon)):
    print("ERR682: Error in {:s}, the three arc points ABC are too closed: AB={:0.2f} BC={:0.2f} AC={:0.2f}".format(ai_error_msg_id, AB, BC, AC))
    sys.exit(2)
  # calculation of M and N
  MX = (AX+BX)/2
  MY = (AY+BY)/2
  NX = (BX+CX)/2
  NY = (BY+CY)/2
  # calculation of e and f
  cos_e = (BX-AX)/AB
  sin_e = (BY-AY)/AB
  cos_f = (CX-BX)/BC
  sin_f = (CY-BY)/BC
  # calculation de I
  #(cos(e)*sin(f)-cos(f)*sin(e))*x = sin(f)*(cos(e)*xM+sin(e)*yM)-sin(e)*(cos(f)*xN+sin(f)*yN)
  #(sin(e)*cos(f)-sin(f)*cos(e))*y = cos(f)*(cos(e)*xM+sin(e)*yM)-cos(e)*(cos(f)*xN+sin(f)*yN)
  # ixl = (cos(e)*sin(f)-cos(f)*sin(e))
  # iyl = (sin(e)*cos(f)-sin(f)*cos(e))
  # ixk = sin(f)*(cos(e)*xM+sin(e)*yM)-sin(e)*(cos(f)*xN+sin(f)*yN)
  # iyk = cos(f)*(cos(e)*xM+sin(e)*yM)-cos(e)*(cos(f)*xN+sin(f)*yN)
  ixl = cos_e*sin_f-cos_f*sin_e
  iyl = sin_e*cos_f-sin_f*cos_e
  ixk = sin_f*(cos_e*MX+sin_e*MY)-sin_e*(cos_f*NX+sin_f*NY)
  iyk = cos_f*(cos_e*MX+sin_e*MY)-cos_e*(cos_f*NX+sin_f*NY)
  if((abs(ixl)<radian_epsilon)or(abs(iyl)<radian_epsilon)):
    print("ERR947: Error in {:s}, ixl (= {:0.2f}) or iyl (= {:0.2f}) are too closed to zero!".format(ai_error_msg_id, ixl, iyl))
    sys.exit(2)
  IX=ixk/ixl
  IY=iyk/iyl
  # check than I is equidistant of A, B and C
  IA = math.sqrt((AX-IX)**2+(AY-IY)**2)
  IB = math.sqrt((BX-IX)**2+(BY-IY)**2)
  IC = math.sqrt((CX-IX)**2+(CY-IY)**2)
  if((abs(IB-IA)>radian_epsilon)or(abs(IC-IA)>radian_epsilon)):
    print("ERR748: Error in {:s}, the calculation of the center of the arc A,B,C is wrong! IA={:0.2f} IB={:0.2f} IC={:0.2f}".format(ai_error_msg_id, IA, IB, IC))
    print("dbg253: A= {:0.2f} {:0.2f}  B= {:0.2f} {:0.2f}  C= {:0.2f} {:0.2f}  I= {:0.2f} {:0.2f}".format(AX,AY,BX,BY,CX,CY,IX,IY))
    print("dbg764: cos_e={:0.2f}  sin_e={:0.2f}  cos_f={:0.2f}  sin_f={:0.2f}".format(cos_e, sin_e, cos_f, sin_f))
    print("dbg765: ixl={:0.2f} ixk={:0.2f} iyl={:0.2f} iyk={:0.2f}".format(ixl, ixk, iyl, iyk))
    print("dbg766: MX={:0.2f} MY={:0.2f} NX={:0.2f} NY={:0.2f}".format(MX,MY,NX,NY))
    sys.exit(2)
  # return
  r_arc_center_radius=(IX, IY, IA)
  return(r_arc_center_radius)

def arc_center_radius_angles(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_error_msg_id):
  """ Compute the center, radius and angles of the arc defined by the three points A,B and C
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_arc_pt1[0]
  AY = ai_arc_pt1[1]
  BX = ai_arc_pt2[0]
  BY = ai_arc_pt2[1]
  CX = ai_arc_pt3[0]
  CY = ai_arc_pt3[1]
  # calculation of I
  (IX,IY, arc_radius) = arc_center_radius(ai_arc_pt1, ai_arc_pt2, ai_arc_pt3, ai_error_msg_id)
  # check I is equidistant of A,B,C,D,E
  IA = math.sqrt((AX-IX)**2+(AY-IY)**2)
  IB = math.sqrt((BX-IX)**2+(BY-IY)**2)
  IC = math.sqrt((CX-IX)**2+(CY-IY)**2)
  if((abs(IA-arc_radius)>radian_epsilon)or(abs(IB-arc_radius)>radian_epsilon)or(abs(IC-arc_radius)>radian_epsilon)):
    print("ERR841: Error, in {:s}, I is not equidistant from A,B,C. arc_radius={:0.2f} IA={:0.2f} IB={:0.2f} IC={:0.2f}".format(ai_error_msg_id, arc_radius, IA, IB, IC))
    sys.exit(2)
  # calculation of the angle u=(Ix, IA) , v=(Ix, IB), w=(Ix, IC), d=(Ix, ID) and e=(Ix, IE)
  u = math.atan2(AY-IY, AX-IX)
  v = math.atan2(BY-IY, BX-IX)
  w = math.atan2(CY-IY, CX-IX)
  # calculation of the angle uv=(IA, IB), uw=(IA, IC)
  uv = math.fmod(v-u+4*math.pi, 2*math.pi)
  uw = math.fmod(w-u+4*math.pi, 2*math.pi)
  # check arc direction
  ccw_ncw = True
  if(uw>uv):
    #print("dbg874: arc of circle direction: counter clock wise (CCW)")
    ccw_ncw = True
  else:
    #print("dbg875: arc of circle direction: clock wise (CW)")
    ccw_ncw = False
    uv = uv - 2*math.pi
    uw = uw - 2*math.pi
  # return
  r_arc_center_radius_angles=(IX, IY, IA, uw, u, w)
  return(r_arc_center_radius_angles)

# aka circle_circle_intersection
def triangulation(ai_A, ai_AC, ai_B, ai_BC, ai_D, ai_D_direction, ai_error_msg_id):
  """ knowing the coordiantes of A and B and the lengths AC and BC, returns the coordinates of C
      C is placed on the same side as D compare to the line (AB)
      If D is too closed to the line (AB), the D_direction is used to identified the side to place C
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # code error
  r_status = 0
  # check the arguments
  if((ai_AC<radian_epsilon)or(ai_BC<radian_epsilon)):
    print("ERR965: Error in {:s}, the length ai_AC (={:0.2f}) or ai_BC (={:0.2f})".format(ai_error_msg_id, ai_AC, ai_BC))
    sys.exir(2)
  # interprete the arguments
  AX = ai_A[0]
  AY = ai_A[1]
  b = ai_AC
  BX = ai_B[0]
  BY = ai_B[1]
  a = ai_BC
  DX = ai_D[0]
  DY = ai_D[1]
  # calculation of the length c=AB
  c = math.sqrt((BX-AX)**2+(BY-AY)**2)
  if(c<radian_epsilon):
    print("ERR662: Error in {:s}, the length c (=AB={:0.2f}) is too small!".format(ai_error_msg_id, c))
    sys.exit(2)
  # calculation of the angle A with the law of cosines
  #BAC = math.acos((b**2+c**2-a**2)/(2*b*c))
  cos_BAC = (b**2+c**2-a**2)/(2*b*c)
  if(abs(cos_BAC)>1):
    print("ERR542: Error in {:s}, cos_BAC is out of [-1,1]! a={:0.2f} b={:0.2f} c={:0.2f} cos_BAC={:0.2f}".format(ai_error_msg_id, a, b, c, cos_BAC))
    print("dbg652: AX={:0.2f} AY={:0.2f} BX={:0.2f} BY={:0.2f}".format(AX,AY,BX,BY))
    #sys.exit(2)
    r_status=2
    return((0,0,r_status))
  BAC = math.acos(cos_BAC)
  # calculation of the angle xAB
  xAB = math.atan2(BY-AY, BX-AX)
  # calculation of the angle BAD
  xAD =  math.atan2(DY-AY, DX-AX) # atan2 avoid the problem of divided by zero
  BAD = math.fmod(xAD - xAB + 5*math.pi, 2*math.pi) - math.pi
  if(abs(BAD)<radian_epsilon):
    print("WARN546: Warning in {:s}, the side of the triangulation is not clear! Use the ai_D_direction".format(ai_error_msg_id))
    DX1 = DX+5*radian_epsilon*math.cos(ai_D_direction)
    DY1 = DY+5*radian_epsilon*math.sin(ai_D_direction)
    xAD =  math.atan2(DY1-AY, DX1-AX) # atan2 avoid the problem of divided by zero
    BAD = math.fmod(xAD - xAB + 5*math.pi, 2*math.pi) - math.pi
  # calculation of the angle xAC
  xAC = xAB + math.copysign(BAC, BAD)
  # calculation of the coordinates of C
  CX = AX+b*math.cos(xAC)
  CY = AY+b*math.sin(xAC)
  # for verification, duplication of the calculation via B
  ABC = math.acos((a**2+c**2-b**2)/(2*a*c))
  xBA = math.atan2(AY-BY, AX-BX) # = xAB+math.pi
  #BD = math.sqrt((DX-BX)**2+(DY-BY)**2)
  xBD = math.atan2(DY-BY, DX-BX)
  ABD = math.fmod(xBD - xBA + 5*math.pi, 2*math.pi) - math.pi
  if(abs(ABD)<radian_epsilon):
    print("WARN547: Warning in {:s}, the side of the triangulation is not clear! Use the ai_D_direction".format(ai_error_msg_id))
    DX1 = DX+5*radian_epsilon*math.cos(ai_D_direction)
    DY1 = DY+5*radian_epsilon*math.sin(ai_D_direction)
    xBD = math.atan2(DY1-BY, DX1-BX)
    ABD = math.fmod(xBD - xBA + 5*math.pi, 2*math.pi) - math.pi
  xBC = xBA + math.copysign(ABC, ABD)
  CX2 = BX+a*math.cos(xBC)
  CY2 = BY+a*math.sin(xBC)
  if((abs(CX2-CX)>radian_epsilon)or(abs(CY2-CY)>radian_epsilon)):
    print("ERR686: Error in {:s}, the coordinate of C seems wrong! CX={:0.2f} CX2={:0.2f} CY={:0.2f} CY2={:0.2f}".format(ai_error_msg_id, CX, CX2, CY, CY2))
    print("dbg545: D {:0.2f} {:0.2f}  ai_D_direction {:0.2f}".format(DX,DY, ai_D_direction))
    print("dbg512: BAC", BAC)
    print("dbg513: xAB", xAB)
    #print("dbg514: AD", AD)
    print("dbg515: BAD", BAD)
    print("dbg516: xAC", xAC)
    print("dbg517: AX {:0.2f}  AY {:0.2f}  b {:0.2f}".format(AX,AY, b))
    print("dbg522: ABC", ABC)
    print("dbg523: xBA", xBA)
    #print("dbg524: BD", BD)
    print("dbg525: ABD", ABD)
    print("dbg526: xBC", xBC)
    print("dbg527: BX {:0.2f}  BY {:0.2f}  a {:0.2f}".format(BX,BY, a))
    sys.exit(2)
  r_C = (CX,CY,r_status)
  return(r_C)

def line_equation(ai_A, ai_B, ai_error_msg_id):
  """ Given the coordinates of two points, it returns the three coefficient of the line equation, the length of the segment and the inclination
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_A[0]
  AY = ai_A[1]
  BX = ai_B[0]
  BY = ai_B[1]
  # calculation of the length AB
  lAB = math.sqrt((BX-AX)**2+(BY-AY)**2)
  if(lAB<radian_epsilon):
    print("ERR261: Error, lAB {:0.3f} is too small".format(lAB))
    sys.exit(2)
  # calculation of the inclination of AB
  xAB = math.atan2(BY-AY, BX-AX)
  cos_xAB = (BX-AX)/lAB
  sin_xAB = (BY-AY)/lAB
  # calculation of the line equation coefficient : ABlx * x + ABly * y + ABk = 0
  # ABlx = sin(xAB)
  ABlx = sin_xAB
  # ABly = -cos(xAB)
  ABly = -cos_xAB
  # ABk = -(ABlx*AX+ABly*AY)
  ABk = -(ABlx*AX+ABly*AY)
  # return
  r_line_equation = (ABlx, ABly, ABk, lAB, xAB)
  return(r_line_equation)

def line_distance_point(ai_A, ai_B, ai_q, ai_error_msg_id):
  """ Given the two points A and B and the distance q, what are the coordinates of Q, distance of q from A and AB
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  AX = ai_A[0]
  AY = ai_A[1]
  BX = ai_B[0]
  BY = ai_B[1]
  # line equation of AB
  #(ABlx, ABly, ABkA, lAB, xAB) = line_equation(ai_A, ai_B, ai_error_msg_id)
  lAB = math.sqrt((BX-AX)**2+(BY-AY)**2)
  cos_xAB = (BX-AX)/lAB
  sin_xAB = (BY-AY)/lAB
  ABlx = sin_xAB
  ABly = -cos_xAB
  # calculation of Q
  # QX = AX+q*cos(xAB+pi/2) = AX-q*sin(xAB)
  # QY = AX+q*sin(xAB+pi/2) = AX+q*cos(xAB)
  QX = AX-ai_q*sin_xAB
  QY = AY+ai_q*cos_xAB
  ABkQ = -(ABlx*QX+ABly*QY)
  # return
  r_Q = (QX, QY, ABkQ)
  return(r_Q)

def line_point_projection(ai_AB, ai_M, ai_error_msg_id):
  """ Given the line equation of AB (ABlx, AVly, ABk) and the coordinates of M (MX,MY), returns the coordinates of P, projection of M on AB
  """
  # use to check is angle is smaller than pi/2
  #radian_epsilon = math.pi/1000
  # interpretation of the input points
  a = ai_AB[0] # ABlx
  b = ai_AB[1] # ABly
  c = ai_AB[2] # ABk
  MX = ai_M[0]
  MY = ai_M[1]
  # calculation of d (MPk, coefficient of the line equation of PM)
  d = -(b*MX-a*MY) # MPk
  # calculation of the coordinates of P
  PX = -(c*a+d*b)
  PY = d*a-c*b
  # return
  r_P = (PX, PY)
  return(r_P)

def line_circle_intersection(ai_AB, ai_I, ai_R, ai_C, ai_D_direction, ai_error_msg_id):
  """ Given the line equation (a*x+b*y+c=0) and the circle of center I and radius R, returns the intersection M
      C define the side of the intersection
      D_direction is used if C is too closed to the border. Set it to zero if you don't know how to set it.
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # status for error forward
  line_circle_intersection_status = 0
  r_line_circle_intersection = (0, 0, line_circle_intersection_status)
  # interpretation of the input points
  a = ai_AB[0] # ABlx
  b = ai_AB[1] # ABly
  c = ai_AB[2] # ABk
  IX = ai_I[0]
  IY = ai_I[1]
  CX = ai_C[0]
  CY = ai_C[1]
  # calculation of the coordinates of P, projection of I on AB
  (PX, PY) = line_point_projection(ai_AB, ai_I, ai_error_msg_id)
  # calculation of the coordinates of C2, projection of C on AB
  (C2X, C2Y) = line_point_projection(ai_AB, ai_C, ai_error_msg_id)
  # calculation of the length IP
  #IP = math.sqrt((PX-IX)**2+(PY-IY)**2)
  IP2 = (PX-IX)**2+(PY-IY)**2
  IP = math.sqrt(IP2)
  if(IP>ai_R):
    # This error might occur when the sign of the tangent is wrong because of calculation impression.
    # That's why, we need to report the error instead of stopping on this error
    print("ERR672: Error in {:s}, the line and the circle have no intersection! IP={:0.2f}  ai_R={:0.2f}".format(ai_error_msg_id, IP, ai_R))
    print("dbg611: ai_AB:", ai_AB)
    print("dbg612: ai_I:", ai_I)
    print("dbg613: ai_R:", ai_R)
    print("dbg614: ai_C:", ai_C)
    #sys.exit(2)
    line_circle_intersection_status=2
    r_line_circle_intersection = (0, 0, line_circle_intersection_status)
  else:
    # calculation of the length PM
    PM = math.sqrt(ai_R**2-IP2)
    # calculation of the length C2P
    C2P = math.sqrt((PX-C2X)**2+(PY-C2Y)**2)
    cos_i = (C2X-PX)/C2P
    sin_i = (C2Y-PY)/C2P
    if(C2P<radian_epsilon):
      print("WARN348: Warning in {:s}, C is too closed from the board to find the line_circle_intersection!".format(ai_error_msg_id))
      xAB = math.atan2(a, -b)
      direction_correlation = math.fmod(ai_D_direction-xAB+5*math.pi, 2*math.pi)-math.pi
      direction_AB = math.copysign(1, direction_correlation)
      norm_ab = math.sqrt(a**2+b**2)
      cos_i = direction_AB * -b / norm_ab
      sin_i = direction_AB * a / norm_ab
    # calculation of the coordinates of M
    MX = PX+cos_i*PM
    MY = PY+sin_i*PM
    r_line_circle_intersection = (MX, MY, line_circle_intersection_status)
  # return
  return(r_line_circle_intersection)

def line_line_intersection(ai_AB, ai_CD, ai_error_msg_id):
  """ Given the line equations (a*x+b*y+c=0) of the two lines (AB) and (CD), returns the intersection M
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # status for error forward
  line_line_intersection_status = 0
  # interpretation of the input points
  a1 = ai_AB[0] # ABlx
  b1 = ai_AB[1] # ABly
  c1 = ai_AB[2] # ABk
  a2 = ai_CD[0] # CDlx
  b2 = ai_CD[1] # CDly
  c2 = ai_CD[2] # CDk
  # we have
  # a1*MX+b1*MY+c1=0
  # a2*MX+b2*MY+c2=0
  MX = 0
  MY = 0
  determinant = a1*b2-a2*b1
  if(abs(determinant)<radian_epsilon):
    print("WARN656: Warning in {:s}, the two lines are parallel!".format(ai_error_msg_id))
    line_line_intersection_status=2
  else:
    MX = (c2*b1-c1*b2)/determinant
    MY = (c1*a2-c2*a1)/determinant
  r_line_line_intersection = (MX, MY, line_line_intersection_status)
  # return
  #print("dbg947: r_line_line_intersection:", r_line_line_intersection)
  return(r_line_line_intersection)

def sub_smooth_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ compute the corner center of a smoothed line-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  # calculation of the AC line equation and J
  (AClx, ACly, ACkA, lAC, xAC) = line_equation(ai_pre_point, ai_current_point, ai_error_msg_id)
  (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
  # arc orientation
  #o1 = math.copysign(1, uw1)
  o2 = math.copysign(1, uw2)
  # sign of the tangent angle
  tangent_angle = math.fmod( u2+o2*math.pi/2-xAC+7*math.pi, 2*math.pi) - math.pi
  #r_outline = []
  smooth_status = 0
  if(abs(tangent_angle)<radian_epsilon):
    print("WARN942: Warning in {:s}, the tangent_angle is too flat! the corner doesn't need to be smoothed.".format(ai_error_msg_id))
    #r_outline = [(ai_current_point[0], ai_current_point[1])]
    smooth_status = 2
  #elif(abs(tangent_angle)>math.pi-radian_epsilon):
  #  print("WARN943: Warning in {:s}, the tangent_angle is too sharp! the corner cannot be smoothed.".format(ai_error_msg_id))
  #  r_outline = [(ai_current_point[0], ai_current_point[1])]
  else:
    o3 = math.copysign(1, tangent_angle)
    # calculation of IS and JS
    Q1_plus = o3 # = -1 if the router below the line, else 1
    R2_plus = o2*o3 # = -1 if the router is outer the arc, else 1
    (QX,QY, ACkQ) = line_distance_point(ai_pre_point, ai_current_point, Q1_plus*ai_router_bit_request, ai_error_msg_id)
    JS = R2-R2_plus*ai_router_bit_request
    #print("dbg147: ai_pre_point", ai_pre_point)
    #print("dbg347: ai_current_point", ai_current_point)
    #print("dbg447: ai_post_middle", ai_post_middle)
    #print("dbg547: ai_post_point", ai_post_point)
    #print("dbg647: ai_router_bit_request", ai_router_bit_request)
    #print("dbg123: AClx={:0.2f} ACly={:0.2f} ACkA={:0.2f} lAC={:0.2f} xAC={:0.2f}".format(AClx, ACly, ACkA, lAC, xAC))
    #print("dbg124: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
    #print("dbg125: o2={:0.2f} o3={:0.2f}".format(o2,o3))
    #print("dbg127: tangent_angle", tangent_angle)
    #print("dbg126: QS={:0.2f} JS={:0.2f}".format(QS,JS))
    #print("dbg532: in {:s}, xAC={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, xAC, R2, ai_router_bit_request))
    # calculation of the coordiantes of S, the center of the router_bit in the smooth corner
    bisector_angle = math.fmod(u2+o2*math.pi/2-(xAC+math.pi) + 7*math.pi, 2*math.pi) - math.pi
    D_direction = xAC + bisector_angle/2
    #print("dbg693: bisector_angle {:0.2f}  D_direction {:0.2f}".format(bisector_angle, D_direction))
    (SX,SY, line_circle_intersection_status) = line_circle_intersection((AClx, ACly, ACkQ), (JX,JY),JS, (CX,CY), D_direction, ai_error_msg_id)
    # when the angle is too sharp, the sign of the tangeant angle might be wrong because of calculation imprecition.
    # in this case, we use the method of try and retry
    if((line_circle_intersection_status==2)and(abs(tangent_angle)>math.pi-10*radian_epsilon)): # error then retry with -Q1_plus instead of Q1_plus
      print("WARN682: Warning in {:s}, line_arc corner is smoothed with the other side because of a line_circle_intersection error!".format(ai_error_msg_id))
      (QX,QY, ACkQ) = line_distance_point(ai_pre_point, ai_current_point, -Q1_plus*ai_router_bit_request, ai_error_msg_id)
      tmpCX = CX + JS*math.cos(xAC+math.pi)
      tmpCY = CY + JS*math.sin(xAC+math.pi)
      (SX,SY, line_circle_intersection_status) = line_circle_intersection((AClx, ACly, ACkQ), (JX,JY),JS, (tmpCX,tmpCY), D_direction, ai_error_msg_id)
    # end of the retry. Continue the normal calculation recipe
    if(line_circle_intersection_status==2):
      print("WARN684: Warning in {:s}, corner is not smoothed because of a line_circle_intersection error!".format(ai_error_msg_id))
      print("dbg681: ai_pre_point", ai_pre_point)
      print("dbg683: ai_current_point", ai_current_point)
      print("dbg684: ai_post_middle", ai_post_middle)
      print("dbg685: ai_post_point", ai_post_point)
      print("dbg686: ai_router_bit_request", ai_router_bit_request)
      print("dbg623: AClx={:0.2f} ACly={:0.2f} ACkA={:0.2f} lAC={:0.2f} xAC={:0.2f}".format(AClx, ACly, ACkA, lAC, xAC))
      print("dbg688: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
      print("dbg689: o2={:0.2f} o3={:0.2f}".format(o2,o3))
      print("dbg691: tangent_angle", tangent_angle)
      print("dbg692: JS={:0.2f}".format(JS))
      print("dbg711: QX={:0.2f} QY={:0.2f} ACkQ={:0.2f}".format(QX,QY,ACkQ))
      print("dbg693: in {:s}, xAC={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, xAC, R2, ai_router_bit_request))
      #r_outline = [(ai_current_point[0], ai_current_point[1])]
      smooth_status = 2
      sys.exit(2)
    else:
      # calculation of U, the projection of S on AC
      (UX, UY) = line_point_projection((AClx, ACly, ACkA), (SX,SY), ai_error_msg_id)
      # calculation of the angles xSU and xSJ
      #xSU = math.atan2(UY-SY, UX-SX)+(1+Q1_plus)/2*math.pi
      xSU = math.atan2(UY-SY, UX-SX)
      xSJ = math.atan2(JY-SY, JX-SX)+(1+R2_plus)/2*math.pi
      router_bit_arc_uw = math.fmod(xSJ-xSU+4*math.pi, 2*math.pi)
      if(o3<0):
        router_bit_arc_uw = router_bit_arc_uw - 2*math.pi
      #print("dbg337: SX {:0.2f}  SY {:0.2f}".format(SX,SY))
      #print("dbg994: xSI {:0.2f}  xSJ {:0.2f}".format(xSI, xSJ))
      #print("dbg773: router_bit_arc_uw", router_bit_arc_uw)
      smooth_status = 1
  # return
  r_sub_smooth_corner_line_arc = (SX, SY, UX, UY, xSU, xSJ, router_bit_arc_uw, smooth_status)
  return(r_sub_smooth_corner_line_arc)

def sub_smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Compute the smooth corner center for a arc-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  #BX = ai_pre_middle[0]
  #BY = ai_pre_middle[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  # calculation of I and J
  (IX,IY, R1, uw1, u1, w1) = arc_center_radius_angles(ai_pre_point, ai_pre_middle, ai_current_point, ai_error_msg_id)
  (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
  # arc orientation
  o1 = math.copysign(1, uw1)
  o2 = math.copysign(1, uw2)
  # sign of the tangent angle
  #tangent_angle = math.fmod( (u2+o2*path.pi/2)-(w1+o1*path.pi/2)+8*math.pi, 2*math.pi) - math.pi
  tangent_angle = math.fmod( u2-w1+(o2-o1)*math.pi/2+9*math.pi, 2*math.pi) - math.pi
  #r_outline = []
  smooth_status = 0
  if(abs(tangent_angle)<radian_epsilon):
    print("WARN932: Warning in {:s}, the tangent_angle is too flat! the corner doesn't need to be smoothed.".format(ai_error_msg_id))
    #r_outline = [(ai_current_point[0], ai_current_point[1])]
    smooth_status = 2
  elif(abs(tangent_angle)>math.pi-radian_epsilon):
    print("WARN933: Warning in {:s}, the tangent_angle is too sharp! the corner cannot be smoothed.".format(ai_error_msg_id))
    #r_outline = [(ai_current_point[0], ai_current_point[1])]
    smooth_status = 2
  else:
    o3 = math.copysign(1, tangent_angle)
    # calculation of IS and JS
    R1_plus = o1*o3 # = -1 if the router is outer the arc, else 1
    R2_plus = o2*o3 # = -1 if the router is outer the arc, else 1
    IS = R1-R1_plus*ai_router_bit_request
    JS = R2-R2_plus*ai_router_bit_request
    #print("dbg147: ai_pre_point", ai_pre_point)
    #print("dbg247: ai_pre_middle", ai_pre_middle)
    #print("dbg347: ai_current_point", ai_current_point)
    #print("dbg447: ai_post_middle", ai_post_middle)
    #print("dbg547: ai_post_point", ai_post_point)
    #print("dbg647: ai_router_bit_request", ai_router_bit_request)
    #print("dbg123: IX={:0.2f} IY={:0.2f} R1={:0.2f} uw1={:0.2f} u1={:0.2f}  w1={:0.2f}".format(IX, IY, R1, uw1, u1, w1))
    #print("dbg124: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
    #print("dbg125: o1={:0.2f} o2={:0.2f} o3={:0.2f}".format(o1,o2,o3))
    #print("dbg127: tangent_angle", tangent_angle)
    #print("dbg126: IS={:0.2f} JS={:0.2f}".format(IS,JS))
    #print("dbg532: in {:s}, R1={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, R1, R2, ai_router_bit_request))
    # calculation of the coordiantes of S, the center of the router_bit in the smooth corner
    bisector_angle = math.fmod(u2-w1+(o2+o1)*math.pi/2 + 9*math.pi, 2*math.pi) - math.pi #(u2+o2*math.pi/2)-(w1-o1*math.pi/2)
    D_direction = w1 + bisector_angle/2
    #print("dbg693: bisector_angle {:0.2f}  D_direction {:0.2f}".format(bisector_angle, D_direction))
    (SX,SY, triangulation_status) = triangulation((IX,IY),IS,(JX,JY),JS,(CX,CY), D_direction, ai_error_msg_id)
    if(triangulation_status==2):
      print("WARN693: Warning in {:s}, corner is not smoothed because of a triangulation error!".format(ai_error_msg_id))
      #print("dbg681: ai_pre_point", ai_pre_point)
      #print("dbg682: ai_pre_middle", ai_pre_middle)
      #print("dbg683: ai_current_point", ai_current_point)
      #print("dbg684: ai_post_middle", ai_post_middle)
      #print("dbg685: ai_post_point", ai_post_point)
      #print("dbg686: ai_router_bit_request", ai_router_bit_request)
      #print("dbg687: IX={:0.2f} IY={:0.2f} R1={:0.2f} uw1={:0.2f} u1={:0.2f}  w1={:0.2f}".format(IX, IY, R1, uw1, u1, w1))
      #print("dbg688: JX={:0.2f} JY={:0.2f} R2={:0.2f} uw2={:0.2f} u2={:0.2f}  w2={:0.2f}".format(JX, JY, R2, uw2, u2, w2))
      #print("dbg689: o1={:0.2f} o2={:0.2f} o3={:0.2f}".format(o1,o2,o3))
      #print("dbg691: tangent_angle", tangent_angle)
      #print("dbg692: IS={:0.2f} JS={:0.2f}".format(IS,JS))
      #print("dbg693: in {:s}, R1={:0.2f} R2={:0.2f} ai_router_bit_request={:0.2f}".format(ai_error_msg_id, R1, R2, ai_router_bit_request))
      #r_outline = [(ai_current_point[0], ai_current_point[1])]
      smooth_status = 2
    else:
      # calculation of the angles xSI and xSJ
      xSI = math.atan2(IY-SY, IX-SX)+(1+R1_plus)/2*math.pi
      xSJ = math.atan2(JY-SY, JX-SX)+(1+R2_plus)/2*math.pi
      router_bit_arc_uw = math.fmod(xSJ-xSI+4*math.pi, 2*math.pi)
      if(o3<0):
        router_bit_arc_uw = router_bit_arc_uw - 2*math.pi
      #print("dbg337: SX {:0.2f}  SY {:0.2f}".format(SX,SY))
      #print("dbg994: xSI {:0.2f}  xSJ {:0.2f}".format(xSI, xSJ))
      #print("dbg773: router_bit_arc_uw", router_bit_arc_uw)
      smooth_status = 1
  #return
  r_sub_smooth_corner_arc_arc = (SX, SY, xSI, xSJ, router_bit_arc_uw, smooth_status)
  return(r_sub_smooth_corner_arc_arc)

def sub_enlarge_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Compute the points related to an enlarged line-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  enlarge_status = 0
  #r_sub_enlarge_corner_line_arc = ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status)
  MKX=0; MKY=0; GX=0; GY=0; HX=0; HY=0; NLX=0; NLY=0; enlarge_type_request_1=0; enlarge_type_request_2=0
  (SX, SY, UX, UY, xSU, xSJ, router_bit_arc_uw, smooth_status) = sub_smooth_corner_line_arc(ai_pre_point, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  if(smooth_status!=1):
    print("ERR977: Error in {:s}, the sub smooth corner get an error!".format(ai_error_msg_id))
    sys.exit(2)
    enlarge_status = 2
  else:
    #print("dbg553: router_bit_arc_uw:", router_bit_arc_uw)
    if(abs(router_bit_arc_uw)>math.pi):
      print("ERR877: Error in {:s}, the sub smooth corner is englobed!".format(ai_error_msg_id))
      sys.exit(2)
      enlarge_status = 2
    elif(abs(router_bit_arc_uw)<radian_epsilon):
      print("WARN878: Warning in {:s}, the corner is too flat to be enlarged with this router_bit radius!")
      enlarge_status = 2
      enlarge_type_request_1=1
      enlarge_type_request_2=1
    else:
      corner_orientation = math.copysign(1, router_bit_arc_uw)
      enlarge_status = 1
      (SClx, SCly, SCkS, lSC, xSC) = line_equation((SX,SY), (CX,CY), ai_error_msg_id)
      (FX,FY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkS), (CX,CY),ai_router_bit_request, (SX,SY), xSC+math.pi, ai_error_msg_id)
      if(line_circle_intersection_status==2):
        print("ERR739: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
        sys.exit(2)
      (GX,GY, SCkG) = line_distance_point((FX,FY), (CX,CY), -1*corner_orientation*ai_router_bit_request, ai_error_msg_id)
      (HX,HY, SCkH) = line_distance_point((FX,FY), (CX,CY),  1*corner_orientation*ai_router_bit_request, ai_error_msg_id)
      #(IX,IY, R1, uw1, u1, w1) = arc_center_radius_angles(ai_pre_point, ai_pre_middle, ai_current_point, ai_error_msg_id)
      (AClx, ACly, ACkC, lAC, xAC) = line_equation(ai_pre_point, ai_current_point, ai_error_msg_id)

      (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
      #(MX,MY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkG), (IX,IY),R1, ((GX+SX)/2,(GY+SY)/2), xSC+math.pi, ai_error_msg_id)
      (MX,MY, line_line_intersection_status) = line_line_intersection((SClx, SCly, SCkG), (AClx, ACly, ACkC), ai_error_msg_id)

      #print("dbg321: MX={:0.2f}  MY={:0.2f}  line_circle_intersection={:0.2f}".format(MX, MY, line_circle_intersection_status))
      if(line_line_intersection_status==2):
        print("ERR736: Error in {:s} with the line_line_intersection_status!".format(ai_error_msg_id))
        sys.exit(2)
        enlarge_status = 2
      (NX,NY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkH), (JX,JY),R2, ((HX+SX)/2,(HY+SY)/2), xSC+math.pi, ai_error_msg_id)
      #print("dbg322: NX={:0.2f}  NY={:0.2f}  line_circle_intersection={:0.2f}".format(NX, NY, line_circle_intersection_status))
      if(line_circle_intersection_status==2):
        print("ERR733: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
        #print("dbg513: G={:0.2f} {:0.2f}  H={:0.2f} {:0.2f}".format(GX, GY, HX, HY))
        sys.exit(2)
        enlarge_status = 2
      # check if arc-arc intersection must be calculated
      tmp_MG_deep_x = (MX-GX)*(CX-FX)
      tmp_MG_deep_y = (MY-GY)*(CY-FY)
      #print("dbg301: tmp_MG_deep_x:", tmp_MG_deep_x)
      #print("dbg302: tmp_MG_deep_y:", tmp_MG_deep_y)
      MG_deep = math.copysign(1, tmp_MG_deep_x)
      if(abs(tmp_MG_deep_x)<abs(tmp_MG_deep_y)):
        MG_deep = math.copysign(1, tmp_MG_deep_y)
        #print("dbg303: use Y to get MG_deep")
      tmp_NH_deep_x = (NX-HX)*(CX-FX)
      tmp_NH_deep_y = (NY-HY)*(CY-FY)
      #print("dbg311: tmp_NH_deep_x:", tmp_NH_deep_x)
      #print("dbg312: tmp_NH_deep_y:", tmp_NH_deep_y)
      NH_deep = math.copysign(1, tmp_NH_deep_x)
      if(abs(tmp_NH_deep_x)<abs(tmp_NH_deep_y)):
        NH_deep = math.copysign(1, tmp_NH_deep_y)
        #print("dbg313: use Y to get NH_deep")
      MKX = MX
      MKY = MY
      NLX = NX
      NLY = NY
      enlarge_type_request_1 = 3
      enlarge_type_request_2 = 3
      # compute the arc-arc intersection
      if(MG_deep>0):
        #(KX,KY, triangulation_status) = triangulation((IX,IY),R1,(FX,FY),ai_router_bit_request,(GX,GY), xSC+math.pi, ai_error_msg_id)
        (KX,KY, line_circle_intersection_status) = line_circle_intersection((AClx, ACly, ACkC), (FX,FY),ai_router_bit_request, (GX, GY), xSC+math.pi, ai_error_msg_id)

        if(line_circle_intersection==2):
          print("ERR536: Error in {:s} with the triangulation_status!".format(ai_error_msg_id))
          sys.exit(2)
        MKX = KX
        MKY = KY
        enlarge_type_request_1 = 2
      if(NH_deep>0):
        (LX,LY, triangulation_status) = triangulation((JX,JY),R2, (FX,FY),ai_router_bit_request, (HX,HY), xSC+math.pi, ai_error_msg_id)
        if(triangulation_status==2):
          print("ERR533: Error in {:s} with the triangulation_status!".format(ai_error_msg_id))
          sys.exit(2)
        NLX = LX
        NLY = LY
        enlarge_type_request_2 = 2
      lMN=math.sqrt((NLX-MKX)**2+(NLY-MKY)**2)
      if(lMN<radian_epsilon):
        print("WARN667: Warning in {:s}, the angle is too flat to be enlarged!".format(ai_error_msg_id))
        enlarge_type_request_1 = 1
        enlarge_type_request_2 = 1
  # return
  r_sub_enlarge_corner_line_arc = ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status)
  #print("dbg668: r_sub_enlarge_corner_line_arc:", r_sub_enlarge_corner_line_arc)
  return(r_sub_enlarge_corner_line_arc)

def sub_enlarge_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id):
  """ Compute the points related to an enlarged arc-arc corner
  """
  # use to check is angle is smaller than pi/2
  radian_epsilon = math.pi/1000
  # interpretation of the input points
  #AX = ai_pre_point[0]
  #AY = ai_pre_point[1]
  #BX = ai_pre_middle[0]
  #BY = ai_pre_middle[1]
  CX = ai_current_point[0]
  CY = ai_current_point[1]
  #DX = ai_post_middle[0]
  #DY = ai_post_middle[1]
  #EX = ai_post_point[0]
  #EY = ai_post_point[1]
  #r_sub_enlarge_corner_arc_arc = ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status)
  MKX=0; MKY=0; GX=0; GY=0; HX=0; HY=0; NLX=0; NLY=0; enlarge_type_request_1=0; enlarge_type_request_2=0
  (SX, SY, xSI, xSJ, router_bit_arc_uw, smooth_status) = sub_smooth_corner_arc_arc(ai_pre_point, ai_pre_middle, ai_current_point, ai_post_middle, ai_post_point, ai_router_bit_request, ai_error_msg_id)
  enlarge_status = 0
  if(smooth_status==2):
    print("ERR927: Error in {:s}, the sub smooth corner gets an error!".format(ai_error_msg_id))
    sys.exit(2)
  else:
    #print("dbg553: router_bit_arc_uw:", router_bit_arc_uw)
    if(abs(router_bit_arc_uw)>math.pi):
      print("ERR887: Error in {:s}, the sub smooth corner is englobed!".format(ai_error_msg_id))
      sys.exit(2)
      enlarge_status = 2
    elif(abs(router_bit_arc_uw)<radian_epsilon):
      print("WARN877: Error in {:s}, the corner is too flat to be enlarged with this router_bit radius!".format(ai_error_msg_id))
      enlarge_status = 2
      enlarge_type_request_1 = 1
      enlarge_type_request_2 = 1
    else:
      corner_orientation = math.copysign(1, router_bit_arc_uw)
      enlarge_status = 1
      (SClx, SCly, SCkS, lSC, xSC) = line_equation((SX,SY), (CX,CY), ai_error_msg_id)
      (FX,FY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkS), (CX,CY),ai_router_bit_request, (SX,SY), xSC+math.pi, ai_error_msg_id)
      if(line_circle_intersection_status==2):
        print("ERR639: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
        sys.exit(2)
      (GX,GY, SCkG) = line_distance_point((FX,FY), (CX,CY), -1*corner_orientation*ai_router_bit_request, ai_error_msg_id)
      (HX,HY, SCkH) = line_distance_point((FX,FY), (CX,CY),  1*corner_orientation*ai_router_bit_request, ai_error_msg_id)
      (IX,IY, R1, uw1, u1, w1) = arc_center_radius_angles(ai_pre_point, ai_pre_middle, ai_current_point, ai_error_msg_id)
      (JX,JY, R2, uw2, u2, w2) = arc_center_radius_angles(ai_current_point, ai_post_middle, ai_post_point, ai_error_msg_id)
      (MX,MY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkG), (IX,IY),R1, ((GX+SX)/2,(GY+SY)/2), xSC+math.pi, ai_error_msg_id)
      #print("dbg321: MX={:0.2f}  MY={:0.2f}  line_circle_intersection={:0.2f}".format(MX, MY, line_circle_intersection_status))
      if(line_circle_intersection_status==2):
        print("ERR636: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
        sys.exit(2)
      (NX,NY, line_circle_intersection_status) = line_circle_intersection((SClx, SCly, SCkH), (JX,JY),R2, ((HX+SX)/2,(HY+SY)/2), xSC+math.pi, ai_error_msg_id)
      #print("dbg322: NX={:0.2f}  NY={:0.2f}  line_circle_intersection={:0.2f}".format(NX, NY, line_circle_intersection_status))
      if(line_circle_intersection_status==2):
        print("ERR633: Error in {:s} with the line_circle_intersection_status!".format(ai_error_msg_id))
        #print("dbg513: G={:0.2f} {:0.2f}  H={:0.2f} {:0.2f}".format(GX, GY, HX, HY))
        #sys.exit(2)
        enlarge_status = 2
      # check if arc-arc intersection must be calculated
      tmp_MG_deep_x = (MX-GX)*(CX-FX)
      tmp_MG_deep_y = (MY-GY)*(CY-FY)
      #print("dbg301: tmp_MG_deep_x:", tmp_MG_deep_x)
      #print("dbg302: tmp_MG_deep_y:", tmp_MG_deep_y)
      MG_deep = math.copysign(1, tmp_MG_deep_x)
      if(abs(tmp_MG_deep_x)<abs(tmp_MG_deep_y)):
        MG_deep = math.copysign(1, tmp_MG_deep_y)
        #print("dbg303: use Y to get MG_deep")
      tmp_NH_deep_x = (NX-HX)*(CX-FX)
      tmp_NH_deep_y = (NY-HY)*(CY-FY)
      #print("dbg311: tmp_NH_deep_x:", tmp_NH_deep_x)
      #print("dbg312: tmp_NH_deep_y:", tmp_NH_deep_y)
      NH_deep = math.copysign(1, tmp_NH_deep_x)
      if(abs(tmp_NH_deep_x)<abs(tmp_NH_deep_y)):
        NH_deep = math.copysign(1, tmp_NH_deep_y)
        #print("dbg313: use Y to get NH_deep")
      MKX = MX
      MKY = MY
      NLX = NX
      NLY = NY
      enlarge_type_request_1 = 3
      enlarge_type_request_2 = 3
      # compute the arc-arc intersection
      if(MG_deep>0):
        (KX,KY, triangulation_status) = triangulation((IX,IY),R1,(FX,FY),ai_router_bit_request,(GX,GY), xSC+math.pi, ai_error_msg_id)
        if(triangulation_status==2):
          print("ERR536: Error in {:s} with the triangulation_status!".format(ai_error_msg_id))
          sys.exit(2)
        MKX = KX
        MKY = KY
        enlarge_type_request_1 = 2
      if(NH_deep>0):
        (LX,LY, triangulation_status) = triangulation((JX,JY),R2,(FX,FY),ai_router_bit_request,(HX,HY), xSC+math.pi, ai_error_msg_id)
        if(triangulation_status==2):
          print("ERR533: Error in {:s} with the triangulation_status!".format(ai_error_msg_id))
          sys.exit(2)
        NLX = LX
        NLY = LY
        enlarge_type_request_2 = 2
      lMN=math.sqrt((NLX-MKX)**2+(NLY-MKY)**2)
      if(lMN<radian_epsilon):
        print("WARN667: Warning in {:s}, the angle is too flat to be enlarged!".format(ai_error_msg_id))
        enlarge_type_request_1 = 1
        enlarge_type_request_2 = 1
  # return
  r_sub_enlarge_corner_arc_arc = ((MKX,MKY), (GX,GY), (CX,CY), (HX,HY), (NLX,NLY), enlarge_type_request_1, enlarge_type_request_2, enlarge_status)
  #print("dbg588: r_sub_enlarge_corner_arc_arc:", r_sub_enlarge_corner_arc_arc)
  return(r_sub_enlarge_corner_arc_arc)

def curve_arc(ai_AX, ai_AY, ai_CX, ai_CY, ai_At, ai_router_bit_request, ai_error_msg_id):
  """ Given the start-point (A), the end-point (C) and the arc tangent (At) at (A), return the middle-point (B) and the arc tangent (Ct) at (C)
  """
  # use to check if the calculation is possible
  radian_epsilon = math.pi/1000
  # line equation of (AC)
  (AClx, ACly, ACk, lAC, xAC) = line_equation((ai_AX, ai_AY), (ai_CX, ai_CY), ai_error_msg_id)
  # calcultion of I the middle of [AC]
  IX = (ai_AX+ai_CX)/2
  IY = (ai_AY+ai_CY)/2
  # line equation of the bisection (OI) of [AC]
  OIlx = ACly
  OIly = -1*AClx
  OIk = -1*(OIlx*IX+OIly*IY)
  # line equation of (OA)
  # Tangent(A) equation (sin(At), -cos(At), K)
  # OA is perpendicular to Tangent(A)
  OAlx = math.cos(ai_At)
  OAly = math.sin(ai_At)
  OAk = -1*(OAlx*ai_AX+OAly*ai_AY)
  # O intersection of (OI) and (OA). It's the center of the arc
  (OX, OY, line_line_intersection_status) = line_line_intersection((OIlx, OIly, OIk),(OAlx, OAly, OAk), ai_error_msg_id)
  if(line_line_intersection_status==2):
    print("ERR374: Error in {:s}, the tangent and AC are collinear!".format(ai_error_msg_id))
    sys.exit(2)
  # verification of the distance OA and OC
  lOA = math.sqrt((ai_AX-OX)**2+(ai_AY-OY)**2)
  lOC = math.sqrt((ai_CX-OX)**2+(ai_CY-OY)**2)
  #print("dbg354: ai_AX={:0.2f}  ai_AY={:0.2f}".format(ai_AX, ai_AY))
  #print("dbg355: ai_CX={:0.2f}  ai_CY={:0.2f}".format(ai_CX, ai_CY))
  #print("dbg356: IX={:0.2f}  IY={:0.2f}".format(IX, IY))
  #print("dbg357: OX={:0.2f}  OY={:0.2f}".format(OX, OY))
  if(abs(lOC-lOA)>radian_epsilon):
    print("ERR375: Error in {:s}, O is not equidistant from A and C! lOA={:0.2f} l_OC={:0.2f}".format(ai_error_msg_id, lOA, lOC))
    sys.exit(2)
  if(lOA<ai_router_bit_request):
    print("WARN446: Warning in {:s}, the radius_of_curvature is smaller than the router_bit_request! lOA={:0.2f} rbr={:0.2f}".format(ai_error_msg_id, lOA, ai_router_bit_request))
  # calculation of the angle (Ox, OA)
  xOA = math.atan2((ai_AY-OY)/lOA, (ai_AX-OX)/lOA)
  # calculation of the angle (Ox, OC)
  xOC = math.atan2((ai_CY-OY)/lOC, (ai_CX-OX)/lOC)
  # arc orientation = sign of the angle (At,AC)
  AtAC = math.fmod(xAC-ai_At+5*math.pi, 2*math.pi) - math.pi
  # calculation of the angle AOC
  AOC = 0
  if(AtAC>0):
    AOC = math.fmod(xOC-xOA+4*math.pi, 2*math.pi)
  else:
    AOC = -1*math.fmod(xOA-xOC+4*math.pi, 2*math.pi)
  if(abs(AOC)<radian_epsilon):
    print("WARN776: Warning in {:s}, the angle AOC is really small!".format(ai_error_msg_id))
  # calculation of B
  xOB = xOA + AOC/2
  BX = OX+lOA*math.cos(xOB)
  BY = OY+lOA*math.sin(xOB)
  # calculation of the tangent inclination Ct in C
  Ct = xOC + math.copysign(math.pi/2, AtAC)
  # return
  r_curve_arc = (BX, BY, Ct)
  return(r_curve_arc)

def unstable_smooth_outline_b_curve(ai_polyline, ai_initial_tangent, ai_precision, ai_router_bit_request, ai_error_msg_id):
  """
  This function computes a serie of N arcs that pass through the (N+1) points defined by the N line-segments of ai_polyline.
  ai_polyline is an outline of format B, that contains only lines (no arcs) (list of list of 2 floats).
  ai_initial_tangent is the tangent of the wished curve at the first-point of the outline ai_polyline.
  ai_precision defined when a line should be generated instead of an arc because the tangent and the new segment are almost collinear.
  ai_router_bit_request is just used to warn if the radius_of_curvature is smaller than the router_bit. Because this function can not know on which side of the outline is the material, those warnings might be irrelevant. If you don't want this feature, just set it to 0, this disables these warnings.
  ai_error_msg_id is a string, that can help you to track bugs and erros.
  The function returns an outline of format B containing only arcs
  """
  # define the angle precision to know when to use a line instead of an arc
  #radian_epsilon = 1/1000.0
  radian_epsilon = ai_precision
  # check if the input outline is closed
  outline_closed = False
  if((ai_polyline[0][0]==ai_polyline[-1][-2])and(ai_polyline[0][1]==ai_polyline[-1][-1])):
  #if((abs(ai_polyline[0][0]-ai_polyline[-1][-2])<radian_epsilon)and(abs(ai_polyline[0][1]==ai_polyline[-1][-1])<radian_epsilon)):
    outline_closed = True
    print("WARN994: Warning in {:s}, the curve to smooth is closed and this will be ignored by the unstable_smooth_curve() function".format(ai_error_msg_id))
  # number of corners and segments
  point_nb = len(ai_polyline)
  # check the outline point number
  if(point_nb<2):
    print("ERR209: Error in {:s}, the number of points must be bigger than 2. Currently: {:d}".format(ai_error_msg_id, point_nb))
    sys.exit(2)
  # check if the first point is valid
  first_point_len = len(ai_polyline[0])
  if(first_point_len!=2):
    print("ERR219: Error in {:s}, the first-point of ai_polyline must have exactly 2 elements. Currently: {:d}".format(ai_error_msg_id, first_point_len))
    sys.exit(2)
  # processing initialization
  ti = ai_initial_tangent
  r_outline = []
  r_outline.append(ai_polyline[0]) # first-point
  # processing incrementation
  for i in range(point_nb-1):
    # error message
    i_error_msg_id = "{:s}.{:d}".format(ai_error_msg_id, i)
    # check the validity of the new segment
    segment_len = len(ai_polyline[i+1])
    if(segment_len!=2):
      print("ERR229: Error in {:s}, the ai_polyline segment length must be exactly 2. Currently: {:d}".format(i_error_msg_id, segment_len))
      sys.exit(2)
    # geometrical data
    AX = ai_polyline[i][0]
    AY = ai_polyline[i][1]
    CX = ai_polyline[i+1][0]
    CY = ai_polyline[i+1][1]
    # calculation of the inclination of AC
    lAC = math.sqrt((CX-AX)**2+(CY-AY)**2)
    iAC = math.atan2((CY-AY)/lAC, (CX-AX)/lAC)
    rti = math.fmod(ti-iAC+5*math.pi, 2*math.pi)-math.pi # angle (AC, tangent) between [-pi,pi]
    if(abs(rti)>math.pi-radian_epsilon):
      print("ERR239: Error in {:s}, AC and the tangent Ti are collinear and in opposite direction. iAC={:0.2f}  ti={:0.2f}".format(i_error_msg_id, iAC, ti))
      sys.exit(2)
    if(abs(rti)>math.pi/3):
      print("WARN249: Warning in {:s}, AC and the tangent Ti are doing a large angle. Add itermediate points to remove this warning. iAC={:0.2f}  ti={:0.2f}".format(i_error_msg_id, iAC, ti))
    if(abs(rti)<radian_epsilon):
      print("WARN259: Warning in {:s}, AC and the tangent Ti are almost identical. A line is generated for this segment. iAC={:0.2f}  ti={:0.2f}".format(i_error_msg_id, iAC, ti))
      r_outline.append([CX, CY]) # create a line-segment
      ti = iAC
    else:
      (BX, BY, nti) = curve_arc(AX, AY, CX, CY, ti, ai_router_bit_request, i_error_msg_id)
      r_outline.append([BX, BY, CX, CY]) # create an arc-segment
      ti = nti
  print("dbg536: the last tangent inclination ti: {:0.2f}".format(ti))
  # return
  return(r_outline)

def sub_smooth_outline_c_curve(ai_polyline, ai_precision, ai_router_bit_request, ai_error_msg_id):
  """
  This function computes a serie of 2N arcs that pass through the (N+1) points defined by the N line-segments of ai_polyline.
  ai_polyline is an outline of format C, (list of list of 3 floats).
  ai_precision defined when a line should be generated instead of an arc because the tangent and the new segment are almost collinear.
  ai_router_bit_request is just used to warn if the radius_of_curvature is smaller than the router_bit. Because this function can not know on which side of the outline is the material, those warnings might be irrelevant. If you don't want this feature, just set it to 0, this disables these warnings.
  ai_error_msg_id is a string, that can help you to track bugs and erros.
  The function returns an outline of format B containing only arcs
  """
  # define the angle precision to know when to use a line instead of an arc
  #radian_epsilon = 1/1000.0
  radian_epsilon = ai_precision
  # check if the input outline is closed
  outline_closed = False
  if((ai_polyline[0][0]==ai_polyline[-1][0])and(ai_polyline[0][1]==ai_polyline[-1][1])):
  #if((abs(ai_polyline[0][0]-ai_polyline[-1][-2])<radian_epsilon)and(abs(ai_polyline[0][1]==ai_polyline[-1][-1])<radian_epsilon)):
    outline_closed = True
    #print("WARN694: Warning in {:s}, the curve to smooth is closed and this will be ignored by the unstable_smooth_curve() function".format(ai_error_msg_id))
  # number of corners and segments
  point_nb = len(ai_polyline)
  # check the outline point number
  if(point_nb<2):
    print("ERR609: Error in {:s}, the number of points must be bigger than 2. Currently: {:d}".format(ai_error_msg_id, point_nb))
    sys.exit(2)
  # check if the first point is valid
  first_point_len = len(ai_polyline[0])
  if(first_point_len!=3):
    print("ERR619: Error in {:s}, the first-point of ai_polyline must have exactly 3 elements. Currently: {:d}".format(ai_error_msg_id, first_point_len))
    sys.exit(2)
  # processing initialization
  r_outline = []
  r_outline.append((ai_polyline[0][0], ai_polyline[0][1])) # first-point
  # processing incrementation
  for i in range(point_nb-1):
    # error message
    i_error_msg_id = "{:s}.{:d}".format(ai_error_msg_id, i)
    # check the validity of the new segment
    segment_len = len(ai_polyline[i+1])
    if(segment_len!=3):
      print("ERR629: Error in {:s}, the ai_polyline segment length must be exactly 3. Currently: {:d}".format(i_error_msg_id, segment_len))
      sys.exit(2)
    # geometrical data
    AX = ai_polyline[i][0]
    AY = ai_polyline[i][1]
    xAt = ai_polyline[i][2]
    EX = ai_polyline[i+1][0]
    EY = ai_polyline[i+1][1]
    xEt = ai_polyline[i+1][2]
    # calculation of the inclination of AE
    lAE = math.sqrt((EX-AX)**2+(EY-AY)**2)
    xAE = math.atan2((EY-AY)/lAE, (EX-AX)/lAE)
    # calculation of the inclination of AC
    AtAE = math.fmod(xAt-xAE+5*math.pi, 2*math.pi)-math.pi # angle (AE, tangent) between [-pi,pi]
    xAC = math.fmod(xAE + AtAE/2 + 5*math.pi, 2*math.pi) - math.pi
    AClx = math.sin(xAC)
    ACly = -1*math.cos(xAC)
    ACk = -1*(AClx*AX+ACly*AY)
    # calculation of the inclination of EC
    EtEA = math.fmod(xEt-xAE+5*math.pi, 2*math.pi)-math.pi # angle (AE, tangent) between [-pi,pi]
    xEC = math.fmod(xAE+math.pi + EtEA/2 + 5*math.pi, 2*math.pi) - math.pi
    EClx = math.sin(xEC)
    ECly = -1*math.cos(xEC)
    ECk = -1*(EClx*EX+ECly*EY)
    # check if the segment must be an arc or a line
    if(abs(AtAE)>math.pi/2):
      print("ERR639: Error in {:s}, the angle between AC and the tangent xAt is larger than pi/2. It doesn't look like a feasible curbe. xAC={:0.2f}  xAt={:0.2f}".format(i_error_msg_id, xAC, xAt))
      sys.exit(2)
    if(abs(EtEA)>math.pi/2):
      print("ERR638: Error in {:s}, the angle between EC and the tangent et is larger than pi/2. It doesn't look like a feasible curbe. xEC={:0.2f}  xEt={:0.2f}".format(i_error_msg_id, xEC, xEt))
      sys.exit(2)
    if(abs(AtAE)>math.pi/3):
      print("WARN649: Warning in {:s}, AC and the tangent xAt are doing a large angle. Add itermediate points to remove this warning. xAC={:0.2f}  xAt={:0.2f}".format(i_error_msg_id, xAC, xAt))
    if(abs(EtEA)>math.pi/3):
      print("WARN648: Warning in {:s}, EC and the tangent xEt are doing a large angle. Add itermediate points to remove this warning. xEC={:0.2f}  xEt={:0.2f}".format(i_error_msg_id, xEC, xEt))
    if((abs(AtAE)<radian_epsilon)or(abs(EtEA)<radian_epsilon)):
      print("WARN659: Warning in {:s}, (xAC, xAt) or (xEC, xEt) are almost identical. A line is generated for this segment. xAC={:0.2f}  xAt={:0.2f} xEC={:0.2f}  xEt={:0.2f} ".format(i_error_msg_id, xAC, xAt, xEC, xEt))
      r_outline.append((EX, EY)) # create a line-segment
    elif((AtAE*EtEA)>0):
      print("WARN669: Warning in {:s}, xAt and xEt are not one the side of (AE). It look like an inflexion. A line is generated for this segment. xAC={:0.2f}  xAt={:0.2f} xEC={:0.2f} xEt={:0.2f} ".format(i_error_msg_id, xAC, xAt, xEC, xEt))
      r_outline.append((EX, EY)) # create a line-segment
    else:
      # C intersection of (AC) and (EC). it is the junction point between the two arcs
      (CX, CY, line_line_intersection_status) = line_line_intersection((AClx, ACly, ACk),(EClx, ECly, ECk), ai_error_msg_id)
      if(line_line_intersection_status==2):
        print("ERR324: Error in {:s}, AC and EC are collinear!".format(ai_error_msg_id))
        sys.exit(2)
      (BX, BY, xCt) = curve_arc(AX, AY, CX, CY, xAt, ai_router_bit_request, i_error_msg_id)
      if(abs(math.fmod(xCt-xAE+5*math.pi, 2*math.pi)-math.pi)>radian_epsilon):
        print("ERR325: Error in {:s}, the first arc tangent in C is not parallel to AE! xCt={:0.2f} xAE={:0.2f}".format(ai_error_msg_id, xCt, xAE))
        sys.exit(2)
      (DX, DY, xEt2) = curve_arc(CX, CY, EX, EY, xAE, ai_router_bit_request, i_error_msg_id)
      if(abs(math.fmod(xEt2-xEt+5*math.pi, 2*math.pi)-math.pi)>radian_epsilon):
        print("ERR326: Error in {:s}, the second arc tangent in E is different from xEt! xEt={:0.2f} xEt2={:0.2f}".format(ai_error_msg_id, xEt, xEt2))
        sys.exit(2)
      r_outline.append((BX, BY, CX, CY)) # create the first arc-segment
      r_outline.append((DX, DY, EX, EY)) # create the second arc-segment
      #print("dbg048: BX {:0.3f}  BY {:0.3f}  CX {:0.3f}  CY {:0.3f}  DX {:0.3f}  DY {:0.3f}  EX {:0.3f}  EY {:0.3f}".format(BX, BY, CX, CY, DX, DY, EX, EY))
      #print("fbg049: r_outline:", r_outline)
  # return
  return(r_outline)


