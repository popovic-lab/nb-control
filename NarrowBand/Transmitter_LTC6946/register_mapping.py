# -*- coding: utf-8 -*-
# Python 2.7
# 2020-09-04
"""
Description:
    Module for register settings on the LTC6946-2 PLL Frequency Synthesizer for the narrowband system.

Functions::

    register_values :       return string for burst SPI write of register settings for a given frequency.
    register_values_list:   return list of strings for register settings for a given frequency.


Written by Leonardo Fortaleza
"""

reg_lists = {   "1550":  ['04','08','00','19','24','54','63','FB','DB','C0'],
                "1600":  ['04','08','00','19','25','80','63','FB','DB','C0'],
                "1650":  ['04','08','00','19','19','C8','63','FA','DB','C0'],
                "1700":  ['04','08','00','19','1A','90','63','FA','DB','C0'],
                "1750":  ['04','08','00','19','1B','58','63','FA','DB','C0'],
                "1800":  ['04','08','00','19','1C','20','63','FA','DB','C0'],
                "1850":  ['04','08','00','19','1C','E8','63','FA','DB','C0'],
                "1900":  ['04','08','00','19','1D','B0','63','FA','DB','C0'],
                "1950":  ['04','08','00','19','1E','78','63','FA','DB','C0'],
                "2000":  ['04','08','00','19','1F','40','63','FA','DB','C0'],
                "2012_5":['04','08','00','19','1F','72','63','FA','DB','C0'],
                "2025":  ['04','08','00','19','1F','A4','63','FA','DB','C0'],
                "2037_5":['04','08','00','19','1F','D6','63','FA','DB','C0'],
                "2050":  ['04','08','00','19','20','08','63','FA','DB','C0'],
                "2062_5":['04','08','00','19','20','3A','63','FA','DB','C0'],
                "2075":  ['04','08','00','19','20','6C','63','FA','DB','C0'],
                "2087_5":['04','08','00','19','20','9E','63','FA','DB','C0'],
                "2100":  ['04','08','00','19','20','D0','63','FA','DB','C0'],
                "2112_5":['04','08','00','19','21','02','63','FA','DB','C0'],
                "2125":  ['04','08','00','19','21','34','63','FA','DB','C0'],
                "2137_5":['04','08','00','19','21','66','63','FA','DB','C0'],
                "2150":  ['04','08','00','19','21','98','63','FA','DB','C0'],
                "2162_5":['04','08','00','19','21','CA','63','FA','DB','C0'],
                "2175":  ['04','08','00','19','21','FC','63','FA','DB','C0'],
                "2187_5":['04','08','00','19','22','2E','63','FA','DB','C0'],
                "2200":  ['04','08','00','19','22','60','63','FA','DB','C0'],
                "2250":  ['04','08','00','19','23','28','63','FA','DB','C0'],
                "2300":  ['04','08','00','19','23','F0','63','FA','DB','C0'],
                "2350":  ['04','08','00','19','24','B8','63','FA','DB','C0'],
                "2400":  ['04','08','00','19','25','80','63','FA','DB','C0'],
                "2450":  ['04','08','00','19','26','48','63','FA','DB','C0'],
                "3100":  ['04','08','00','19','18','38','63','F9','DB','C0'],
                "3150":  ['04','08','00','19','18','9C','63','F9','DB','C0'],
                "3200":  ['04','08','00','19','19','00','63','F9','DB','C0'],
                "0":     ['04','0A','00','19','22','60','63','FA','DB','C0']}

regs = {  "1550":  'xS02S04S0AS00S19S24S54S63SFBSDBSC0XxS04S08X',
          "1600":  'xS02S04S0AS00S19S25S80S63SFBSDBSC0XxS04S08X',
          "1650":  'xS02S04S0AS00S19S19SC8S63SFASDBSC0XxS04S08X',
          "1700":  'xS02S04S0AS00S19S1AS90S63SFASDBSC0XxS04S08X',
          "1750":  'xS02S04S0AS00S19S1BS58S63SFASDBSC0XxS04S08X',
          "1800":  'xS02S04S0AS00S19S1CS20S63SFASDBSC0XxS04S08X',
          "1850":  'xS02S04S0AS00S19S1CSE8S63SFASDBSC0XxS04S08X',
          "1900":  'xS02S04S0AS00S19S1DSB0S63SFASDBSC0XxS04S08X',
          "1950":  'xS02S04S0AS00S19S1ES78S63SFASDBSC0XxS04S08X',
          "2000":  'xS02S04S0AS00S19S1FS40S63SFASDBSC0XxS04S08X',
          "2012_5":'xS02S04S0AS00S19S1FS72S63SFASDBSC0XxS04S08X',
          "2025":  'xS02S04S0AS00S19S1FSA4S63SFASDBSC0XxS04S08X',
          "2037_5":'xS02S04S0AS00S19S1FSD6S63SFASDBSC0XxS04S08X',
          "2050":  'xS02S04S0AS00S19S20S08S63SFASDBSC0XxS04S08X',
          "2062_5":'xS02S04S0AS00S19S20S3AS63SFASDBSC0XxS04S08X',
          "2075":  'xS02S04S0AS00S19S20S6CS63SFASDBSC0XxS04S08X',
          "2087_5":'xS02S04S0AS00S19S20S9ES63SFASDBSC0XxS04S08X',
          "2100":  'xS02S04S0AS00S19S20SD0S63SFASDBSC0XxS04S08X',
          "2112_5":'xS02S04S0AS00S19S21S02S63SFASDBSC0XxS04S08X',
          "2125":  'xS02S04S0AS00S19S21S34S63SFASDBSC0XxS04S08X',
          "2137_5":'xS02S04S0AS00S19S21S66S63SFASDBSC0XxS04S08X',
          "2150":  'xS02S04S0AS00S19S21S98S63SFASDBSC0XxS04S08X',
          "2162_5":'xS02S04S0AS00S19S21SCAS63SFASDBSC0XxS04S08X',
          "2175":  'xS02S04S0AS00S19S21SFCS63SFASDBSC0XxS04S08X',
          "2187_5":'xS02S04S0AS00S19S22S2ES63SFASDBSC0XxS04S08X',
          "2200":  'xS02S04S0AS00S19S22S60S63SFASDBSC0XxS04S08X',
          "2250":  'xS02S04S0AS00S19S23S28S63SFASDBSC0XxS04S08X',
          "2300":  'xS02S04S0AS00S19S23SF0S63SFASDBSC0XxS04S08X',
          "2350":  'xS02S04S0AS00S19S24SB8S63SFASDBSC0XxS04S08X',
          "2400":  'xS02S04S0AS00S19S25S80S63SFASDBSC0XxS04S08X',
          "2450":  'xS02S04S0AS00S19S26S48S63SFASDBSC0XxS04S08X',
          "3100":  'xS02S04S0AS00S19S18S38S63SF9SDBSC0XxS04S08X',
          "3150":  'xS02S04S0AS00S19S18S9CS63SF9SDBSC0XxS04S08X',
          "3200":  'xS02S04S0AS00S19S19S00S63SF9SDBSC0XxS04S08X',
          "0":     'xS02S04S0AS00S19S22S60S63SFASDBSC0X'}

def register_values(freq):
    """Return string with register settings in SPI burst format for a given frequency.

    Function calls dictionary regs with frequency string as key.

    Parameters
    ----------
    freq : str
        string containing the input frequency in MHz, with underscores "_" replacing dots "."

    Returns
    -------
    list of str
        string with register values in SPI format for given frequency, ready for SPI write operation.
        if frequency not in dictionary (KeyError), prints "Not a valid frequency!".
    """
    try :
        return regs[freq]
    except KeyError:
        try :
            return regs[_freq2str(freq)]
        except KeyError:
            print "Not a valid frequency!"

def register_values_list(freq):
    """Return list of strings with register settings for a given frequency.

    Function calls dictionary reg_lists with frequency string as key.

    Parameters
    ----------
    freq : str
        string containing the input frequency in MHz, with underscores "_" replacing dots "."

    Returns
    -------
    list of str
        list with register values for given frequency, for register addresses from h01 to h0A.
        if frequency not in dictionary (KeyError), prints "Not a valid frequency!".
    """
    try :
        return reg_lists[freq]
    except KeyError:
        try :
            return regs[_freq2str(freq)]
        except KeyError:
            print "Not a valid frequency!"

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

if __name__ == '__main__':

    ans = register_values('0')
    print(ans)