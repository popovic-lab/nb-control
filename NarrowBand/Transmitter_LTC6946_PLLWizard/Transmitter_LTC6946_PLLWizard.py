"""
Written by: Leonardo Fortaleza

 Description:
		Module for controlling the LTC6946 (demo board DC1705C) through the PLLWizard software and the DC590B demo controller.

		Requires installation of pywinauto, pyautogui and pywin32 libraries.
		In some cases it may also require Microsoft Visual C++ 2008 SP1 Redistributable Package (x64).

Functions::

	init : initializes PLLWizard software for LTC6946 PLL frequency synthesizer (demo board DC1705C, demo controller DC590B).

	freq_set : sets a Tx frequency by loading a preset for the LTC6946 PLL Frequency Synthesizer, optimized for manual input.

	freq_set_auto : freq_set optimized for automated scripts.

	freq_output_mute: mutes RF output, turning off Tx.

Inner functions::

	_freq2str

	_is_freq_range_s
"""
# Standard library imports
import os
import ctypes
from time import sleep

# Third party imports
import pywinauto.keyboard as keyboard
from pywinauto.application import Application, win32defines
from pywinauto.application import ProcessNotFoundError
#from pywinauto.win32functions import SetForegroundWindow, ShowWindow
from pywinauto.win32functions import ShowWindow
from pyautogui import typewrite


import warnings
# to supress "UserWarning: 32-bit application should be automated using 32-bit Python (you use 64-bit Python)"
warnings.simplefilter('ignore', category=UserWarning)

app = Application()

def	init(appl_path = "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe"):
	"""Initialize PLLWizard software for LTC6946 PLL frequency synthesizer (demo board DC1705C, demo controller DC590B).

	Initializes the PLLWizard application, closing the initial message box (A DC590B was/was not found).

	In case the device is not connected to a USB port and powered on, another message box will appear stating
		"Can't find DC590B. Disable Communication?" The function responds "No".

	If PLLWizard is not installed in the default directory or specified as appl_path when calling the function,
	an error message is displayed.

	Parameters
	----------
	appl_path : str, optional
		PLLWizard.exe application path, by default "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe"
	"""

	try:
		app.connect(path = appl_path)
	except ProcessNotFoundError:
		if os.path.isfile(appl_path):
			app.start(appl_path)

			dlg = app.PLLWizard
			dlg.wait("exists enabled visible ready")
			sleep(0.5)
			keyboard.send_keys("{ENTER}")

			if dlg.exists():
				keyboard.send_keys("{RIGHT}""{ENTER}")
				pass

		else:
			MessageBox = ctypes.windll.user32.MessageBoxW
			MessageBox(None, u"PLLWizard is not installed in the specified path.\n\nPlease provide the correct path or install PLLWizard in the default directory.", u"Error", 0)
			return

def freq_set(freq,appl_path = "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe",
	fname = "C:\Users\leofo\OneDrive - McGill University\Documents McGill\Data\PLL Wizard Screenshots\Set Files\ new design1 FREQMHz 12_5MHz RFOUT.pllset"):
	"""Set Tx frequency for the LTC6946 PLL Frequency Synthesizer.

	Function to set a Tx frequency by loading a preset for the LTC6946 PLL Frequency Synthesizer.

	Initially it converts the numeric or string frequency input (freq) into a properly formatted string, using _freq2str().

	Then, it verifies if the input frequency is in the range of presets available using _is_freq_range_s().

	For valid frequencies, it connect to the Linear Technology PLLWizard software and loads the appropriate preset file.

	Parameters
	----------
	freq : float or int or string
		frequency in MHz
	appl_path : str, optional
		 optional PLLWizard.exe application path, by default "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe"
	fname : str, optional
		optional generic preset file path and name in string format,
		with the word "FREQ" replacing the frequency in MHz,
		by default "C:\Users\leofo\OneDrive - McGill University\Documents McGill\Data\PLL Wizard Screenshots\Set Files\ new design1 FREQMHz 12_5MHz RFOUT.pllset"
	"""

	freq_str = _freq2str(freq)
	if _is_freq_range_s(freq_str):
		app.connect(path = appl_path)
		pllwiz = app.window(best_match="Linear Technology PLLWizard")
		dlg_mes = app.window(best_match="PLLWizard")
		if dlg_mes.exists():
			keyboard.send_keys("{RIGHT}""{ENTER}")
			pass
		if pllwiz.exists():
			pllwiz.set_focus()
			pllwiz.wait("exists enabled visible ready")
			keyboard.send_keys("%f""{DOWN}""{ENTER}")
			fname = fname.replace("FREQ",freq_str)
			typewrite(fname)
			typewrite("\n")
	else:
		print("{} is not a valid frequency".format(freq))

def freq_set_auto(freq,appl_path = "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe",
	fname = "C:\Users\leofo\OneDrive - McGill University\Documents McGill\Data\PLL Wizard Screenshots\Set Files\ new design1 FREQMHz 12_5MHz RFOUT.pllset", verbose = False):
    """Set Tx frequency for the LTC6946 PLL Frequency Synthesizer, assumes input frequency is properly formatted string.

	Use this for automated scripts.

    Function doesn't check if frequency is in the appropriate format or range (saving computational time).

	Function to set a Tx frequency by loading a preset for the LTC6946 PLL Frequency Synthesizer.

    It connect to the Linear Technology PLLWizard software and loads the appropriate preset file, if it exists.

	Parameters
	----------
	freq : float or int or string
		frequency in MHz
	appl_path : str, optional
		 optional PLLWizard.exe application path, by default "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe"
	fname : str, optional
		optional generic preset file path and name in string format,
		with the word "FREQ" replacing the frequency in MHz,
		by default "C:\Users\leofo\OneDrive - McGill University\Documents McGill\Data\PLL Wizard Screenshots\Set Files\ new design1 FREQMHz 12_5MHz RFOUT.pllset"
	verbose : bool, optional
		set True to print each frequency being set, by default False
	"""

    if verbose:
        print("\rSetting frequency: {} MHz                         ".format(freq)),
    app.connect(path = appl_path)
    pllwiz = app.window(best_match="Linear Technology PLLWizard")
    dlg_mes = app.window(best_match="PLLWizard")
    if dlg_mes.exists():
        keyboard.send_keys("{RIGHT}""{ENTER}")
        pass
    if pllwiz.exists():
        if pllwiz.has_style(win32defines.WS_MINIMIZE): # if minimized
            ShowWindow(pllwiz.wrapper_object(), 9) # restore window state
        else:
            #SetForegroundWindow(pllwiz.wrapper_object()) #bring to front
			pllwiz.wrapper_object().set_focus()
        pllwiz.wait("exists enabled visible ready")
        keyboard.send_keys("%f""{DOWN}""{ENTER}")
        fname = fname.replace("FREQ",freq)
        load = app.window(best_match="Load Settings")
        load.wait("exists enabled visible ready")
        typewrite(fname)
        typewrite("\n")
        #sleep(0.1)

def freq_output_mute(appl_path = "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe",
	fname = "%UserProfile%\Documents\Documents McGill\Data\PLL Wizard Screenshots\Set Files\ new design1 2200MHz 12_5MHz RFOUT_MUTED.pllset", verbose = False):
    """Mute RF Output for the LTC6946 PLL Frequency Synthesizer (stops output), internally setting frequency at 2200 MHz.

	Parameters
	----------
	appl_path : str, optional
		 optional PLLWizard.exe application path, by default "%ProgramFiles(x86)%/LTC/PLLWizard/PLLWizard.exe"
	fname : str, optional
		optional generic preset file path and name in string format,
		by default "C:\Users\leofo\OneDrive - McGill University\Documents McGill\Data\PLL Wizard Screenshots\Set Files\ new design1 2200MHz 12_5MHz RFOUT_MUTED.pllset"
	verbose : bool, optional
		set True to print each frequency being set, by default False
	"""

    if verbose:
        print("\rMuted output."),
    app.connect(path = appl_path)
    pllwiz = app.window(best_match="Linear Technology PLLWizard")
    dlg_mes = app.window(best_match="PLLWizard")
    if dlg_mes.exists():
        keyboard.send_keys("{RIGHT}""{ENTER}")
        pass
    if pllwiz.exists():
        if pllwiz.has_style(win32defines.WS_MINIMIZE): # if minimized
            ShowWindow(pllwiz.wrapper_object(), 9) # restore window state
        else:
            #SetForegroundWindow(pllwiz.wrapper_object()) #bring to front
			pllwiz.wrapper_object().set_focus()
        pllwiz.wait("exists enabled visible ready")
        keyboard.send_keys("%f""{DOWN}""{ENTER}")
        fname = fname
        load = app.window(best_match="Load Settings")
        load.wait("exists enabled visible ready")
        typewrite(fname)
        typewrite("\n")

def _freq2str(freq_num):
	"""Convert numeric or string frequency value in MHz (freq_num) to compatible string value.

	Replaces dots (.) with underscores (_) for non-integers in freq_num.

	Parameters
	----------
	freq_num : float or int or string
		frequency in MHz
	"""

	if str(freq_num).replace('.','',1).isdigit():
	    if float(freq_num).is_integer():
			n = int(freq_num)
			return "{}".format(n)
	    else:
			n = float(freq_num)
			s = "{:.1f}".format(n)
			return s.replace(".","_")
	else:
	    return freq_num

def _is_freq_range_s(freq):
	"""Check if frequency has a valid PLLWizard settings file.

	Parameters
	----------
	freq : string
		frequency in MHz and in compatible string format (underscore "_" instead of dot ".")
	"""
	range = {"2000","2012_5","2025","2037_5","2050",
	"2062_5","2075","2087_5","2100","2112_5","2125","2137_5",
	"2150","2162_5","2175","2187_5","2200","1550","1600",
	"1650","1700","1750","1800","1850","1900","1950",
	"2250","2300","2350","2400","2450","3100","3150","3200"}

	if freq in range:
		return True
	else:
		return False

def _is_freq_range_(freq):
	"""Check if frequency has a valid PLLWizard settings file.

	Parameters
	----------
	freq : int or float
		frequency in MHz
	"""
	range = {2000, 2012.5, 2025, 2037.5, 2050, 2062.5, 2075, 2087.5, 2100, 2112.5, 2125, 2137.5,
	2150, 2162.5, 2175, 2187.5, 2200, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2250,
	2300, 2350, 2400, 2450, 3100, 3150, 3200}

	if freq in range:
		return True
	else:
		return False


if __name__ == '__main__':
	"""
	NUM_SAMPLES = 64*1024
	spi_reg = []

	data_file = "%UserProfile%/Documents/Documents McGill/Data/PScope/DATE/Phantom PHA/ANG deg/Plug PLU/Phantom PHA Plug PLU ANG deg FREQMHz ANTPAIR Iter ITE Rep REP.adc"
	fft_file = "%UserProfile%/Documents/Documents McGill/Data/PScope/DATE/Phantom PHA/ANG deg/Plug PLU/Phantom PHA Plug PLU ANG deg FREQMHz ANTPAIR Iter ITE Rep REP.fft"
	fset_file = "%UserProfile%\\Documents\\Documents McGill\\Data\\PLL Wizard Screenshots\\Set Files\\new design1 FREQMHz 12_5MHz RFOUT.pllset"

	cal_data_file = "%UserProfile%/Documents/Documents McGill/Data/PScope/DATE/Calibration/Calibration Iter ITE.adc"
	cal_fft_file = "%UserProfile%/Documents/Documents McGill/Data/PScope/DATE/Calibration/Calibration Iter ITE.fft"

	date = "2019_07_03"
	Phantom = 1
	Angle = 0
	Plug = 2

	rep = 1
	"""

	f_range = ("2000",
				"2012_5",
				"2025",
				"2037_5",
				"2050",
				"2062_5",
				"2075",
				"2087_5",
				"2100",
				"2112_5",
				"2125",
				"2137_5",
				"2150",
				"2162_5",
				"2175",
				"2187_5",
				"2200")

	init()
	freq_set_auto(f_range[0])