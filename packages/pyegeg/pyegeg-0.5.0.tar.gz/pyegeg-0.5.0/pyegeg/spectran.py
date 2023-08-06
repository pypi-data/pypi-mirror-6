"""
In this module functions for spectral analysis are collected 

"""

from scipy.fftpack import fft
import scipy.signal as spsig
import numpy as np

def stft(x, dt, window_type = 'hanning', window_len = 1200, step = 120, z_add = True):
	"""
	Calculating of STFT
	
	:param x: Samples
	:type x: numpy.ndarray
	
	:param dt: Sampling period
	:type dt: float
	
	:param length: Length of window in samples
	:type length: int
	
	:param window_type: Type of window
	:type window_type: str
	
	:param step: Step for STFT in samples
	:type step: int
	
	:returns: list
	
	"""
	window = spsig.get_window(window_type, window_len)
	X=[]
	for i in range(0, len(x)-window_len, step):
		if z_add:
			tmp = np.zeros(len(x))
			tmp[i:i + window_len] = x[i:i + window_len]*window
		else:
			tmp = x[i:i + window_len]*window
		X.append(abs(fft(tmp)))
		
	return X

