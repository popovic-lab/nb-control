# Python 2.7
# 2020-09-04

# Version 4.0.2
# Last updated on 2021-08-12

# Leonardo Fortaleza (leonardo.fortaleza@mail.mcgill.ca)

"""
Description:
        Module for controlling the narrow band system. The main function is to initiate a frequency sweep, recording and optionally plotting the data collected
        by the DC Receiver.

Class::
        Dc1513bAa(dc890.Demoboard): defined for communication with the D890B demo board.

Functions::

        ant_sweep : performs scans for selected antenna pairs, for all selected input frequencies
                    in order order antenna pair switching -> frequency switching

        ant_sweep_alt : performs scans for selected antenna pairs, for all selected input frequencies
                        in order frequency switching -> antenna pair switching

        cal_system : performs a calibration scan, for which there are 3 types

Inner functions::

        _generate_file_path

        _generate_file_path2

        _generate_cal_file_path

        _save_json_exp

        _save_json_cal

Written by: Leonardo Fortaleza

With code by Anne-Marie Zaccarin on Dc1513bAa(dc890.Demoboard) and its data collection, adapted from Linear Technology.
"""
# Standard library imports
import copy
from datetime import datetime
import json
import os, sys
import time

# checks proper folder for Linear Lab Tools and adds to path
lltpath = '{}/Documents/Analog Devices/linear_lab_tools64/python/'.format(os.environ['USERPROFILE'])
if not os.path.exists(os.path.dirname(lltpath)):
    lltpath = '{}/Documents/linear_technology/linear_lab_tools64/python/'.format(os.environ['USERPROFILE'])
sys.path.insert(1,lltpath)

# Third-party imports
import numpy as np
from timeit import default_timer as timer
from tqdm.auto import tqdm

# Local  Linear Technology imports
import llt.common.constants as consts
import llt.common.dc890 as dc890
import llt.common.functions as funcs

# Local application imports
from ReceiverFFT import ReceiverFFT as rfft
from SwitchingMatrix import switching_matrix as swm
from Transmitter_LTC6946 import ltc6946_serial as fsynth


class Dc1513bAa(dc890.Demoboard):
    """
        A DC890 demo board with settings for the DC1513B-AA.
    """

    def __init__(self, spi_registers, verbose = False):
        dc890.Demoboard.__init__(self,
                                dc_number           = 'DC_1513B-AA',
                                fpga_load           = 'CMOS',
                                num_channels        = 2,
                                is_positive_clock   = False,
                                num_bits            = 14,
                                alignment           = 14,
                                is_bipolar          = True,
                                spi_reg_values      = spi_registers,
                                verbose             = verbose)

def ant_sweep(meas_parameters, window = 'hann', do_plot = False, do_FFT = False, save_json = True, display=False):
    """Execute frequency sweep and data acquisition, recording files for time and frequency domain.

    Performs narrow band system measurements by setting discrete input frequencies with the LTC6946 PLL Frequency Synthesizer
    and acquiring data with the LTM9004 DC Receiver.

    This function uses serial control for the frequency synthesizer and performs in order: switch antenna pair  ->  switch frequency. 

    Parameters
    ----------
    meas_parameters : dict
        dictionary containing several measurement parameters for the experiment (see details after parameters)
    window : str, optional
        FFT window to be used (see fft_window module), by default 'hann'
    do_plot : bool, optional
        set True to plot the data on the terminal, by default False
    do_FFT : bool, optional
        set True to record the FFT, by default False
    save_json : bool, optional
        set True to save JSON dictionary file with experiment configuration, by default True

    For the meas_parameters dictionary:
    ----------------------------------------

    freq_range: list or tuple of strings
        list or tuple of strings containing the input frequency range in MHz, with underscores "_" replacing dots "."

    data_file: str
        string with generic file name and path for the time domain data file to be written,
        using placeholders for several details such as "FREQ" for the current frequency

    date: str
        string in the format "yyyy_mm_dd" (placeholder in file names is "DATE")

    Phantom: int
        phantom number (placeholder in file names is "PHA")

    Angle: int
        phantom rotation angle (placeholder in file names is "ANG")

    Plug: int
        plug number (placeholder in file names is "PLU")

    rep: int
        user determined number counting the repetitions of measurement after repositioning,
        requires calling the function again for each repetition (placeholder in file names is "REP")

    iter: int
        number of iteations to be performed of full frequency sweeps (for checking repeatability of measurements)
        (placeholder in file names is "ITE")

    window: str
        FFT window to be used, default is 'hann' (see fft_window module)
    """

    start = timer()

    if save_json:
        meas_parameters["start"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for key in ["cal_data_file", "cal_fft_file"]:
            del meas_parameters[key]

        meas_parameters["type"] =  "measurement configuration parameters"

    ite = meas_parameters["iter"]

    pairs = meas_parameters["pairs"]

    _generate_file_path(meas_parameters = meas_parameters)

    num_samples = meas_parameters["num_samples"]
    spi_registers = meas_parameters["spi_registers"]
    verbose = meas_parameters["verbose"]

    freq_range = meas_parameters["freq_range"]

    window = meas_parameters["fft_window"]

    fctrl = fsynth.DC590B()

    with Dc1513bAa(spi_registers, verbose) as controller:
        pbar = tqdm(range(1,ite+1), leave= True)
        for j in pbar:
            pbar.set_description("Iteration: %i" % j)
            ite_start = timer()
            for (TX, RX) in tqdm(pairs, leave= False):
                swm.set_pair(TX, RX)
                pbar2 = tqdm( range(0,len(freq_range)) , leave= False)
                for i in pbar2:
                    f_cur = freq_range[i]
                    fctrl.freq_set(freq = f_cur, verbose=verbose)
                    pbar2.set_description("Tx - %i Rx - %i @ %s MHz" % (TX, RX, f_cur))
                    data_file= _generate_file_path2(meas_parameters = meas_parameters, antenna_pair = "Tx {0:d} Rx {1:d}".format(TX,RX))
                    if not os.path.exists(os.path.dirname(data_file.replace("ITE",str(j)))):
                        os.makedirs(os.path.dirname(data_file.replace("ITE",str(j))))
                    ch0,ch1 = controller.collect(num_samples, consts.TRIGGER_NONE)
                    if do_plot:
                        tqdm.write("\rPlotting for input frequency: {} MHz".format(f_cur), end="")
                        rfft.plot_channels(controller.get_num_bits(), window,
                                            ch0, ch1,
                                            verbose=verbose)
                    rfft.save_for_pscope(data_file.replace("FREQ",f_cur).replace("ITE",str(j)), controller.num_bits, controller.is_bipolar, num_samples,
                                            'DC_1513B-AA', 'LTM9004', ch0, ch1,)
                    if do_FFT:
                        rfft.save_for_pscope_fft(data_file.replace(".adc",".fft").replace("FREQ",f_cur).replace("ITE",str(j)), controller.num_bits, controller.is_bipolar,num_samples,
                                            'DC_1513B-AA', 'LTM9004', window, ch0, ch1)

            if save_json and j != ite:
                ite_end = timer()
                meas_parameters["iter_duration"] = ite_end - ite_start
                _save_json_exp(meas_parameters = meas_parameters, iteration = j)

    fctrl.freq_set(freq = "0", verbose=verbose)
    end = timer()
    meas_parameters["meas_duration"] = str(end - start)

    if save_json:
        meas_parameters["end"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _save_json_exp(meas_parameters = meas_parameters)

def ant_sweep_alt(meas_parameters, window = 'hann', do_plot = False, do_FFT = False, save_json = True, display=False):
    """Execute frequency sweep and data acquisition, recording files for time and frequency domain.

    Performs narrow band system measurements by setting discrete input frequencies with the LTC6946 PLL Frequency Synthesizer
    and acquiring data with the LTM9004 DC Receiver.

    This function uses serial control for the frequency synthesizer and the
    order frequency switching -> antenna pair switching.

    Parameters
    ----------
    meas_parameters : dict
        dictionary containing several measurement parameters for the experiment (see details after parameters)
    window : str, optional
        FFT window to be used (see fft_window module), by default 'hann'
    do_plot : bool, optional
        set True to plot the data on the terminal, by default False
    do_FFT : bool, optional
        set True to record the FFT, by default False
    save_json : bool, optional
        set True to save JSON dictionary file with experiment configuration, by default True

    For the meas_parameters dictionary:
    ----------------------------------------

    freq_range: list or tuple of strings
        list or tuple of strings containing the input frequency range in MHz, with underscores "_" replacing dots "."

    data_file: str
        string with generic file name and path for the time domain data file to be written,
        using placeholders for several details such as "FREQ" for the current frequency

    date: str
        string in the format "yyyy_mm_dd" (placeholder in file names is "DATE")

    Phantom: int
        phantom number (placeholder in file names is "PHA")

    Angle: int
        phantom rotation angle (placeholder in file names is "ANG")

    Plug: int
        plug number (placeholder in file names is "PLU")

    rep: int
        user determined number counting the repetitions of measurement after repositioning,
        requires calling the function again for each repetition (placeholder in file names is "REP")

    iter: int
        number of iteations to be performed of full frequency sweeps (for checking repeatability of measurements)
        (placeholder in file names is "ITE")

    window: str
        FFT window to be used, default is 'hann' (see fft_window module)
    """

    start = timer()

    if save_json:
        meas_parameters["start"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for key in ["cal_data_file", "cal_fft_file"]:
            del meas_parameters[key]

        meas_parameters["type"] =  "measurement configuration parameters"

    ite = meas_parameters["iter"]

    pairs = meas_parameters["pairs"]

    _generate_file_path(meas_parameters = meas_parameters)

    num_samples = meas_parameters["num_samples"]
    spi_registers = meas_parameters["spi_registers"]
    verbose = meas_parameters["verbose"]

    freq_range = meas_parameters["freq_range"]=

    window = meas_parameters["fft_window"]

    fctrl = fsynth.DC590B()

    with Dc1513bAa(spi_registers, verbose) as controller:
        pbar = tqdm(range(1,ite+1), leave= True)
        for j in pbar:
            pbar.set_description("Iteration: %i" % j)
            ite_start = timer()
            for i in tqdm(range(0,len(freq_range))):
                f_cur = freq_range[i]
                fctrl.freq_set(freq = f_cur, verbose=verbose)
                pbar2 = tqdm( pairs , leave= False)
                for (TX, RX) in pbar2:
                    swm.set_pair(TX, RX)
                    pbar2.set_description("Tx - %i Rx - %i @ %s MHz" % (TX, RX, f_cur))
                    data_file= _generate_file_path2(meas_parameters = meas_parameters, antenna_pair = "Tx {0:d} Rx {1:d}".format(TX,RX))
                    if not os.path.exists(os.path.dirname(data_file.replace("ITE",str(j)))):
                        os.makedirs(os.path.dirname(data_file.replace("ITE",str(j))))
                    ch0,ch1 = controller.collect(num_samples, consts.TRIGGER_NONE)
                    if do_plot:
                        tqdm.write("\rPlotting for input frequency: {} MHz".format(f_cur), end="")
                        rfft.plot_channels(controller.get_num_bits(), window,
                                            ch0, ch1,
                                            verbose=verbose)
                    rfft.save_for_pscope(data_file.replace("FREQ",f_cur).replace("ITE",str(j)), controller.num_bits, controller.is_bipolar, num_samples,
                                            'DC_1513B-AA', 'LTM9004', ch0, ch1,)
                    if do_FFT:
                        rfft.save_for_pscope_fft(data_file.replace(".adc",".fft").replace("FREQ",f_cur).replace("ITE",str(j)), controller.num_bits, controller.is_bipolar,num_samples,
                                            'DC_1513B-AA', 'LTM9004', window, ch0, ch1)

            if save_json and j != ite:
                ite_end = timer()
                meas_parameters["iter_duration"] = ite_end - ite_start
                _save_json_exp(meas_parameters = meas_parameters, iteration = j)

    fctrl.freq_set(freq = "0", verbose=verbose)
    end = timer()
    meas_parameters["meas_duration"] = str(end - start)

    if save_json:
        meas_parameters["end"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _save_json_exp(meas_parameters = meas_parameters)

def cal_system(meas_parameters, do_plot = False, cal_type  = 1, do_FFT = False, save_json = True):
    """Execute calibration routine of a specified type, recording calibration data files.

    Records calibration data for the narrow band system, to be used for normalization by removing offsets from the measurements, such as the DC offset inherent to Direct Conversion Receivers.

    Files are recorded for time domain and, optionally, for frequency domain.

    Uses serial control for the frequency synthesizer.

    Parameters
    ----------
    meas_parameters : dict
        dictionary containing several measurement parameters for the experiment (see further details after parameters)
    do_plot : bool, optional
        set to True to plot of the data on the terminal, by default False
    cal_type : int, optional
        number describing the calibration type, by default 1. Possible types:
        :1: LO and RF grounded with a 50 ohm terminator
        :2: RF grounded with a 50 ohm terminator, LO active with frequencies set by freq_range
        :3: RF receives Tx and Rx connected directly (without antennas), using frequencies set by freq_range
        :4: scan of antenna pairs on air (no phantom inside the hemisphere)
    do_FFT : bool, optional
        set True to record the FFT, by default False
    save_json : bool, optional
        set True to save JSON dictionary file with experiment configuration, by default True

    For the meas_parameters dictionary:
    ----------------------------------------

    freq_range: list or tuple of str
        list or tuple of strings containing the input frequency range, with underscores "_" replacing dots "."

    cal_data_file: str
        string with generic file name and path for the time domain data file to be written,
        using placeholders for several details such as "FREQ" for the current frequency

    date: str
        string in the format "yyyy_mm_dd" (placeholder in file names is "DATE")

    rep: int
        user determined number counting the repetitions of measurement after repositioning,
        requires calling the function again for each repetition (placeholder in file names is "REP")

    iter: int
        number of iteations to be performed of full frequency sweeps (for checking repeatability of measurements)
        (placeholder in file names is "ITE")

    window: str
        FFT window to be used, default is 'hann' (see fft_window module)
    """

    start = timer()

    meas_parameters["start"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    num_samples = meas_parameters["num_samples"]
    spi_registers = meas_parameters["spi_registers"]
    verbose = meas_parameters["verbose"]

    freq_range = meas_parameters["freq_range"]

    ite = meas_parameters["iter"]
    window = meas_parameters["fft_window"]

    if save_json:
        meas_parameters["type"] =  "calibration configuration parameters"

        for key in ["Phantom", "Angle", "Plug", "data_file", "fft_file"]:
            del meas_parameters[key]

    data_file = _generate_cal_file_path(meas_parameters = meas_parameters, cal_type = cal_type)

    if cal_type == 1:
        del meas_parameters["pairs"]

        pbar = tqdm(range(1,ite+1), leave= True)
        for j in pbar:
            pbar.set_description("Iteration: %i" % j)
            ite_start = timer()
            if not os.path.exists(os.path.dirname(data_file.replace("ITE",str(j)))):
                    os.makedirs(os.path.dirname(data_file.replace("ITE",str(j))))
            with Dc1513bAa(spi_registers, verbose) as controller:
                ch0,ch1 = controller.collect(num_samples, consts.TRIGGER_NONE)
                if do_plot:
                    tqdm.write("\rPlotting calibration for grounded LO and RF:", end="")
                    rfft.plot_channels(controller.get_num_bits(), window, 
                                        ch0, ch1,
                                        verbose=verbose)
                rfft.save_for_pscope(data_file.replace("ITE",str(j)).replace(".adc"," LO GND RF GND.adc"), controller.num_bits, controller.is_bipolar, num_samples,
                                        'DC_1513B-AA', 'LTM9004', ch0, ch1)
                if do_FFT:
                    rfft.save_for_pscope_fft(data_file.replace(".adc",".fft").replace("ITE",str(j)).replace(".fft"," LO GND RF GND.fft"), controller.num_bits, controller.is_bipolar, num_samples,
                                        'DC_1513B-AA', 'LTM9004', window, ch0, ch1)

            if save_json and j != ite:
                ite_end = timer()
                meas_parameters["iter_duration"] = ite_end - ite_start
                meas_parameters["obs"] = "Type 1: Both LO and RF grounded with 50 ohm terminators. No frequency input."
                _save_json_cal(meas_parameters = meas_parameters, cal_type = cal_type, iteration = j)

    if cal_type == 2:
        del meas_parameters["pairs"]
        fctrl = fsynth.DC590B()

        with Dc1513bAa(spi_registers, verbose) as controller:
            pbar = tqdm(range(1,ite+1), leave= True)
            for j in pbar:
                pbar.set_description("Iteration: %i" % j)
                ite_start = timer()
                pbar2 = tqdm( range(0,len(freq_range)) , leave= False)
                for i in pbar2:
                    f_cur = freq_range[i]
                    fctrl.freq_set(freq = f_cur, verbose=verbose)
                    pbar2.set_description("Calibration Type 2 @ %s MHz" % f_cur)
                    if not os.path.exists(os.path.dirname(data_file.replace("ITE",str(j)))):
                        os.makedirs(os.path.dirname(data_file.replace("ITE",str(j))))
                    ch0,ch1 = controller.collect(num_samples, consts.TRIGGER_NONE)
                    if do_plot:
                        tqdm.write("\rPlotting calibration for RF grounded and LO with input frequency: {} MHz".format(f_cur), end="")
                        rfft.plot_channels(controller.get_num_bits(), window, ch0, ch1, verbose=verbose)
                    rfft.save_for_pscope(data_file.replace("ITE",str(j)).replace(".adc"," LO FREQMHz RF GND.adc".replace("FREQ",f_cur)),
                                        controller.num_bits, controller.is_bipolar, num_samples, 'DC_1513B-AA', 'LTM9004', ch0, ch1)
                    if do_FFT:
                        rfft.save_for_pscope_fft(data_file.replace(".adc",".fft").replace("ITE",str(j)).replace(".fft"," LO FREQMHz RF GND.fft".replace("FREQ",f_cur)),
                                                controller.num_bits, controller.is_bipolar, num_samples, 'DC_1513B-AA', 'LTM9004', window, ch0, ch1)

                if save_json and j != ite:
                    ite_end = timer()
                    meas_parameters["iter_duration"] = ite_end - ite_start
                    meas_parameters["obs"] = "Type 2: RF grounded with 50 ohm terminator, LO connected to frequency synthesizer."
                    _save_json_cal(meas_parameters = meas_parameters, cal_type = cal_type, iteration = j)

    if cal_type == 3:
        del meas_parameters["pairs"]
        fctrl = fsynth.DC590B()

        with Dc1513bAa(spi_registers, verbose) as controller:
            pbar = tqdm(range(1,ite+1), leave= True)
            for j in pbar:
                pbar.set_description("Iteration: %i" % j)
                ite_start = timer()
                pbar2 = tqdm( range(0,len(freq_range)) , leave= False)
                for i in pbar2:
                    f_cur = freq_range[i]
                    fctrl.freq_set(freq = f_cur, verbose=verbose)
                    pbar2.set_description("Calibration Type 3 @ %s MHz" % f_cur)
                    if not os.path.exists(os.path.dirname(data_file.replace("ITE",str(j)))):
                        os.makedirs(os.path.dirname(data_file.replace("ITE",str(j))))
                    ch0,ch1 = controller.collect(num_samples, consts.TRIGGER_NONE)
                    if do_plot:
                        tqdm.write("\rPlotting calibration for RF connected directly to Rx-Tx and LO with input frequency: {} MHz".format(f_cur), end="")
                        rfft.plot_channels(controller.get_num_bits(), window,
                                            ch0, ch1,
                                            verbose=verbose)
                    rfft.save_for_pscope(data_file.replace("ITE",str(j)).replace(".adc"," LO FREQMHz RF RxTx.adc".replace("FREQ",f_cur)),
                                        controller.num_bits, controller.is_bipolar, num_samples, 'DC_1513B-AA', 'LTM9004', ch0, ch1)
                    if do_FFT:
                        rfft.save_for_pscope_fft(data_file.replace(".adc",".fft").replace("ITE",str(j)).replace(".fft"," LO FREQMHz RF RxTx.fft".replace("FREQ",f_cur)),
                                                controller.num_bits, controller.is_bipolar, num_samples, 'DC_1513B-AA', 'LTM9004', window, ch0, ch1)

                if save_json and j != ite:
                    ite_end = timer()
                    meas_parameters["iter_duration"] = ite_end - ite_start
                    meas_parameters["obs"] = "Type 3: RF connected to Rx-Tx directly by cables (bypassing antennas) and LO connected to frequency syntesizer."
                    _save_json_cal(meas_parameters = meas_parameters, cal_type = cal_type, iteration = j)

    if cal_type == 4:
        pairs = meas_parameters["pairs"]
        fctrl = fsynth.DC590B()

        with Dc1513bAa(spi_registers, verbose) as controller:
            pbar = tqdm(range(1,ite+1), leave= True)
            for j in pbar:
                pbar.set_description("Iteration: %i" % j)
                ite_start = timer()
                for (TX, RX) in tqdm(pairs, leave= False):
                    swm.set_pair(TX, RX)
                    pbar2 = tqdm(range(0,len(freq_range)) , leave= False)
                    for i in pbar2:
                        f_cur = freq_range[i]
                        fctrl.freq_set(freq = f_cur, verbose=verbose)
                        pbar2.set_description("Cal Type 4: Tx - %i Rx - %i @ %s MHz" % (TX, RX, f_cur))
                        data_file= _generate_file_path2(meas_parameters = meas_parameters, antenna_pair = "Tx {0:d} Rx {1:d}".format(TX,RX))
                        if not os.path.exists(os.path.dirname(data_file.replace("ITE",str(j)))):
                            os.makedirs(os.path.dirname(data_file.replace("ITE",str(j))))
                        ch0,ch1 = controller.collect(num_samples, consts.TRIGGER_NONE)
                        if do_plot:
                            tqdm.write("\rPlotting calibration for room noise with input frequency: {} MHz".format(f_cur), end="")
                            rfft.plot_channels(controller.get_num_bits(), window,
                                                ch0, ch1,
                                                verbose=verbose)
                        rfft.save_for_pscope(data_file.replace("ITE",str(j)).replace(".adc"," LO FREQMHz Tx {0:d} Rx {1:d}.adc".format(TX,RX).replace("FREQ",f_cur)),
                                            controller.num_bits, controller.is_bipolar, num_samples, 'DC_1513B-AA', 'LTM9004', ch0, ch1)
                        if do_FFT:
                            rfft.save_for_pscope_fft(data_file.replace(".adc",".fft").replace("ITE",str(j)).replace(".fft"," LO FREQMHz Tx {0:d} Rx {1:d}.fft".format(TX,RX).replace("FREQ",f_cur)),
                                                    controller.num_bits, controller.is_bipolar, num_samples, 'DC_1513B-AA', 'LTM9004', window, ch0, ch1)

                if save_json and j != ite:
                    ite_end = timer()
                    meas_parameters["iter_duration"] = ite_end - ite_start
                    meas_parameters["obs"] = "Type 4: scan of room noise, without Tx active on phantom hemisphere."
                    _save_json_cal(meas_parameters = meas_parameters, cal_type = cal_type, iteration = j)

    end = timer()
    meas_parameters["cal_duration"] = end - start

    if save_json:
        meas_parameters["end"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _save_json_cal(meas_parameters = meas_parameters, cal_type = cal_type)

def _generate_file_path(meas_parameters):
    """Alter the dictionary value for the key "data_file" with current values for date, phantom, angle, plug and rep.

    Parameters
    ----------
    meas_parameters : dict
        dictionary with "measurement configuration parameters"
    """
    #fft_file = meas_parameters["fft_file"]

    date = meas_parameters["date"]
    phantom = meas_parameters["Phantom"]
    angle = meas_parameters["Angle"]
    plug = meas_parameters["Plug"]
    repetition = meas_parameters["rep"]


    meas_parameters["data_file"] = meas_parameters["data_file"].replace("DATE", date).replace("PHA",str(phantom)).replace("ANG",str(angle)).replace("PLU",str(plug)).replace("REP",str(repetition))

def _generate_file_path2(meas_parameters, antenna_pair = "Tx 15 Rx 16", file_path_key = "data_file"):
    """Output the data_file full path with the current antenna pair values.

    Parameters
    ----------
    meas_parameters : dict
        dictionary with "measurement configuration parameters"
    antenna_pair : str, optional
        string in the format: "Tx # Rx #", by default "Tx 15 Rx 16"
    file_path_key: str, optional
        string with file path, by default "data_file"

    Returns
    ----------
    str
        data_file path with placeholders "ANTPAIR" replaced with current values
    """

    data_file = copy.copy(meas_parameters[file_path_key])


    data_file = data_file.replace("ANTPAIR",str(antenna_pair))

    return data_file

def _generate_cal_file_path(meas_parameters, cal_type = 1):
    """Alter and output the dictionary value for the key "cal_data_file" with current values for date and calibration type.

    Parameters
    ----------
    meas_parameters : dict
        dictionary with "measurement configuration parameters"
    cal_type : int, optional
        number describing the calibration type, by default 1. Possible types:
        :1: LO and RF grounded with a 50 ohm terminator
        :2: RF grounded with a 50 ohm terminator, LO active with frequencies set by freq_range
        :3: RF receives Tx and Rx connected directly (without antennas), using frequencies set by freq_range

    Returns
    ----------
    str
        cal_data_file path with placeholders "DATE", "REP" and "TYPE" replaced with current values
    """

    date = meas_parameters["date"]

    repetition = meas_parameters["rep"]


    meas_parameters["cal_data_file"] = meas_parameters["cal_data_file"].replace("DATE", date).replace("REP",str(repetition)).replace("TYPE",str(cal_type))

    return meas_parameters["cal_data_file"]

def _save_json_exp(meas_parameters, config_folder = "Config/", iteration = None):
    """Save "measurement configuration parameters" dictionary to JSON file.

    Parameters
    ----------
    meas_parameters : dict
        dictionary with "measurement configuration parameters"
    config_folder: str, optional
        sub-folder to place the JSON configuration file, by default "Config/"
    iteration: int or None, optional
        current iteration value, by default None
        when None, receives meas_parameter["iter"]
    """

    if iteration is None:
        iteration = meas_parameters["iter"]
        original_it = None
    else:
        original_it = meas_parameters["iter"]
        meas_parameters["iter"] = iteration

    out_path = meas_parameters["data_file"].partition("Phantom ")[0] + config_folder
    file_name = os.path.basename(meas_parameters["data_file"]).replace("ANTPAIR FREQMHz","").replace("ITE", str(iteration)).replace(".adc",".json")

    #file_name = meas_parameters["file_name"].replace(".adc",".json")

    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    with open(out_path + file_name, 'w') as fp:
        json.dump(meas_parameters, fp, sort_keys=True, indent=4)
    print "\r Saved JSON file for: ", file_name
    if original_it is not None:
        meas_parameters["iter"] = original_it

def _save_json_cal(meas_parameters, cal_type = 1, config_folder = "Config/", iteration = None):
    """Save calibration "measurement configuration parameters" dictionary to JSON file.

    Parameters
    ----------
    meas_parameters : dict
        dictionary with "measurement configuration parameters"
    cal_type : int, optional
        number describing the calibration type, by default 1. Possible types:
        :1: LO and RF grounded with a 50 ohm terminator
        :2: RF grounded with a 50 ohm terminator, LO active with frequencies set by freq_range
        :3: RF receives Tx and Rx connected directly (without antennas), using frequencies set by freq_range
    config_folder: str, optional
        sub-folder to place the JSON configuration file, by default "Config/"
    iteration: int or None, optional
        current iteration value, by default None
        when None, receives meas_parameter["iter"]
    """

    if iteration is None:
        iteration = meas_parameters["iter"]
        original_it = None
    else:
        original_it = meas_parameters["iter"]
        meas_parameters["iter"] = iteration

    out_path = meas_parameters["cal_data_file"].partition("Calibration")[0] + config_folder
    file_name = os.path.basename(meas_parameters["cal_data_file"]).replace("ITE",str(iteration)).replace(".adc"," Type {}.json".format(cal_type))

    meas_parameters["cal_type"] = cal_type

    #file_name = meas_parameters["file_name"].replace(".adc",".json")

    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    with open(out_path + file_name, 'w') as fp:
        json.dump(meas_parameters, fp, sort_keys=True, indent=4)
    print "\r Saved JSON file for: ", file_name
    if original_it is not None:
        meas_parameters["iter"] = original_it

    del  meas_parameters["cal_type"]


if __name__ == '__main__':

    now = datetime.now()

    #PAIRS = [(TX, RX) for RX in range(1,17) for TX in range(1,17) if TX != RX]
    #PAIRS = [(TX, RX) for RX in range(1,17) for TX in range(1,17) if TX != RX and TX != 13 and RX != 13]
    #PAIRS = [(1,2), (2,3), (3,5), (4,5), (5,6), (6,7), (7,8),
    #            (1,8), (1,9), (1,16), (2,10), (2,11), (3,11), (3,12), (4,9), (4,10), (4,11), (4,12), (4,14), (5,12),
    #            (6,14), (6,15), (7,15), (7,16), (8,15), (8,16), (9,10), (9,14), (9,15), (9,16), (10,11), (10,12), (10,14),
    #            (11,12), (14,15), (14,16), (15,16)
    #            ]

    pairs = [(1,2), (2,3), (3,5), (5,6), (7,8), (9,10), (10,11), (11,12), (14,15), (15,16),
			(1,6), (2,5), (4,10), (4,12), (4,14), (7,8), (9,14), (9,16)
            ]
    pairs_rev = [tuple(reversed(t)) for t in pairs]
    extra_pairs = [(3, 13), (5,13)]

    pairs.extend(pairs_rev)
    pairs.extend(extra_pairs)

    # MeasParameters should be reset every loop of rep (repetition), except for new iterations!

    MeasParameters ={
                    "num_samples" : 1024,
                    "spi_registers" : [],
                    "verbose" : False, # DC590B controller board verbosity

                    "samp_rate" : 125*1e6,
                    "fft_window" : "hann",

                    "data_file" : "{}/Documents/Documents McGill/Data/PScope/DATE/Phantom PHA/ANG deg/Plug PLU/Rep REP/Iter ITE/Phantom PHA Plug PLU ANG deg FREQMHz ANTPAIR Rep REP Iter ITE.adc".format(os.environ['USERPROFILE']),
                    "fft_file" : "{}/Documents/Documents McGill/Data/PScope/DATE/Phantom PHA/ANG deg/Plug PLU/Rep REP/Iter ITE/Phantom PHA Plug PLU ANG deg FREQMHz ANTPAIR Rep REP Iter ITE.fft".format(os.environ['USERPROFILE']),

                    "cal_data_file" : "{}/Documents/Documents McGill/Data/PScope/DATE/Calibration/Type TYPE/Rep REP/Iter ITE/Calibration Iter ITE.adc".format(os.environ['USERPROFILE']),
                    "cal_fft_file" : "{}/Documents/Documents McGill/Data/PScope/DATE/Calibration/Type TYPE/Rep REP/Iter ITE/Calibration Iter ITE.fft".format(os.environ['USERPROFILE']),

                    "folder_path" : None,
                    "file_name" : None,
                    "fft_file_name" : None,


                    "date" : now.strftime("%Y_%m_%d"),

                    "Phantom" : 1,
                    "Angle" : 0,
                    "Plug" : 2,

                    "rep" : 1,
                    "iter" : 1,

                    "freq_range" : ("2000",
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
                                    "2200"),

                    "pairs" : pairs,

                    "attLO" : 20,
                    "attRF" : 9,

                    "obs" : "",

                    "system" : "narrow band",
                    "type" : "measurement configuration parameters"
                    }

    #ant_sweep(meas_parameters = MeasParameters, do_plot = False, do_FFT = False, save_json = True, display = False)
    cal_system(meas_parameters = MeasParameters, cal_type  = 1, do_plot = False, do_FFT = False, save_json = True)