import serial
import serial.tools.list_ports

__initialized = False
__sw_com = None
__set_SMC_command_str = "SMC_SET_TX%02d_RX%02d"
__set_HEF_command_str = "HEF_SET_TX%02d_RX%02d"

__led_colors = ['red','blue','green','orange', 'all']
__toggle_led_command = "toggle_%s_led"

def locate_switching_matrix():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        #if 'STMicroelectronics' or 'STMicroelectronics.' in p.manufacturer:
        #    #return p.device
        #    return p
        if p.description.startswith("STMicroelectronics Virtual"):
            return p
    return None



def init():
    global __sw_com, __initialized
    port = locate_switching_matrix()
    #print port.description
    port =port.device
    if port:
        __sw_com = serial.Serial(port)
    else:
        raise(Exception("Switching Matrix not found"))
    __initialized = True


def set_pair(TX, RX):
    if not __initialized:
        init()
    command = __set_SMC_command_str % (TX, RX)
    __sw_com.write(command)


def toggle_led(color='red'):
    if not __initialized:
        init()

    if color not in __led_colors:
        return

    if color == 'all':
        for c in __led_colors[0:4]:
            __sw_com.write(__toggle_led_command % c)
    else:
        __sw_com.write(__toggle_led_command % color)

