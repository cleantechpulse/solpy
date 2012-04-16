#!/usr/bin/python

#    Copyright 2012 Nathan Charles
#
#
#    This is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This software is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with Pysolar. If not, see <http://www.gnu.org/licenses/>.

"""Calculate different kinds of radiation components via default values

"""
from math import radians
from numpy import sin, cos
from solar import position

def tilt(latitude, longitude, d, radiation, tilt = 0, plane_azimuth = 180):
    S = radians(tilt) #
    theta, Z, zenith = position(latitude, longitude, d, S, radians(plane_azimuth))
    #Gth = Btd + Dth + Rth
    etr, ghi, dni, dhi = radiation

    Bh = dni #hourly direct solar radiation
    Dh = dhi
    Gh = ghi

    #NREL Manual
    Bth = max(0,Bh * cos(theta))

    #sky-diffuse
    #Badescu 2002
    #rd = 3+cos(2*S)/4
    #Tian et al. 2001
    #rd = 1 -S/(2 *pi)
    #Liu and Jordan
    #rd = (1+cos(S))/2
    #Dth = rd*Dh # ?

    # perez(diffuse,hdi,etr,S,theta,zenith):
    Dth = perez(Dh,dni,dhi,etr,S,theta,Z,zenith)

    #ground diffuse
    # p = ground reflectivity
    p = 0.2
    Rth = Gh*p*(1-cos(S))/2 #?

    Gth = Bth + Dth +Rth
    return Gth

def perez(Xh,dni,hdi,etr,S,theta,zenith,h):
    """Perez et al. 1990
    Diffuse irradiance and illuminance on tilted surfaces
    """
    #theta is incident angle of the sun
    #Xh = horizontal diffuse
    Z = zenith
    Dh = hdi

    #m = airmass
    #Pickering 2002 footnote 39
    m = 1/(sin(radians(h+244/(165+47*h**1.1))))

    I = etr
    k = 1.041  #for Z in radians

    #(1)
    e = 0
    if Dh > 0:
        #print I,Dh,Z
        #this factor is a mystery i don't currently understand what 
        #it should be set at
        factor = 5.0
        e = round(((((Dh+dni)/Dh+k*Z**3)/(1.0+k*Z**3)))/factor)
        e = int(e)

    #(2)
    delta = Dh*m/I

    #Table 6
    #Irradiance model
    IRR = [[-0.008, 0.588,-0.062,-0.060, 0.072,-0.022],
            [0.130, 0.683,-0.151,-0.019, 0.066,-0.029],
            [0.330, 0.487,-0.221, 0.055,-0.064,-0.026],
            [0.568, 0.187,-0.295, 0.109,-0.152,-0.014],
            [0.873,-0.392,-0.362, 0.226,-0.462, 0.001],
            [1.132,-1.237,-0.412, 0.288,-0.823, 0.056],
            [1.060,-1.600,-0.359, 0.264,-1.127, 0.131],
            [0.678,-0.327,-0.250, 0.156,-1.377, 0.251]]
    #Illumanince
    ILL = [ [0.011, 0.570,-0.081,-0.095, 0.158,-0.018],
            [0.429, 0.363,-0.307, 0.050, 0.008,-0.065],
            [0.809,-0.054,-0.442, 0.181,-0.169,-0.092],
            [1.014,-0.252,-0.531, 0.275,-0.350,-0.096],
            [1.282,-0.420,-0.689, 0.380,-0.559,-0.114],
            [1.426,-0.653,-0.779, 0.425,-0.785,-0.097],
            [1.485,-1.214,-0.784, 0.411,-0.629,-0.082],
            [1.170,-0.300,-0.615, 0.518,-1.892,-0.055]]


    #3.2
    a = max(0,cos(theta))
    b = max(0.087,cos(Z))

    F1= IRR[e][0] * IRR[e][1]*delta + IRR[e][2]*Z
    F2= IRR[e][3] + IRR[e][4]*delta + IRR[e][5]*Z

    #3.2.2 Illumanince Model
    #(9)
    Xc = Xh*((1-F1)*(1+cos(S))/2 + F1*a/b+F2*sin(S))
    Xc = max(0,Xc)
    #Xc = Xh*(.5*(1-F1)*(1+cos(beta)) + F1*a/b+F2*sin(beta))
    return Xc