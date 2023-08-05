"""
python -m lifelines.tests.test_suit

"""
import unittest
import numpy as np
import numpy.testing as npt
from collections import Counter
import matplotlib.pyplot as plt
import pdb

import pandas as pd

from ..estimation import KaplanMeierFitter, NelsonAalenFitter, AalenAdditiveFitter
from ..statistics import logrank_test,multivariate_logrank_test, pairwise_logrank_test
from ..generate_datasets import *
from ..plotting import plot_lifetimes
from ..utils import datetimes_to_durations

class MiscTests(unittest.TestCase):

    def test_quadratic_integration_identity(self):
      #integrate x between 0 and 10:
      x = np.linspace(0,10,1000)[:,None]
      answer = 0.5*x**2
      approx_answer = cumulative_quadrature( x.T, x).T
      npt.assert_almost_equal(answer, approx_answer, decimal=5)

    def test_quadratic_integration_exp(self):
      #integrate exp(x) between 0 and 4:
      x = np.linspace(0,4,1000)[:,None]
      answer = np.exp(x) -1.
      approx_answer = cumulative_quadrature( np.exp(x).T, x).T
      #pdb.set_trace()
      npt.assert_almost_equal(answer, approx_answer, decimal=4)

    def test_aalen_additive_allows_numpy_or_df(self):
      t = np.random.random((10,1))
      dfX = pd.DataFrame(np.random.random((10,3)), columns = ["A", "B", "C"])
      c = dfX.columns
      npX = np.random.random((10,5))
      aaf = AalenAdditiveFitter()
      aaf.fit(t,npX)
      aaf.fit(t, dfX)
      npt.assert_array_equal( c, aaf.cumulative_hazards_.columns[:3] )

    def test_datetimes_to_durations_days(self):
        start_date = ['2013-10-10 0:00:00', '2013-10-09', '2012-10-10']
        end_date = ['2013-10-13', '2013-10-10 0:00:00', '2013-10-15']
        T,C = datetimes_to_durations(start_date, end_date)
        npt.assert_almost_equal(T, np.array([3,1,5+365]) )
        npt.assert_almost_equal(C, np.array([1,1,1], dtype=bool) )
        return    

    def test_datetimes_to_durations_years(self):
        start_date = ['2013-10-10', '2013-10-09', '2012-10-10']
        end_date = ['2013-10-13', '2013-10-10', '2013-10-15']
        T,C = datetimes_to_durations(start_date, end_date, freq='Y')
        npt.assert_almost_equal(T, np.array([0,0,1]) )
        npt.assert_almost_equal(C, np.array([1,1,1], dtype=bool) )
        return

    def test_datetimes_to_durations_censor(self):
        start_date = ['2013-10-10', '2013-10-09', '2012-10-10']
        end_date = ['2013-10-13', None, '']
        T,C = datetimes_to_durations(start_date, end_date, freq='Y')
        npt.assert_almost_equal(C, np.array([1,0,0], dtype=bool) )
        return


class StatisticalTests(unittest.TestCase):

  def setUp(self):
      self.lifetimes = Counter(LIFETIMES)
      self.km = self.kaplan_meier()
      self.kmc = self.kaplan_meier(censor=True)
      self.na = self.nelson_aalen()
      self.nac = self.nelson_aalen(censor=True)

  def test_kaplan_meier(self):
      kmf = KaplanMeierFitter()
      kmf.fit(LIFETIMES)
      npt.assert_almost_equal(kmf.survival_function_.values, self.km )
  
  def test_nelson_aalen(self):
      naf = NelsonAalenFitter(nelson_aalen_smoothing=False)
      naf.fit(LIFETIMES)
      npt.assert_almost_equal(naf.cumulative_hazard_.values, self.na )
  
  def test_censor_nelson_aalen(self):
      naf = NelsonAalenFitter(nelson_aalen_smoothing=False)
      naf.fit(LIFETIMES, censorship=CENSORSHIP)
      npt.assert_almost_equal(naf.cumulative_hazard_.values, self.nac )
  
  def test_censor_kaplan_meier(self):
      kmf = KaplanMeierFitter()
      kmf.fit(LIFETIMES, censorship = CENSORSHIP)
      npt.assert_almost_equal(kmf.survival_function_.values, self.kmc )

  def test_not_to_break(self):
      try:
        naf = NelsonAalenFitter(nelson_aalen_smoothing=False)
        naf.fit(LIFETIMES)
        naf = NelsonAalenFitter(nelson_aalen_smoothing=True)
        naf.fit(LIFETIMES)
        self.assertTrue(1==1)
      except Exception as e:
        print e
        self.assertTrue(0==1)

  def test_equal_intensity(self):
      data1 = np.random.exponential(5, size=(200,1))
      data2 = np.random.exponential(5, size=(200,1))
      summary, p_value, result = logrank_test(data1, data2)
      print summary
      self.assertTrue(result==None)

  def test_unequal_intensity(self):
      data1 = np.random.exponential(5, size=(200,1))
      data2 = np.random.exponential(1, size=(200,1))
      summary, p_value, result = logrank_test(data1, data2)
      print summary
      self.assertTrue(result)

  def test_unequal_intensity_censorship(self):
      data1 = np.random.exponential(5, size=(200,1))
      data2 = np.random.exponential(1, size=(200,1))
      censorA = np.random.binomial(1,0.5, size=(200,1))
      censorB = np.random.binomial(1,0.5, size=(200,1))
      summary, p_value, result = logrank_test(data1, data2, censorship_A = censorA, censorship_B = censorB)
      print summary
      self.assertTrue(result)

  def test_integer_times_logrank_test(self):
      data1 = np.random.exponential(5, size=(200,1)).astype(int)
      data2 = np.random.exponential(1, size=(200,1)).astype(int)
      summary, p_value, result = logrank_test(data1, data2)
      print summary
      self.assertTrue(result)

  def test_waltons_data(self):
      summary, p_value, result = logrank_test(waltonT1, waltonT2)
      print summary
      self.assertTrue(result)

  def test_multivariate_unequal_intensities(self):
     T = np.random.exponential(10, size=300)
     g = np.random.binomial(2, 0.5, size=300)
     T[g==1] = np.random.exponential(6, size=(g==1).sum())
     s, _, result = multivariate_logrank_test(T, g)
     print s
     self.assertTrue(result==True)

  def test_multivariate_equal_intensities(self):
     T = np.random.exponential(10, size=300)
     g = np.random.binomial(2, 0.5, size=300)
     s, _, result = multivariate_logrank_test(T, g)
     print s
     self.assertTrue(result==None)

  def test_pairwise_waltons_data(self):
      _,_,R = pairwise_logrank_test(waltonT, waltonG)
      print R
      self.assertTrue(R.values[0,1])

  def test_pairwise_logrank_test(self):
      T = np.random.exponential(10, size=300)
      g = np.random.binomial(2, 0.7, size=300)
      S, P, R = pairwise_logrank_test(T, g, alpha=0.95)
      V = np.array([[np.nan,None,None],[None,np.nan,None],[None,None,np.nan]])
      npt.assert_array_equal(R,V)


  def test_aalen_additive_median_predictions_split_data(self):
      #generate some hazard rates and a survival data set
      n = 2500
      d = 5
      timeline = np.linspace(0,70,5000)
      hz, coef, X = generate_hazard_rates(n,d, timeline )
      T = generate_random_lifetimes(hz, timeline)
      #fit it to Aalen's model
      aaf = AalenAdditiveFitter(penalizer=0., fit_intercept=False)
      aaf.fit(T,X, censorship=None)

      #predictions
      T_pred = aaf.predict_median(X)

      self.assertTrue( abs((T_pred.values > T).mean() - 0.5) < 0.1 )

  def test_lists_to_KaplanMeierFitter(self):
      T = [2,3,4.,1.,6,5.]
      C = [1,0,0,0,1,1]
      kmf = KaplanMeierFitter()
      with_list = kmf.fit(T,C).survival_function_.values
      with_array = kmf.fit(np.array(T),np.array(C)).survival_function_.values
      npt.assert_array_equal(with_list,with_array)

  def test_lists_to_NelsonAalenFitter(self):
      T = [2,3,4.,1.,6,5.]
      C = [1,0,0,0,1,1]
      naf = NelsonAalenFitter()
      with_list = naf.fit(T,C).cumulative_hazard_.values
      with_array = naf.fit(np.array(T),np.array(C)).cumulative_hazard_.values
      npt.assert_array_equal(with_list,with_array)

  def kaplan_meier(self, censor=False):
      km = np.zeros((len(self.lifetimes.keys()),1))
      ordered_lifetimes = np.sort( self.lifetimes.keys())
      v = 1.
      n = N*1.0
      for i,t in enumerate(ordered_lifetimes):
        if censor:
           ix = LIFETIMES == t
           c = sum(1-CENSORSHIP[ix])
           n -=  c
           if n!=0:
              v *= ( 1-(self.lifetimes.get(t)-c)/n )
           n -= self.lifetimes.get(t) - c
        else:
           v *= ( 1-self.lifetimes.get(t)/n )
           n -= self.lifetimes.get(t)
        km[i] = v
      if km[0] < 1.:
        km = np.insert(km,0,1.)
      return km.reshape(len(km),1)

  def nelson_aalen(self, censor = False):
      na = np.zeros((len(self.lifetimes.keys()),1))
      ordered_lifetimes = np.sort( self.lifetimes.keys())
      v = 0.
      n = N*1.0
      for i,t in enumerate(ordered_lifetimes):
        if censor:
           ix = LIFETIMES == t
           c = sum(1-CENSORSHIP[ix])
           n -=  c
           if n!=0:
              v += ( (self.lifetimes.get(t)-c)/n )
           n -= self.lifetimes.get(t) - c
        else:
           v += ( self.lifetimes.get(t)/n )
           n -= self.lifetimes.get(t)
        na[i] = v
      if na[0] > 0:
        na = np.insert(na,0,0.)
      return na.reshape(len(na),1)

class PlottingTests(unittest.TestCase):

  def test_kmf_plotting(self):
      data1 = np.random.exponential(10, size=(200,1))
      data2 = np.random.exponential(2, size=(200,1))
      kmf = KaplanMeierFitter()
      kmf.fit(data1, columns = ['test label 1'])
      ax = kmf.plot()
      kmf.fit(data2, columns = ['test labe 2'] )
      kmf.plot(ax=ax, c="#A60628")
      return 

  def test_naf_plotting(self):
      data1 = np.random.exponential(5, size=(200,1))
      data2 = np.random.exponential(1, size=(200,1))
      naf = NelsonAalenFitter()
      naf.fit(data1)
      ax = naf.plot()
      naf.fit(data2)
      naf.plot(ax=ax, c="#A60628", ci_force_lines=True)
      plt.title('testing naf')
      return 

  def test_naf_plotting_slice(self):
      data1 = np.random.exponential(5, size=(200,1))
      data2 = np.random.exponential(1, size=(200,1))
      naf = NelsonAalenFitter()
      naf.fit(data1)
      ax = naf.plot(ix=slice(0,None))
      naf.fit(data2)
      naf.plot(ax=ax, c="#A60628", ci_force_lines=True, ix=slice(50,150))
      plt.title('testing slicing')
      return 

  def test_plot_lifetimes_calendar(self):
      plt.figure()
      t = np.linspace(0, 20, 1000)
      hz, coef, covrt =generate_hazard_rates(1,5, t) 
      N = 20
      current = 10
      birthtimes = current*np.random.uniform(size=(N,))
      T, C = generate_random_lifetimes(hz, t, size=N, censor=current - birthtimes )
      plot_lifetimes(T, censorship=C, birthtimes=birthtimes)

  def test_plot_lifetimes_relative(self):
      plt.figure()
      t = np.linspace(0, 20, 1000)
      hz, coef, covrt =generate_hazard_rates(1,5, t) 
      N = 20
      T, C= generate_random_lifetimes(hz, t, size=N, censor=True )
      plot_lifetimes(T, censorship=C)

#some data

LIFETIMES = np.array([2,4,4,4,5,7,10,11,11,12])
CENSORSHIP = np.array([1,1,0,1,0,1,1,1,1,0])

waltonT2 = np.array([6., 13., 13., 13., 19., 19., 19., 26., 26., 26., 26., 26., 33., 33., 47., 62., 62., 9., 9., 9., 15., 15., 22., 22., 22., 22., 29., 29., 29., 29., 29., 36., 36., 43.])
waltonT1 = np.array([33., 54., 54., 61., 61., 61., 61., 61., 61., 61., 61., 61., 61., 61., 69., 69., 69., 69., 69., 69., 69., 69., 69., 69., 69., 32., 53., 53., 60., 60., 60., 60., 60., 68., 68., 68., 68., 68., 68., 68., 68., 68., 68., 75., 17., 51., 51., 51., 58., 58., 58., 58., 66., 66., 7., 7., 41., 41., 41., 41., 41., 41., 41., 48., 48., 48., 48., 48., 48., 48., 48., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 56., 63., 63., 63., 63., 63., 63., 63., 63., 63., 69., 69., 38., 38., 45., 45., 45., 45., 45., 45., 45., 45., 45., 45., 53., 53., 53., 53., 53., 60., 60., 60., 60., 60., 60., 60., 60., 60., 60., 60., 66.])

waltonG = np.array(['miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137',
       'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137',
       'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137',
       'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137',
       'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137', 'miR-137',
       'miR-137', 'miR-137', 'miR-137', 'miR-137', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control', 'control', 'control', 'control', 'control', 'control',
       'control'], dtype=object)

waltonT = np.array([  6.,  13.,  13.,  13.,  19.,  19.,  19.,  26.,  26.,  26.,  26.,
        26.,  33.,  33.,  47.,  62.,  62.,   9.,   9.,   9.,  15.,  15.,
        22.,  22.,  22.,  22.,  29.,  29.,  29.,  29.,  29.,  36.,  36.,
        43.,  33.,  54.,  54.,  61.,  61.,  61.,  61.,  61.,  61.,  61.,
        61.,  61.,  61.,  61.,  69.,  69.,  69.,  69.,  69.,  69.,  69.,
        69.,  69.,  69.,  69.,  32.,  53.,  53.,  60.,  60.,  60.,  60.,
        60.,  68.,  68.,  68.,  68.,  68.,  68.,  68.,  68.,  68.,  68.,
        75.,  17.,  51.,  51.,  51.,  58.,  58.,  58.,  58.,  66.,  66.,
         7.,   7.,  41.,  41.,  41.,  41.,  41.,  41.,  41.,  48.,  48.,
        48.,  48.,  48.,  48.,  48.,  48.,  56.,  56.,  56.,  56.,  56.,
        56.,  56.,  56.,  56.,  56.,  56.,  56.,  56.,  56.,  56.,  56.,
        56.,  56.,  63.,  63.,  63.,  63.,  63.,  63.,  63.,  63.,  63.,
        69.,  69.,  38.,  38.,  45.,  45.,  45.,  45.,  45.,  45.,  45.,
        45.,  45.,  45.,  53.,  53.,  53.,  53.,  53.,  60.,  60.,  60.,
        60.,  60.,  60.,  60.,  60.,  60.,  60.,  60.,  66.])

N = len(LIFETIMES)




if __name__ == '__main__':
    unittest.main()
