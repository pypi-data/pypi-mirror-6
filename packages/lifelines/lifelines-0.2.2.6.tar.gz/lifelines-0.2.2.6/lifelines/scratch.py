
from lifelines.generate_datasets import *
from lifelines.estimation import AalenAdditiveFitter


#generate some hazard rates and a survival data set
n = 2000
d = 5
timeline = np.linspace(0,70,5000)

hz, coef, X = generate_hazard_rates(n,d, timeline )

T = generate_random_lifetimes(hz, timeline)

#print X.ix[:10]

#fit it to Aalen's model

aaf = AalenAdditiveFitter(penalizer=0.5, fit_intercept=False)
aaf.fit(T,X, censorship=None)


#predictions
T_pred = aaf.predict_median(X)
hz_pred = aaf.predict_cumulative_hazard(X)
sv_pred = aaf.predict_survival_function(X)
m_pred = aaf.predict_expectation(X)

print m_pred

figure()
scatter( T_pred.values, T)
plt.ylabel('actual')
plt.xlabel('pred')

figure()
scatter( log(T_pred.values), np.log(T))
plt.ylabel('actual')
plt.xlabel('pred')

figure()
scatter( m_pred, T)
plt.ylabel('actual')
plt.xlabel('pred')

figure()
scatter( log(m_pred), log(T))
plt.ylabel('actual')
plt.xlabel('pred')



print (T_pred.values > T).mean()

figure()
i = T.argmax()
plot( timeline, cumulative_quadrature(hz[i].values[:,None].T, timeline)[0,:] )
hz_pred[i].plot()
#hz[i].plot()

figure()
sv_pred[i].plot()


#test the yaun_loss
from lifelines.utils import yaun_loss

#yaun_loss(fitter, T_true, T_pred, X_train, T_train, censorship=None)


print yaun_loss(aaf, T, T_pred.values, X, T, C)