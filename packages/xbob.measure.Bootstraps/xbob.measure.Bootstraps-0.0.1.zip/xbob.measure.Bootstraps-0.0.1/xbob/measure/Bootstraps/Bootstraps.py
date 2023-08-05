#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Chi Ho CHAN <c.chan@surrey.ac.uk>
# @date: Mon July  8 11:33:00 CEST 2013
#
# Copyright (C) 2011-2013 CVSSP, University of Surrey, U.K.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bob
import os, sys
import numpy
import math
import scipy
from scipy.stats import norm
from random import randint


def ROC2DETPolar(FAR,FRR):

  min_res = [0.00001,0.00001]

  firsts=(FRR==0.0).nonzero()
  if len(firsts[0]) ==0 :
	firsts=(FAR==1.0).nonzero()
	FAR[firsts[0][-1]]= 1-min_res[1]
  else:
        FRR[firsts[0][-1]]= min_res[0]

  lasts=(FAR==0).nonzero()
  if len(lasts[0]) ==0 :
	lasts=(FRR==1.0).nonzero()
	FRR[lasts[0][0]]=1-min_res[0]
  else:
        FAR[lasts[0][0]]=min_res[1]


  if len(firsts[0])==0 :
    first=0;
  else:
    first=firsts[0][-1]

  if len(lasts[0])==0 :
    last=len(FAR)
  else:
    last=lasts[0][0]+1

  iFAR=FAR[first:last]
  iFRR=FRR[first:last]

  min_res=[norm.ppf(x) for x in min_res]
  nFAR=[norm.ppf(x)-min_res[0] for x in iFAR]
  nFRR=[norm.ppf(x)-min_res[1] for x in iFRR]


#interpolate the first and last two elements -- where data is scarce

  first_dumpFAR= numpy.linspace(nFAR[0],nFAR[1], num=20)
  first_dumpFRR=numpy.linspace(nFRR[0],nFRR[1], num=20)
  end_dumpFAR=numpy.linspace(nFAR[-2],nFAR[-1], num=20)
  end_dumpFRR=numpy.linspace(nFRR[-2],nFRR[-1], num=20)

  nnFAR=numpy.append(first_dumpFAR, nFAR[2:-2])
  nnFRR=numpy.append(first_dumpFRR, nFRR[2:-2])
  nnFAR=numpy.append(nnFAR, end_dumpFAR)
  nnFRR=numpy.append(nnFRR, end_dumpFRR)


  radius=[]
  degree=[]

  for idx in range(0, len(nnFAR)):
	radius=numpy.append(radius,math.sqrt(nnFAR[idx]**2+nnFRR[idx]**2))
        rad=float(math.atan2(nnFRR[idx],nnFAR[idx]))
        if rad >0 :
          deg=rad/float((math.pi))*180
        else:
          deg=rad/float((math.pi))*180+360
        if deg ==360 :
	  deg=0
        degree=numpy.append(degree,deg)

  chosen=[i for i, x in enumerate(degree) if (x>=0) and not(numpy.isnan(x)) and not(numpy.isinf(x))]
  ndegree=degree[chosen]
  nradius=radius[chosen]
#sort ndegree
  chosen=numpy.argsort(ndegree)
  ndegree=ndegree[chosen]
  nradius=nradius[chosen]

  chosen=[i for i, x in enumerate(nradius) if not(numpy.isinf(x))]
  ndegree=ndegree[chosen]
  nradius=nradius[chosen]
  dup=[i for i, x in enumerate(numpy.diff(ndegree)) if x==0]
  ndegree=numpy.delete(ndegree,dup)
  nradius=numpy.delete(nradius,dup)	


  deg_list=range(0,360)
  f=scipy.interpolate.interp1d(ndegree,nradius,kind='linear',bounds_error=False)
  r=f(deg_list)

  Polar=[deg_list, r]

  return Polar


def Polar2DET(Polar):

  deg_list=Polar[0]
  r=Polar[1]
  min_res = [0.00001, 0.00001];
  from scipy.stats import norm
  min_res=[norm.ppf(x) for x in min_res]

  DET=[[r[i]*math.cos(float(deg_list[i])/360*2*math.pi)+min_res[0] for i,x in enumerate(deg_list) ],[r[i]*math.sin(float(deg_list[i])/360*2*math.pi)+min_res[1] for i,x in enumerate(deg_list) ]]

  return DET


def quantile(a, prob):
#    """
#   Estimates the prob'th quantile of the values in a data array.

#    Uses the algorithm of matlab's quantile(), namely:
#        - Remove any nan values
#        - Take the sorted data as the (.5/n), (1.5/n), ..., (1-.5/n) quantiles.
#        - Use linear interpolation for values between (.5/n) and (1 - .5/n).
#        - Use the minimum or maximum for quantiles outside that range.

#    See also: scipy.stats.mstats.mquantiles
#    """

  if sum(numpy.isnan(a)) == a.size :
        return numpy.array([float('nan')])
  a = numpy.asanyarray(a)
  a = a[numpy.logical_not(numpy.isnan(a))].ravel()
  n = a.size
  if prob >= 1 - .5/n:
        return a.max()
  elif prob <= .5 / n:
        return a.min()

    # find the two bounds we're interpreting between:
    # that is, find i such that (i+.5) / n <= prob <= (i+1.5)/n
  t = n * prob - .5
  i = numpy.floor(t)

  a = numpy.sort(a)

  if i == t: # did we luck out and get an integer index?
        return a[i]
  else:
        # we'll linearly interpolate between this and the next index
        smaller = a[i]
        larger = a[i+1:].min()
        if numpy.isinf(smaller):
            return smaller # avoid inf - inf
        return smaller + (larger - smaller) * (t - i)


def JointBootstraps(cmc_scores, conf_interval, n_user_bstrp, n_bstrp):

  """ Calculates Confidence interval of the DET curve from the given input of cmc_scores. The input has a specific format, which is a list of two-element tuples. Each of the tuples contains the negative and the positive scores for one test item. To read the lists from score files in 4 or 5 column format, please use the bob.measure.load.cmc_four_column or bob.measure.load.cmc_five_column function.
  conf_interval is a list of confidence interval
  n_user_bstrp is the number of iteration of the user-specific bootstrap resampling
  n_bstrp is the number of iteration of the user-constrained sample bootstrap resampling.

  OUTPUT:
  X axis values in the normal deviate scale for the false-accepts
  Y axis values in the normal deviate scale for the false-rejections

  You can plot the results using your preferred tool to first create a plot using rows 0 and 1 from the returned value and then replace the X/Y axis annotation using a pre-determined set of tickmarks as recommended by NIST.

  The algorithm that calculates the deviate scale is based on function ppndf() from the NIST package DETware version 2.1, freely available on the internet. Please consult it for more details.

  By 20.04.2011, you could find such package here: http://www.itl.nist.gov/iad/mig/tools/

  Originally described in the paper:
  Poh, N.; Martin, A.; Bengio, S., "Performance Generalization in Biometric Authentication Using Joint User-Specific and Sample Bootstraps," Pattern Analysis and Machine Intelligence, IEEE Transactions on , vol.29, no.3, pp.492,498, March 2007
  """


#chosen_Id
  radius_list=[]
  deg_list=[]
  retval=[]
  for user_bstrp in range(0,n_user_bstrp):
    chosen_Id=[]
    if user_bstrp ==0 :
      chosen_Id=range(0,len( cmc_scores))
    else:
#      from random import randint
      chosen_Id=[randint(0,len( cmc_scores)-1) for p in range(0,len( cmc_scores))]

    pos_scores=[]
    neg_scores=[]
    for Id in sorted(chosen_Id):
      pos_scores=numpy.append(pos_scores, cmc_scores[Id][1])
      neg_scores=numpy.append(neg_scores, cmc_scores[Id][0])
    for bstrp in range(0, n_bstrp):
      chosen_pIdx=[]
      chosen_nIdx=[]
      if bstrp==0 :
#        from random import randint
	chosen_pIdx=range(0,len( pos_scores))
	chosen_nIdx=range(0,len( neg_scores))
      else:
        chosen_pIdx=[randint(0,len(pos_scores)-1) for p in range(0,len( pos_scores))]
        chosen_nIdx=[randint(0,len(neg_scores)-1) for p in range(0,len( neg_scores))]

      bootstrap_pos_scores=numpy.array([pos_scores[x] for x in chosen_pIdx])
      bootstrap_neg_scores=numpy.array([neg_scores[x] for x in chosen_nIdx])

      pts=1000
      ROC=bob.measure.roc(bootstrap_neg_scores, bootstrap_pos_scores,pts)

      Polar=ROC2DETPolar(ROC[0],ROC[1])

      if len(radius_list) == 0 :
        radius_list=Polar[1]
      else:
        radius_list=numpy.column_stack([radius_list,Polar[1]])
      if bstrp==0:
	deg_list=Polar[0]

    #quantile on radius_list
  conf_scores=[]
  for v in radius_list:
    conf_Tmpscores=[]
    for u in conf_interval:
	score=quantile(v, u)
	conf_Tmpscores=numpy.append(conf_Tmpscores, score)

    if len(conf_scores) == 0 :
      conf_scores=conf_Tmpscores
    else:    
      conf_scores=numpy.row_stack([conf_scores, conf_Tmpscores])
  for idx in range(0,conf_scores.shape[1]):
    nROC=Polar2DET([deg_list, conf_scores[:,idx]])  
    retval.append((numpy.array(nROC[0], numpy.float64),numpy.array(nROC[1], numpy.float64)))


  return retval
  


def JointBootstraps_plot(cmc_scores, conf_interval, n_user_bstrp, n_bstrp, axisfontsize='x-small', **kwargs):
  """ Plot Confidence interval of the DET curve from the given input of cmc_scores. The input has a specific format, which is a list of two-element tuples. Each of the tuples contains the negative and the positive scores for one test item. To read the lists from score files in 4 or 5 column format, please use the bob.measure.load.cmc_four_column or bob.measure.load.cmc_five_column function.
  conf_interval is a list of confidence interval
  n_user_bstrp is the number of iteration of the user-specific bootstrap resampling
  n_bstrp is the number of iteration of the user-constrained sample bootstrap resampling.

  OUTPUT:
  X axis values in the normal deviate scale for the false-accepts
  Y axis values in the normal deviate scale for the false-rejections

  You can plot the results using your preferred tool to first create a plot using rows 0 and 1 from the returned value and then replace the X/Y axis annotation using a pre-determined set of tickmarks as recommended by NIST.

  The algorithm that calculates the deviate scale is based on function ppndf() from the NIST package DETware version 2.1, freely available on the internet. Please consult it for more details.

  By 20.04.2011, you could find such package here: http://www.itl.nist.gov/iad/mig/tools/

  Originally described in the paper:
  Poh, N.; Martin, A.; Bengio, S., "Performance Generalization in Biometric Authentication Using Joint User-Specific and Sample Bootstraps," Pattern Analysis and Machine Intelligence, IEEE Transactions on , vol.29, no.3, pp.492,498, March 2007
  """

  try:
    import matplotlib.pyplot as mpl
  except ImportError:
    print("Cannot import matplotlib. This package is not essential, but required if you wish to use the plotting functionality.")
    raise

  # these are some constants required in this method
  desiredTicks = [
      "0.00001", "0.00002", "0.00005",
      "0.0001", "0.0002", "0.0005",
      "0.001", "0.002", "0.005",
      "0.01", "0.02", "0.05",
      "0.1", "0.2", "0.4", "0.6", "0.8", "0.9",
      "0.95", "0.98", "0.99",
      "0.995", "0.998", "0.999",
      "0.9995", "0.9998", "0.9999",
      "0.99995", "0.99998", "0.99999"
      ]

  desiredLabels = [
      "0.001", "0.002", "0.005",
      "0.01", "0.02", "0.05",
      "0.1", "0.2", "0.5",
      "1", "2", "5",
      "10", "20", "40", "60", "80", "90",
      "95", "98", "99",
      "99.5", "99.8", "99.9",
      "99.95", "99.98", "99.99",
      "99.995", "99.998", "99.999"
      ]

  # this will actually do the plotting

  out = JointBootstraps(cmc_scores, conf_interval, n_user_bstrp, n_bstrp)
  for idx in range(0,len(out)) :
    retval = mpl.plot(out[idx][0], out[idx][1], **kwargs)
    if idx == 0 :
  # now the trick: we must plot the tick marks by hand using the PPNDF method
     pticks = [bob.measure.ppndf(float(v)) for v in desiredTicks]
     ax = mpl.gca() #and finally we set our own tick marks
     ax.set_xticks(pticks)
     ax.set_xticklabels(desiredLabels, size=axisfontsize)
     ax.set_yticks(pticks)
     ax.set_yticklabels(desiredLabels, size=axisfontsize)

  return retval



