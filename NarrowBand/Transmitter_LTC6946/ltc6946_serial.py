# Python 2.7
# 2020-09-04

# Version 1.0.0

# Leonardo Fortaleza (leonardo.fortaleza@mail.mcgill.ca)

"""
Written by: Leonardo Fortaleza

 Description:
		Module for serial (SPI) communication with the LTC9646 PLL Frequency Synthesizer
        through the DC590B demo control board.

        Main usage:

        $ fsynth = DC590B()           # Finds and opens DC590B COM port.
        $ fsynth.freq_set("2012_5")   # Sets known frequency (input is string for compatibility with previous modules).

    Class::
        DC590B: defined for communication with the DC590B demo board, containing several routines.

    Class object implementation adapted from connect_to_arduino_DC590.py module
    by Noe Quintero (Linear Technology). Disclaimer follows:

    Created by: Noe Quintero
    E-mail: nquintero@linear.com
    REVISION HISTORY
    $Revision: $
    $Date: $

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
"""

# Standard library imports
import time

# Third-party library imports
import serial
import serial.tools.list_ports

# Local application imports
from register_mapping import register_values, register_values_list

def scan():
    """Scan for available ports. Return a list of tuples (num, name)."""
    available = []
    for i in range(256):
        try:
            s = serial.Serial("COM"+ str(i))
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

class DC590B(object, verbose=False):
    """Hardware-based SPI implementation for the DC590B demo board controller with
    select frequency setting routine for the LTC6946.

    """

    def __init__(self, verbose=verbose):
        self.open(verbose)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.close()

    def open(self, verbose=verbose):
        """Locates and opens DC590 COM port.
        """
        if verbose:
            print "\nLooking for COM ports ..."
        ports = scan()
        number_of_ports = len(ports)
        if verbose:
            print "Available ports: " + str(ports)
            print "\nLooking for DC590B ..."
        for x in range(0,number_of_ports):
            # Opens the port
            self.port = serial.Serial(ports[x][1], 9600, timeout = 0.5, write_timeout = 0.5)
            try:
                id_dc590 = self.port.read(50) # Remove the hello from buffer

                # Get ID string
                self.port.write("i")
                id_dc590 = self.port.read(50)
                if id_dc590[20:25] == "DC590":
                    #DC590B = ports[x][1]
                    #print ports[x][1]
                    if verbose:
                        print "    Found DC590B!!!!"
                        self.port.write('MS') # Sets SPI mode instead of I2C
                    return self
            except:
                pass
            self.port.close()

        print "    DC590B was not detected."
        return 0

    def close(self):
        """Close serial port, return 1 if successful and 0 otherwise.
        """
        try:
            self.port.close()  # Close serial port
            return 1
        except Exception:
            return 0

    def info(self):
        """Read and print target board info.
        """
        self.port.write('I')
        info = self.port.read((16*2 + 4)*2)
        print info

    def ctrl_info(self):
        """Read and print control board info.
        """
        self.port.write('i')
        info = self.port.read((16*2 + 4)*2)
        print info

    def transfer_packets(self, send_packet, return_size = 0):
        """"Send packet and, if return_size > 0, return read packet.
        """
        try:
            if len(send_packet) > 0:
                self.port.write(send_packet)                       # Send packet
            if return_size > 0:
                return self.port.read((return_size*2 + 4)*2) # Receive packet
            else:
                return None # return_size of 0 implies send only
        except:
            return 0

    def check_PLL_lock(self):
        """Check if only PLL Lock flag is up in register h00, return boolean.

        Register h00 is read only and has a flag for PLL Lock at bit 2. (please refer to LTC6946 datasheet).

        Returns
        -------
        bool
            return True if only the PLL Lock flag is up in register h00, otherwise return False
        """
        ans = self.transfer_packets('xR01', return_size=1)
        self.port.write('X')
        if ans == '04':
            return True
        else:
            return False

    def check_regs(self, values=['04'].append(register_values_list('0')), all_regs=True,
                     addr_list = ['01','03','05','07','09','0B', '0D', '0F', '11', '13', '15']):
        """Check if register values match input 'values', return boolean.

        Can check all relevant registers (h00 to h0A) or else register addresses in addr_list.
        Note that the addresses are 7-bit hex values + LSB 1 for read operation (please refer to LTC6946 datasheet).

        Parameters
        ----------
        values : list of str, optional
            list with byte values in string format, by default ['04'].append(register_values_list('0'))
        all_regs : bool, optional
            set to True for burst SPI read of registers h00 to h0A, by default True
        addr_list : list of str, optional
            list of strings with register addresses in case all_regs = False, by default ['01','03','05','07','09','0B', '0D', '0F', '11', '13', '15']
            note that addresses are composed of 7-bit hex number + LSB 1 for read operation
        Returns
        -------
        bool
            return True if register values match input values list, otherwise return False
        """
        if all_regs: # reads 11 registers, excludes only h0B which only contains Revision and part numbers.
            ans = self.transfer_packets('xR01', return_size=11)
            self.port.write('X')
        else:
            ans = []
            for addr in addr_list:
                ans.append(self.transfer_packets("".join(('xR',addr)), return_size=1))
                self.port.write('X')
            ans = ''.join((ans))
        values = ''.join(values)
        if values == ans:
            return True
        else:
            return False

    def freq_set_from_list(self, freq, verbose=False,
                            addr_list = ['02','04','06','08','0A', '0C', '0E', '10', '12', '14'],
                            check_lock=False, check_values=False,
                            chk_addr_list= ['01','03','05','07','09','0B', '0D', '0F', '11', '13', '15']):
        """Set LTC6946 registers individually for input freq.

        Each register is set a time using SPI communication.
        Register values are provided in the register_mappings module by the reg_lists dictionary.

        Addresses are 7-bit ['01','02','03','04','05','06','07','08','09','0A'] + LSB 0 for write operation,
        so default addr_list = ['02','04','06','08','0A', '0C', '0E', '10', '12', '14'].

        For read operaiton, LSB 1,
        so default chk_addr_list = ['01','03','05','07','09','0B', '0D', '0F', '11', '13', '15'].

        Parameters
        ----------
        freq : str
            string containing the input frequency in MHz, with underscores "_" replacing dots "."
        verbose : bool, optional
            set True for verbosity, by default False
        addr_list : list of str, optional
            list of register addresses for writing, by default ['02','04','06','08','0A', '0C', '0E', '10', '12', '14']
        check_lock : bool, optional
            set to True to perform PLL Lock flag verification, by default False
        check_values : bool, optional
            set to True to perform full register values verification, by default False
            uses register_values_list(freq) to check values
        chk_addr_list : list of str, optional
            list of register addresses for reading if check_values=True,
            by default ['01','03','05','07','09','0B', '0D', '0F', '11', '13', '15']

        Returns
        -------
        int
            If either check_lock or check_values are True, returns 1 if check succesfull and 0 otherwise.
        """
        msg = register_values_list(freq)

        if verbose:
            print "\rSetting frequency: {} MHz                         ".format(freq),

        for index in range(0,len(msg)):                      #Send bytes in msg list
            if index == 1:
                self.port.write("xS04S0AX") # Initially keep RFOUT muted.
            else:
                self.port.write("xS" + addr_list[index] + "S" + msg[index] + "X")
        self.port.write("xS" + addr_list[1] + "S" + msg[1] + "X")
        if verbose:
            print "\rFrequency Set: {} MHz                         ".format(freq)

        if check_values:
            ans = self.check_regs(values=['04'].append(register_values_list(freq)), all_regs=True,
                                    addr_list=chk_addr_list)
            if ans:
                if verbose:
                    print "\nRegisters match!\n"
                return 1
            else:
                if verbose:
                    print "\nRegisters don't match!\n"
                return 0
        elif check_lock:
            ans = self.check_PLL_lock()
            if ans:
                if verbose:
                    print "\nPLL Locked Succesfully!\n"
                return 1
            else:
                if verbose:
                    print "\nPLL Not Locked!\n"
                return 0

    def freq_set(self, freq, verbose=False, check_lock=False, check_values=False):
        """Set LTC6946 registers for input freq, using burst SPI mode.

        This is more efficient than setting each register at a time (freq_set_from_list function).
        SPI message with register values are provided in the register_mappings module by the regs dictionary.

        Parameters
        ----------
        freq : str
            string containing the input frequency in MHz, with underscores "_" replacing dots "."
        verbose : bool, optional
            set True for verbosity, by default False
        check_lock : bool, optional
            set to True to perform PLL Lock flag verification, by default False
        check_values : bool, optional
            set to True to perform full register values verification, by default False
            uses register_values_list(freq) to check values

        Returns
        -------
        int
            If either check_lock or check_values are True, returns 1 if check succesfull and 0 otherwise.
        """
        msg = register_values(freq)

        if verbose:
            print "\rSetting frequency: {} MHz                         ".format(freq),

        self.port.write(msg)

        if verbose:
            print "\rFrequency Set: {} MHz                         ".format(freq)

        if check_values:
            ans = self.check_regs(values=['04'].append(register_values_list(freq)), all_regs=True)
            if ans:
                if verbose:
                    print "\nRegisters match!\n"
                return 1
            else:
                if verbose:
                    print "\nRegisters don't match!\n"
                return 0
        elif check_lock:
            ans = self.check_PLL_lock()
            if ans:
                if verbose:
                    print "\nPLL Locked Succesfully!\n"
                return 1
            else:
                if verbose:
                    print "\nPLL Not Locked!\n"
                return 0
                


if __name__ == '__main__':

    #fsynth = DC590B()
    #fsynth.ctrl_info()
    #fsynth.freq_set("0")

    #fsynth.port.write('xS02S02X')
    #time.sleep(0.1)
    #fsynth.port.write('xS04S08X')
    #fsynth.port.write('xR01')
    #ans = fsynth.port.read(32)
    #print ans

    # Routine to validate frequency settings:

    freq_cal = ("2000",
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
                "2200",
                "0")

    fsynth = DC590B()

    for freq in freq_cal:
        fsynth.freq_set(freq, verbose=True, check_lock=False, check_values=True)
