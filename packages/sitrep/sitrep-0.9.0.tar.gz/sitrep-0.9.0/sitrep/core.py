'''A console-based short and sweet snapshot of system resources'''


### MODULES ###

# Standard
from datetime import timedelta
from socket import gethostname
import argparse
import glob
import os
import re

# Third-party
import netifaces
import psutil
import requests


### COMMAND-LINE OPTIONS ###

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", 
                    action="store_true")
args = parser.parse_args()


### CONSTANTS ###

NA = 'n/a'
NF = 'not found'
VERBOSE = "['--verbose' to display]"

# Color codes
CS = '\033[01;34m'  # foreground blue                                                          
SC = '\033[00m'     # reset

# Add x spaces:
SP = 2


### MAIN ###

def main():
    sitrep_system()
    sitrep_power()
    sitrep_network()
    sitrep_sensors()


### SYSTEM ###

def system_uptime():
    '''Return system uptime in human-readable form'''
    p = '/proc/uptime'
    if os.path.exists(p):
        with open(p, 'r') as f:
            x = int(float(f.readline().split()[0]))
            uptime_string = str(timedelta(seconds = x))
        return uptime_string
    else:
        return NF

def pid_count():
    '''Return a total count of running processes'''
    process_count = len(psutil.get_pid_list())
    return str(process_count)

def memory_total_mb():
    '''Return total system memory in MB'''
    MB = 1048576 # bytes
    mem_total = (psutil.virtual_memory().total / MB)
    return mem_total

def memory_used_mb():
    '''Return current memory usage in MB'''
    MB = 1048576 # bytes
    mem_total = psutil.virtual_memory().total
    mem_avail = psutil.virtual_memory().available
    mem_used = ((mem_total - mem_avail) / MB)
    return mem_used

def load_average():
    '''Return system load averages over 1, 5, 15 minutes'''
    av0, av1, av2 = os.getloadavg()
    load_average_string = ('%.2f, %.2f, %.2f' % (av0, av1, av2))
    return load_average_string
            
def sitrep_system():
    '''Display hostname, uptime, process count, memory, and load'''
    system = (CS + 'System: ' + SC)
    host = (CS + 'Host: ' + SC + gethostname())
    uptime = (CS + 'Uptime: ' + SC + system_uptime())
    process = (CS + 'Processes: ' + SC + pid_count())
    memory = (CS + 'Memory Used/Total: ' + SC + str(memory_used_mb()) 
              + '/' + str(memory_total_mb()) + 'MB')
    load = (CS + 'Load: ' + SC + load_average())
    print(system + ' ' * SP + host + ' ' * SP + uptime)
    print(' ' * 10 + memory + ' ' * SP + process + ' ' * SP + load)


### POWER ###

def battery_status():
    '''Return battery status (Charging, Discharging, Full) 
    if available.
    '''
    p = '/sys/class/power_supply/BAT0/status'
    if os.path.exists(p):
        with open(p, 'r') as f:
            bat_stat = f.readline().split()[0]
        return bat_stat
    else:
        return NF

def adapter_status():
    '''Return AC power adapter status (online, offline)'''
    p = '/sys/class/power_supply/AC/online'
    if os.path.exists(p):
        with open(p, 'r') as f:
            line_stat = int(f.readline())
            line_string = ''
            if line_stat > 0:
                line_string = 'online'
            else:
                line_string = 'off-line'
        return line_string
    else:
        return NF

def battery_capacity():
    '''Return current battery capacity (as percent of total capacity)'''
    p = '/sys/class/power_supply/BAT0/capacity'
    if os.path.exists(p):
        with open(p, 'r') as f:
            bat_cap = int(f.readline().split()[0])
        return bat_cap
    else:
        return NF

def battery_charge_design():
    '''Return the battery capacity by design (measured in mAh)'''
    p = '/sys/class/power_supply/BAT0/charge_full_design'
    if os.path.exists(p):
        with open(p, 'r') as f:
            mAh = 1000
            charge_design = (int(f.readline().split()[0]) / mAh)
        return charge_design
    else:
        return NF

def battery_charge_last():
    '''Return the battery capacity after last full charge 
    (measured in mAh)
    '''
    p = '/sys/class/power_supply/BAT0/charge_full'
    if os.path.exists(p):
        with open(p, 'r') as f:
            mAh = 1000
            charge_last = (int(f.readline().split()[0]) / mAh)
        return charge_last
    else:
        return NF

def battery_charge_last_percent():
    '''Return the battery capacity after last full charge
    (measured as percent of total design capacity)
    '''
    charge_last_percent = ((battery_charge_last() * 100) 
                            / battery_charge_design())
    return charge_last_percent

def battery_time_remaining():
    '''Return battery time remaining (measured in minutes)'''
    p0 = '/sys/class/power_supply/BAT0/charge_now'
    p1 = '/sys/class/power_supply/BAT0/current_now'
    if os.path.exists(p0) and os.path.exists(p1):
        with open(p0, 'r') as f:
            charge_now = float(f.readline().split()[0])
        with open(p1, 'r') as f:
            current_now = float(f.readline().split()[0])
        if current_now > 0:
            hour = 60 # minutes
            time_remaining = ((charge_now / current_now) * hour)
            return time_remaining
        else:
            return 0
    else:
        return NF

def sitrep_power():
    '''Display adapter and battery status, charge, and capacity'''
    power = (CS + 'Power: ' + SC)
    ac_stat = (CS + 'Adapter: ' + SC + adapter_status())
    p = '/sys/class/power_supply/BAT0'
    # Test if battery available
    if os.path.isdir(p):
        # Modify output colour based on percent time remaining
        if battery_status() == 'Discharging' \
                and battery_capacity() >= 60:
            CS1 = '\033[01;32m'
        elif battery_status() == 'Discharging' \
                and battery_capacity() >= 30:
            CS1 = '\033[01;33m'
        elif battery_status() == 'Discharging' \
                and battery_capacity() < 30:
            CS1 = '\033[01;31m'
        else:
            CS1 = ''
        # Battery variables
        bat_stat = (CS + 'Battery: ' + SC + CS1 + battery_status() 
                    + SC)
        bat_cap = (CS1 + str(battery_capacity()) + '%' + SC)
        bat_time = (CS1 + str(int(battery_time_remaining())) 
                    + 'min remaining' + SC)
        bat_charge = (CS + 'Battery Capacity: ' + SC)
        bat_charge_design = (CS + 'by design: ' + SC 
                             + str(battery_charge_design()) + 'mAh')
        bat_charge_last = (CS + 'last charge: ' 
                           + SC + str(battery_charge_last()) + 'mAh')
        bat_charge_last_percent = (str(battery_charge_last_percent()) 
                                   + '%')
        if battery_status() == 'Discharging':
            bat_power = (bat_stat + ', ' + bat_cap + ', ' + bat_time)
        else:
            bat_power = (bat_stat + ', ' + bat_cap)
        print(power + ' ' * 3 + bat_power + ' ' * SP + ac_stat)
        print(' ' * 10 + bat_charge + bat_charge_design + ' ' * SP 
          + bat_charge_last + ' = ' + bat_charge_last_percent)
    else:
        print(power + ' ' * 3 + ac_stat)


### NETWORK ###

def exclude_interface(*interface):
    '''Exclude interface(s) from network device list'''
    interface_list = netifaces.interfaces()
    for a in interface:
        if a in interface_list:
            interface_list.remove(a)
    return interface_list

def interface_state(interface):
    '''Return state(up|down) of network interface'''
    state_0 = 'down'
    state_1 = 'up'
    ip_addr = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in ip_addr:
        return state_1
    else:
        return state_0

def interface_address(interface):
    '''Return IP address of a network interface'''
    interface_list = netifaces.interfaces()
    key = 'addr'
    if interface in interface_list:
        addr_dict = netifaces.ifaddresses(interface)
        ip_addr = addr_dict.get(netifaces.AF_INET, NA)
        if ip_addr == NA:
            return ip_addr
        else:
            return ip_addr[0][key]
    else:
        return NF

def wan_address():                                                                    
    '''Return WAN IP address'''                                                
    # Requests HTTP library:                                                       
    # http://docs.python-requests.org/en/latest/                                   
    # Regular Expression HOWTO:                                                    
    # http://docs.python.org/2/howto/regex.html                                    
    # List of HTTP status codes
    # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    url = "http://checkip.dyndns.org"                                              
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        wan_ip = re.search('\d+\.\d+\.\d+\.\d+', response.text)
        return wan_ip.group()
    else:
        return NF

def display_wan_address():
    # Return WAN IP address if '--verbose' option specified
    if args.verbose:
        return wan_address()
    else:
        return VERBOSE
                                                                                   
def net_traffic(interface):                                                  
    '''Return receive/transmit traffic measured in MB on an interface'''           
    MB = 1048576 # bytes
    p = '/proc/net/dev'
    if os.path.exists(p):
        with open(p, 'r') as f:                                          
            data = f.read().split('%s:' % interface)[1].split()                        
            rx = (float(data[0]) / MB)                                                   
            tx = (float(data[8]) / MB)
    else:
        rx = 0
        tx = 0
    return (rx, tx)

def str_interface_info(interface):
    # Build network info strings for sitrep_network to display
    print(' ' * 9),
    print(CS + 'IF: ' + SC + '%s' % interface),
    print(' ' + CS + 'state: ' + SC + interface_state(interface)),
    print(' ' + CS + 'ip: ' + SC + interface_address(interface)),
    print(' ' + CS + 'rx: ' + SC + '%.2fMB' 
          % net_traffic(interface)[0]),
    print(CS + 'tx: ' + SC + '%.2fMB' 
          % net_traffic(interface)[1])

def sitrep_network():                                                              
    '''Display details about network interface(s)'''
    print(CS + 'Network: ' 
          + ' ' + 'WAN: ' + 'ip: ' + SC + str(display_wan_address()))
    interface_list = exclude_interface('lo')
    for i in interface_list:
        str_interface_info(i)


### SENSORS ###

def temperature_cpu():
    '''Return CPU temperature (Celsius)'''
    p = '/sys/class/thermal/thermal_zone0/temp'
    if os.path.exists(p):
        with open(p, 'r') as f:
            temp_unit = 1000
            temp_cpu = (float(f.readline().split()[0]) / temp_unit)
        return temp_cpu
    else:
        return NF
    
def temperature_mobo():
    pass

def fan_speed_cpu():
    fs_info = glob.glob('/sys/class/hwmon/hwmon*/device/fan1_input')
    if len(fs_info) != 0:
        with open(fs_info[0], 'r') as f:
            fs_cpu = int(f.readline().split()[0])
        return fs_cpu
    else:
        return NF

def fan_speed_mobo():
    pass

def sitrep_sensors():
    '''Display details about system sensors'''
    sensors = (CS + 'Sensors: ' + SC)
    temp_system = (CS + 'System Temperatures: ' + SC)
    temp_cpu = (CS + 'cpu: ' 
                + SC + str('%.1f' % temperature_cpu()) + 'C')
    #temp_mobo = (CS + 'mobo: ' + SC + str(temperature_mobo()))
    fan_speed = (CS + 'Fan Speeds (in rpm): ' + SC)
    fan_cpu = (CS + 'cpu: ' + SC + str(fan_speed_cpu()))
    #fan_mobo = (CS + 'mobo: ' + SC + str(fan_speed_mobo()))
    print(sensors + ' ' + temp_system + temp_cpu)
    print(' ' * 10 + fan_speed + fan_cpu) 
        

### WE ARE GO ###

if __name__ == '__main__':
    main()

