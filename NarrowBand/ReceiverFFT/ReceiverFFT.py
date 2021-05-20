"""
	Created by: Noe Quintero
	E-mail: nquintero@linear.com
	Copyright (c) 2015, Linear Technology Corp.(LTC)
	All rights reserved.
	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are met:
	1. Redistributions of source code must retain the above copyright notice,
	   this list of conditions and the following disclaimer.
	2. Redistributions in binary form must reproduce the above copyright
	   notice, this list of conditions and the following disclaimer in the
	   documentation and/or other materials provided with the distribution.
	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
	AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
	IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
	ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
	LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
	CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
	SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
	INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
	CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
	ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
	POSSIBILITY OF SUCH DAMAGE.
	The views and conclusions contained in the software and documentation are
	those of the authors and should not be interpreted as representing official
	policies, either expressed or implied, of Linear Technology Corp.

	Adapted by: Leonardo Fortaleza

	Description:
		The purpose of this module is to provide FFT of collected data with PScope compatible window formats
		and also provide a plot function that allows the use of other types of FFT windowing.
		In addition to adding new FFT based functions, it replaces the functions.plot function.
"""
import sys
sys.path.insert(1,'%UserProfile%/Documents/linear_technology/linear_lab_tools64/python/')

#import llt.common.exceptions as err
#import llt.common.ltc_controller_comm as comm
import math as m
import time
import llt.utils.sin_params as sp
import numpy as np
import fft_window

def make_vprint(verbose):
	if verbose:
		def vprint(string):
				print string
	else:
		def vprint(string):
				pass
	return vprint

def ReceiverFFT(num_bits, data, channel = 0, wind = 'hann'):
    """Calculate FFT magnitude in dBFS for data collected from a specified channel, using a selected FFT window type.

	Uses the Linear Technology functions.plot.py way of calculating the FFT.
	"""
    num_samples = len(data)
    adc_amplitude = 2.0**(num_bits-1)
    data_no_dc = data - np.average(data) # Remove DC to avoid leakage when windowing


    windowed_data = data_no_dc * fft_window(num_samples, wind)# Apply window (Hann is default)
    freq_domain = np.fft.fft(windowed_data)/(num_samples) # FFT
    freq_domain = freq_domain[0:num_samples/2+1]
    freq_domain_magnitude = np.abs(freq_domain) # Extract magnitude
    freq_domain_magnitude[1:num_samples/2] *= 2
    freq_domain_magnitude_db = 20 * np.log10(freq_domain_magnitude/adc_amplitude)

    return freq_domain_magnitude_db



def plot(num_bits, data, channel = 0, wind = 'hann', verbose = False):
	"""Plot time domain and frequency domain data for a single channel, as designed by Linear Technology.

	Adapted to use selectable FFT window type.
	"""
	vprint = make_vprint(verbose)

	from matplotlib import pyplot as plt
	from matplotlib.font_manager import FontProperties

	vprint("Plotting channel " + str(channel) + " time domain.")

	num_samples = len(data)

	plt.figure(channel)
	plt.clf()
	plt.subplot(2,1,1)
	fig = plt.gcf()
	fig.subplots_adjust(right=0.68)
	plt.plot(data)
	plt.title('Ch' + str(channel) + ': Time Domain Samples')

	vprint("FFT'ing channel " + str(channel) + " data.")

	adc_amplitude = 2.0**(num_bits-1)

	data_no_dc = data - np.average(data) # Remove DC to avoid leakage when windowing

	windowed_data = data_no_dc * fft_window(num_samples, wind)# Apply window (Hann is default)
	freq_domain = np.fft.fft(windowed_data)/(num_samples) # FFT
	freq_domain = freq_domain[0:num_samples/2+1]
	freq_domain_magnitude = np.abs(freq_domain) # Extract magnitude
	freq_domain_magnitude[1:num_samples/2] *= 2
	freq_domain_magnitude_db = 20 * np.log10(freq_domain_magnitude/adc_amplitude)

	vprint("Plotting channel " + str(channel) + " frequency domain.")

	ax = plt.subplot(2, 1, 2)

	ax.set_title('Ch' + str(channel) + ': FFT')
	plt.plot(freq_domain_magnitude_db)

	try:
		harmonics, snr, thd, sinad, enob, sfdr, floor = sp.sin_params(data)

		sig_amp = m.sqrt(abs(harmonics[1][0]))
		fund_dbsf = 20 * m.log10(sig_amp/2**(num_bits-1))
		denominator = 2**(num_bits-1)
		f2 = abs(harmonics[2][0])
		f2 = 20 * m.log10(m.sqrt(f2  / denominator)) if f2 != 0 else -float('inf')

		f3 = abs(harmonics[3][0])
		f3 = 20 * m.log10((m.sqrt(f3))/2**(num_bits-1)) if f3 != 0 else -float('inf')

		f4 = abs(harmonics[4][0])
		f4 = 20 * m.log10((m.sqrt(f4))/2**(num_bits-1)) if f4 != 0 else -float('inf')

		f5 = abs(harmonics[5][0])
		f5 = 20 * m.log10((m.sqrt(f5))/2**(num_bits-1)) if f5 != 0 else -float('inf')

		# The floor is given in dBc. We add the fundimantal to convert to dBFs
		floor += fund_dbsf
		plt.plot([floor for number in xrange(num_samples/2-1)], 'y')

		max_code = max(data)
		min_code = min(data)
		avg = np.mean(data)

		font = FontProperties()
		font.set_family('monospace')
		fig.text(0.72,0.40, "F1 BIN:    " + str(harmonics[1][1]) + "\nF1 Amp:   " + "{0:.1f}".format(round(fund_dbsf,1)) +
			" dBFS\nF2 Amp:   " + "{0:.1f}".format(round(f2,1)) +
			" dBFS\nF3 Amp:   " + "{0:.1f}".format(round(f3,1)) +
			" dBFS\nF4 Amp:   " + "{0:.1f}".format(round(f4,1)) +
			" dBFS\nF5 Amp:   " + "{0:.1f}".format(round(f5,1)) +
			" dBFS\n\nSNR:      " + "{0:.1f}".format(round(snr,1)) + " dB\nSINAD:    " +
			"{0:.1f}".format(round(sinad,1)) + " dB\nTHD:      " +
			"{0:.1f}".format(round(thd,1)) + " dB\nSFDR:     " +
			"{0:.1f}".format(round(sfdr,1))  + " dB\nENOB:     " +
			"{0:.1f}".format(round(enob,1)) + " bits\nMax:      " + str(max_code) +
			"\nMin:      " + str(min_code) + "\nDC Level: " +
			"{0:.1f}".format(round(avg,1)) + "\nFloor:    " +
			"{0:.1f}".format(round(floor,1)) + " dBFS", fontproperties=font)

		ax.annotate('1',
			xy=(harmonics[1][1], fund_dbsf), xycoords='data',
			xytext=(0, -10), textcoords='offset points',
			horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')

		ax.annotate('2',
			xy=(harmonics[2][1], f2), xycoords='data',
			xytext=(0, 0), textcoords='offset points',
			horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
		ax.annotate('3',
			xy=(harmonics[3][1], f3), xycoords='data',
			xytext=(0, 0), textcoords='offset points',
			horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
		ax.annotate('4',
			xy=(harmonics[4][1], f4), xycoords='data',
			xytext=(0, 0), textcoords='offset points',
			horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
		ax.annotate('5',
			xy=(harmonics[5][1], f5), xycoords='data',
			xytext=(0, 0), textcoords='offset points',
			horizontalalignment='right', verticalalignment='bottom', color ="green", fontweight='bold')
	except:
		fig.text(0.75,0.8, "No AC Signal\nDetected")
	plt.show()

def plot_channels(num_bits = 14, window = 'hann', *channels, **verbose_kw):
	"""Plot data collected in both time domain and frequency domain.

	Function as developed by Linear Techinology with the addition of FFT window selection.
	"""
	verbose = verbose_kw.get("verbose", False)
	for channel_num, channel_data in enumerate(channels):
		plot(num_bits, channel_data, channel_num, window, verbose)

def fft_channels(num_bits,num_samples, window = 'hann', *channels, **verbose_kw): #not clear what this function does, need to add return statement
    verbose = verbose_kw.get("verbose", False)
    tmp1 = int(num_samples*0.5 +1)
    tmp2 = int(len(channels))
    out = np.zeros((tmp2,tmp1))
    for channel_num, channel_data in enumerate(channels):
        out[channel_num,:]= ReceiverFFT(num_bits, channel_data, channel_num, window)
    return out

def save_for_pscope(out_path = 'data.adc', num_bits = 14, is_bipolar = True, num_samples = 1*1024, dc_num = 'DC_1513B-AA',
						 ltc_num = 'LTM9004', *data):
	"""Save data in PScope .adc format (csv type file).

	As defined by Linear Technology.

	Keyword arguments (all optional except for data)::
		out-path -- file path in string format
		num_bits -- integer number of bits on the receiver ADC (default is 14, which is the case for the LTM9004)
		is_bipolar -- boolean stating if the ADC operates with both negative and positive values (True) or just positive values (False)
				Default is True, which is the case for the LTM9004
		num_samples -- integer number of samples setting for the ADC on the receiver 
					(multiples of 1024 in powers of 2, up to 64*1024=65,536)
					Default is 1024
		dc_num -- string with the name/number of the demonstration circuit (default is 'DC_1513B-AA', used with the LTM9004)
		ltc_num -- string with the name/number of the device (default is 'LTM9004')
		*data -- array with collected data in the time domain, each column representing a channel
	"""
	num_channels = len(data)
	if num_channels < 0 or num_channels > 16:
		raise ValueError("pass in a list for each channel (between 1 and 16)")

	full_scale = 1 << num_bits
	if is_bipolar:
		min_val = -full_scale / 2
		max_val = full_scale / 2
	else:
		min_val = 0
		max_val = full_scale

	sample_rate = 125.0
	with open(out_path, 'w') as out_file:
		out_file.write('Version,115\n')
		out_file.write('Retainers,0,{0:d},{1:d},1024,0,{2:0.15f},1,1\n'.format(num_channels, num_samples, sample_rate))
		out_file.write('Placement,44,0,1,-1,-1,-1,-1,10,10,1031,734\n')
		out_file.write('DemoID,' + dc_num + ',' + ltc_num + ',0\n')
		for i in range(num_channels):
			out_file.write(
				'RawData,{0:d},{1:d},{2:d},{3:d},{4:d},{5:0.15f},{3:e},{4:e}\n'.format(
					i+1, num_samples, num_bits, min_val, max_val, sample_rate ))
		for samp in xrange(num_samples):
			out_file.write(str(data[0][samp]))
			for ch in range(1, num_channels):
				out_file.write(', ,' + str(data[ch][samp]))
			out_file.write('\n')
		out_file.write('End\n')

def save_for_pscope_fft(out_path = 'data.fft', num_bits = 14, is_bipolar = True, num_samples = 1*1024, dc_num = 'DC_1513B-AA',
			ltc_num = 'LTM9004', window = 'hann', *data):
	"""Save data in PScope .fft format (csv type file).

	Adaptation of the Linear Technology save_for_pscope function for FFT data.

	Keyword arguments (all optional except for data)::
		out-path -- file path in string format
		num_bits -- integer number of bits on the receiver ADC (default is 14, which is the case for the LTM9004)
		is_bipolar -- boolean stating if the ADC operates with both negative and positive values (True) or just positive values (False)
				Default is True, which is the case for the LTM9004
		num_samples -- integer number of samples setting for the ADC on the receiver
					(multiples of 1024 in powers of 2, up to 64*1024=65,536)
					Default is 1024
		dc_num -- string with the name/number of the demonstration circuit (default is 'DC_1513B-AA', used with the LTM9004)
		ltc_num -- string with the name/number of the device (default is 'LTM9004')
		window -- FFT window type (default is 'hann') - see fft_window module
		*data -- array with collected data in the frequency domain, each column representing a channel
	"""
	num_channels = len(data)
	if num_channels < 0 or num_channels > 16:
		raise ValueError("pass in a list for each channel (between 1 and 16)")

	"""full_scale = 1 << num_bits
	if is_bipolar:
		min_val = -full_scale / 2
		max_val = full_scale / 2
	else:
		min_val = 0
		max_val = full_scale"""

	"""	for ch in range(0, num_channels):
		fft_data[ch] = ReceiverFFT(num_bits, data[ch], ch, window)"""

	fft_data = fft_channels(num_bits, num_samples, window, *data)

	sample_rate = 125.0
	with open(out_path, 'w') as out_file:
		out_file.write('Version,115\n')
		out_file.write('FFTMagnitude,{0:d},{1:d},{2:0.15f}\n'.format(num_channels, num_samples/2, sample_rate))
		"""out_file.write('Placement,44,0,1,-1,-1,-1,-1,10,10,1031,734\n')"""
		"""out_file.write('DemoID,' + dc_num + ',' + ltc_num + ',0\n')"""
		"""for i in range(num_channels):
			out_file.write(
				'RawData,{0:d},{1:d},{2:d},{3:d},{4:d},{5:0.15f},{3:e},{4:e}\n'.format(
					i+1, num_samples, num_bits, min_val, max_val, sample_rate ))"""
		for samp in xrange(num_samples/2+1):
			out_file.write(str(fft_data[0][samp]))
			for ch in range(1, num_channels):
				out_file.write(', ,' + str(fft_data[ch][samp]))
			out_file.write('\n')
		out_file.write('End\n')

if __name__ == '__main__':

	num_bits = 14
	num_samples = 65536
	channel_1 = [int(8192 * m.cos(0.12 * d)) for d in range(num_samples)]
	channel_2 = [int(8192 * m.cos(0.034 * d)) for d in range(num_samples)]
	save_for_pscope('test.adc', num_bits, True, num_samples, 'DC9876A-A', 'LTC9999',channel_1, channel_2)
	save_for_pscope_fft('test.fft', num_bits, True, num_samples, 'DC9876A-A', 'LTC9999','hann',channel_1, channel_2)
	#out = fft_channels(num_bits,num_samples,'hann', channel_1,channel_2)
	#print("Channel 0:")
	#print(out[0,:])

	#print("Channel 1:")
	#print(out[1,:])"""
	#print(type(out))
