"""
In this module functions for parameters calculating are collected 

"""

import scipy as sp
import numpy as np
from scipy.fftpack import fft
from scipy import signal
import scipy.signal as spsig
from collections import OrderedDict
import pyegeg.spectran as span


def dominant_frequency(x, dt, fbounds = [0.03, 0.07], spectrum = []):
	"""
	Dominant frequency search
	
	:param x: Sample sequence
	:type x: numpy.ndarray
	
	:param dt: Sampling period
	:type dt: float

	:param fbounds: Frequencies bounds
	:type fbounds: list
	
	:param spectrum: Pre-calculated spectrum. By default it calculates inside this function.
	:type spectrum: numpy.ndarray
	
	:returns: float 
	
	"""
	
	if len(spectrum) == 0:
		spectrum = abs(fft(x))
	
	f = np.fft.fftfreq(len(x),dt)
	ind = (f>=fbounds[0]) & (f<=fbounds[1])
	df_ind = spectrum[ind].argmax()
	return f[ind][df_ind]

def slide_proc(x, dt, procedure, fbounds=[0.03,0.07], stft_res = [], stft_args = ('hamming', 1200, 120, True)):
	"""
	Calculation of the result of the procedure along the time axis using STFT.
	
	:param x: Sample sequence
	:type x: numpy.ndarray
	
	:param dt: Sampling period
	:type dt: float
	
	:param procedure: Name of the function which will be applied on every step
	:type procedure: function

	:param fbounds: Frequencies bounds
	:type fbounds: list
	
	:param stft_res: Pre-calculated result of STFT
	:type stft_res: list
	
	:param stft_args: STFT function arguments (see pyegeg.spectran.stft). Required if STFT didn't calculated yet.
	:type stft_args: list
	
	:returns: list
	
	"""	
	
	if len(stft_res) == 0:
		stft_res = span.stft(x, dt, *stft_args)
	
	res = []
	for spect in stft_res:
		res.append(procedure(x, dt, fbounds, spect))
		
	return res

def kritm(x, dt, fbounds=[0.03, 0.07], spectrum=[]):
	"""
	Normalized Kritm parameter
	
	:param x: Sample sequence
	:type x: numpy.ndarray
	
	:param dt: Sampling period
	:type dt: float

	:param fbounds: Frequencies band
	:type fbounds: list
	
	:param spectrum: Pre-calculated spectrum. By default it calculates inside this function.
	:type spectrum: numpy.ndarray
	
	:returns: float 
	
	"""

	if len(spectrum) == 0:
		spectrum = abs(fft(x))
	
	f = np.fft.fftfreq(len(x),dt)
	ind = (f>=fbounds[0]) & (f<=fbounds[1])
	spectrum = spectrum[ind]
	return sum([abs(spectrum[i] - spectrum[i-1]) for i in range(0,len(spectrum))]) / len(spectrum) / spectrum.max()

def power(x, dt, fbounds=[0.03,0.07], spectrum=[]):
	"""
	Power of the part of the specturm
	
	:param x: Sample sequence
	:type x: numpy.ndarray
	
	:param dt: Sampling period
	:type dt: float

	:param fbounds: Frequencies band
	:type fbounds: list
	
	:param spectrum: Pre-calculated spectrum. By default it is calculated within this function.
	:type spectrum: numpy.ndarray
	
	:returns: float 
	
	"""

	if len(spectrum) == 0:
		spectrum = abs(fft(x)) / len(x) * 2
	else:
		spectrum /= (len(x) / 2)
		
	f = np.fft.fftfreq(len(x),dt)
	ind = (f>=fbounds[0]) & (f<=fbounds[1])
	return sum(spectrum[ind]**2)
	
def DFIC(x, dt, fbounds = [0.03, 0.07], stft_res = [], stft_args = ('hamming', 1200, 120, True)):
	"""
	Dominant frequency instability coefficient
	
	:param x: Sample sequence
	:type x: numpy.ndarray
	
	:param dt: Sampling period
	:type dt: float

	:param fbounds: Frequencies band
	:type fbounds: list

	:param spectrum: Pre-calculated spectrum matix (calculated by stft). By default it calculates inside this function.
	:type spectrum: list
	
	:param stft_args: Arguments for stft function
	:type stft_args: tuple
	
	:returns: float 
	
	"""
	df_in_time = slide_proc(x=x, dt=dt, procedure=dominant_frequency, fbounds=fbounds, stft_res=stft_res, stft_args=stft_args)
	return np.var(df_in_time) / np.mean(df_in_time)
