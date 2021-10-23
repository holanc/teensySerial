
import serial
import time
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsgbox
import tkinter as tk
import serial.tools.list_ports
import configparser
from tkinter import filedialog
import csv


class ChannelSettings:
    def __init__(self, on_time, off_time, unit, pin, seed):
        self.on_time = on_time
        self.off_ime = off_time
        self.unit = unit
        self.pin = pin
        self.seed = seed


# combo_ktx1_unit = ttk.Combobox(frame_ktx1, values=('ms', 'us'), width=4)


# def create_combobox(frame, values, off_time, unit, pin, seed):
#     self.on_time = on_time
#     self.off_ime = off_time
#     self.unit = unit


# def open_csv(filename_tmp):
#     global csv_string
#     global csv_num
#     global file_name_csv
#     str_tmp = ""
#     config.set('general', 'file_path', filename_tmp)
#     with open("config.ini", "w+") as configfile:
#         config.write(configfile)
#     file_name_csv.set(filename_tmp)
#
#     file_csv = open(filename_tmp, "r")
#     csv_reader = csv.reader(file_csv)
#     array = []
#     for row in csv_reader:
#         for val_str in row:
#             array.append(val_str)
#     csv_num = 0
#     for num in array:
#         if csv_num:
#             str_tmp += '_' + num.strip()
#         else:
#             str_tmp += num.strip()
#         csv_num += 1
#     text_csv.config(state=tk.NORMAL)
#     text_csv.delete('1.0', tk.END)
#     text_csv.insert(tk.END, str_tmp)
#     text_csv.config(state=tk.DISABLED)
#     csv_string = str_tmp


# def browse_button():
#     filename_tmp = filedialog.askopenfilename()
#     if filename_tmp.endswith('.csv'):
#         open_csv(filename_tmp)
#         config.set('general', 'file_path', filename_tmp)
#         with open("config.ini", "w+") as configfile:
#             config.write(configfile)


def write_ser(data):
    global num_writes
    num_writes += 1
    ser.write(data.encode())
    time_string = time.strftime("%H:%M:%S", time.localtime())
    text_order.insert('1.0', time_string + data + '\n')
    # text_csv.config(state=tk.DISABLED)


def get_com_port_list():
    port_list = serial.tools.list_ports.comports()
    combo_port['values'] = port_list


def connect_com():
    try:
        if ser.is_open:
            ser.close()
        port_list = serial.tools.list_ports.comports()
        ser.port = port_list[combo_port.current()].device
        if ser.port != port:
            config.set('general', 'port', ser.port)
            with open("config.ini", "w+") as configfile:
                config.write(configfile)
        ser.baudrate = 115200
        ser.parity = serial.PARITY_NONE
        ser.bytesize = serial.EIGHTBITS
        ser.timeout = 0
        # for arduino nano every:
        # ser.dsrdtr = None
        ser.open()
        time.sleep(1.5)
        if ser.is_open:
            btn_start_trg['state'] = tk.NORMAL
            btn_pulse_trg['state'] = tk.NORMAL
            btn_start_ktx['state'] = tk.NORMAL
            btn_start_sig1['state'] = tk.NORMAL
            btn_start_sig2['state'] = tk.NORMAL
            btn_pulse_sig1['state'] = tk.NORMAL
            btn_pulse_sig2['state'] = tk.NORMAL
            btn_start_prod['state'] = tk.NORMAL
            btn_rack_start['state'] = tk.NORMAL
            btn_rack_recovery['state'] = tk.NORMAL
            btn_rack_reset['state'] = tk.NORMAL
            btn_rack_shutdown['state'] = tk.NORMAL
            btn_pulse_sig1['state'] = tk.NORMAL
            btn_pulse_sig2['state'] = tk.NORMAL
            btn_seq_sig2['state'] = tk.NORMAL
            btn_ran_sig2['state'] = tk.NORMAL
            text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + f' connected to {ser.port} ' + '\n')
    except (ValueError, serial.SerialException, IndexError):
        except_string = 'could not connect to port'
        # print(except_string)
        text_order.insert('1.0', except_string + '\n')


def check_connection():
    # global port
    master.after(2000, check_connection)
    if not ser.is_open:
        # err_out.insert(0, 'port closed')
        btn_start_trg['state'] = tk.DISABLED
        btn_pulse_trg['state'] = tk.DISABLED
        btn_start_ktx['state'] = tk.DISABLED
        btn_start_sig1['state'] = tk.DISABLED
        btn_start_sig2['state'] = tk.DISABLED
        btn_pulse_sig1['state'] = tk.DISABLED
        btn_pulse_sig2['state'] = tk.DISABLED
        btn_start_prod['state'] = tk.DISABLED
        btn_rack_start['state'] = tk.DISABLED
        btn_rack_recovery['state'] = tk.DISABLED
        btn_pulse_sig1['state'] = tk.DISABLED
        btn_pulse_sig2['state'] = tk.DISABLED
    # port_list = serial.tools.list_ports.comports()
    # print(port_list[combo_port.current()].device)
    # print(port)
    # if port != port_list[combo_port.current()].device:
    #     get_com_port_list()
    #     lst2 = serial.tools.list_ports.comports()
    #     try:
    #         for item2 in lst2:
    #             if item.device == port:
    #                 combo_port.insert(0, item)
    #                 break
    #         else:
    #             combo_port.insert(0, lst[0])
    #     except NameError:
    #         combo_port.insert(0, lst[0])
    #     port = port_list[combo_port.current()].device


def start_trg():
    on_time = entry_trg_on_time.get()
    off_time = entry_trg_off_time.get()
    unit = combo_trg_unit.current()
    pin = entry_trg_pin.get()
    data = f"{{SIG_{pin}_{on_time}_{off_time}_{unit}}}"
    write_ser(data)
    if off_time != '0':
        btn_stop_trg['state'] = tk.NORMAL
        btn_stop_prod['state'] = tk.NORMAL


def stop_trg():
    pin = entry_trg_pin.get()
    data = f"{{SIG_{pin}_0}}"
    write_ser(data)
    btn_stop_trg['state'] = tk.DISABLED
    btn_stop_prod['state'] = tk.DISABLED


def pulse_trg():
    on_time = entry_trg_on_time.get()
    pin = entry_trg_pin.get()
    data = f"{{SIG_{pin}_{on_time}_0_0}}"
    write_ser(data)
    btn_stop_trg['state'] = tk.DISABLED


def start_ktx():
    on_time = entry_ktx_on_time.get()
    off_time = entry_ktx_off_time.get()
    unit = combo_ktx_unit.current()
    pin = entry_ktx_pin.get()
    data = f"{{SIG_{pin}_{on_time}_{off_time}_{unit}}}"
    write_ser(data)
    if off_time != '0':
        btn_stop_ktx['state'] = tk.NORMAL
        btn_stop_prod['state'] = tk.NORMAL


def stop_ktx():
    pin = entry_ktx_pin.get()
    data = f"{{SIG_{pin}_0}}"
    write_ser(data)
    btn_stop_ktx['state'] = tk.DISABLED
    btn_stop_prod['state'] = tk.DISABLED


def start_sig1():
    on_time = entry_sig1_on_time.get()
    off_time = entry_sig1_off_time.get()
    unit = combo_sig1_unit.current()
    pin = entry_sig1_pin.get()
    data = f"{{SIG_{pin}_{on_time}_{off_time}_{unit}}}"
    write_ser(data)
    if off_time != '0':
        btn_stop_sig1['state'] = tk.NORMAL


def stop_sig1():
    pin = entry_sig1_pin.get()
    data = f"{{SIG_{pin}_0}}"
    write_ser(data)
    btn_stop_sig1['state'] = tk.DISABLED


def pulse_sig1():
    on_time = entry_sig1_on_time.get()
    pin = entry_sig1_pin.get()
    data = f"{{SIG_{pin}_{on_time}_0_0}}"
    write_ser(data)
    btn_stop_sig1['state'] = tk.DISABLED


def start_sig2():
    on_time = entry_sig2_on_time.get()
    off_time = entry_sig2_off_time.get()
    unit = combo_sig2_unit.current()
    pin = entry_trg_pin.get()
    data = f"{{SIG_{pin}_{on_time}_{off_time}_{unit}}}"
    write_ser(data)
    if off_time != '0':
        btn_stop_sig2['state'] = tk.NORMAL


def stop_sig2():
    pin = entry_sig2_pin.get()
    data = f"{{SIG_{pin}_0}}"
    write_ser(data)
    btn_stop_sig2['state'] = tk.DISABLED


def pulse_sig2():
    on_time = entry_sig2_on_time.get()
    pin = entry_sig2_pin.get()
    data = f"{{SIG_{pin}_{on_time}_0_0}}"
    write_ser(data)
    btn_stop_sig2['state'] = tk.DISABLED


def seq_sig2():
    on_time = entry_sig2_on_time.get()
    pin = entry_sig2_pin.get()
    data = f"{{SIG_{pin}_SEQ_{csv_num}_{on_time}_{csv_string}}}"
    write_ser(data)
    btn_stop_sig2['state'] = tk.NORMAL


def ran_sig2():
    on_time = entry_sig2_on_time.get()
    off_time = entry_sig2_off_time.get()
    seed = entry_sig2_seed.get()
    pin = entry_sig2_pin.get()
    data = f"{{SIG_{pin}_RAND_{on_time}_{off_time}_{seed}}}"
    write_ser(data)
    btn_stop_sig2['state'] = tk.NORMAL


def start_prod():
    start_ktx()
    start_trg()
    btn_stop_prod['state'] = tk.NORMAL


def stop_prod():
    stop_ktx()
    stop_trg()
    btn_stop_prod['state'] = tk.DISABLED


def close_dialog():
    res = tkmsgbox.askyesno('ArduinoController', 'Do you want to quit the program?')
    if res:
        if ser.is_open:
            ser.close()
        master.destroy()


def rack_start():
    pin = entry_start_pin.get()
    data = f"{{SIG_{pin}_{start.on_time}_0_0}}"
    write_ser(data)


def rack_recovery():
    pin = entry_start_pin.get()
    data = f"{{SIG_{pin}_{recovery.on_time}_0_0}}"
    write_ser(data)


def rack_reset():
    pin = entry_reset_pin.get()
    data = f"{{SIG_{pin}_{reset.on_time}_0_0}}"
    write_ser(data)


def rack_shutdown():
    pin = entry_reset_pin.get()
    data = f"{{SIG_{pin}_{shutdown.on_time}_0_0}}"
    write_ser(data)


master = tk.Tk()
file_name_csv = tk.StringVar()
csv_values = tk.StringVar()
csv_string = ""
csv_num = 0
num_writes = 0
general_bg = 'grey47'
widget_bg = 'grey20'
widget_fg = 'whitesmoke'

master.title("ArduinoController")
master.geometry("825x570+100+100")
frame_left = tk.Frame(master)
frame_right = tk.Frame(master)
frame_com = tk.Frame(frame_left)
frame_testrack1 = tk.Frame(frame_left)
frame_testrack2 = tk.Frame(frame_left)
frame_sreg = tk.Frame(frame_left)
frame_ktx1 = tk.Frame(frame_testrack1)
frame_trg1_1 = tk.Frame(frame_testrack1)
frame_trg1_2 = tk.Frame(frame_testrack1)
frame_ktx2 = tk.Frame(frame_testrack2)
frame_trg2_1 = tk.Frame(frame_testrack2)
frame_trg2_2 = tk.Frame(frame_testrack2)
frame_admin1 = tk.Frame(frame_testrack1)
frame_admin2 = tk.Frame(frame_testrack2)
frame_csv = tk.Frame(frame_left)

master.configure(background=general_bg)
frame_left.configure(background=general_bg)
frame_right.configure(background=general_bg, relief='ridge', borderwidth=2)
frame_com.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_testrack1.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_testrack2.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_sreg.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_ktx1.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_trg1_1.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_trg1_2.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_ktx2.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_trg2_1.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_trg2_2.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_admin1.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_admin2.configure(background=general_bg, relief='ridge', borderwidth=0)
frame_csv.configure(background=general_bg, relief='ridge', borderwidth=2)

# frame_left.grid_propagate(0)
# frame_right.grid_propagate(0)
# frame_com.grid_propagate(0)
# frame_trg.grid_propagate(0)
# frame_ktx.grid_propagate(0)
# frame_sig1.grid_propagate(0)
# frame_sig2.grid_propagate(0)
# frame_prod.grid_propagate(0)
# frame_admin.grid_propagate(0)
# frame_path.grid_propagate(0)
# frame_csv.grid_propagate(0)

lbl_ktx1_on = tk.Label(frame_ktx1, text="KTX ON", bg=general_bg, fg=widget_fg)
lbl_ktx1_off = tk.Label(frame_ktx1, text="OFF", bg=general_bg, fg=widget_fg)
lbl_ktx1_unit = tk.Label(frame_ktx1, text="UNIT", bg=general_bg, fg=widget_fg)
lbl_trg1_1_on = tk.Label(frame_trg1_1, text="TRG1 ON", bg=general_bg, fg=widget_fg)
lbl_trg1_1_off = tk.Label(frame_trg1_1, text="OFF", bg=general_bg, fg=widget_fg)
lbl_trg1_1_unit = tk.Label(frame_trg1_1, text="UNIT", bg=general_bg, fg=widget_fg)
lbl_trg1_2_on = tk.Label(frame_trg1_2, text="TRG2 ON", bg=general_bg, fg=widget_fg)
lbl_trg1_2_off = tk.Label(frame_trg1_2, text="OFF", bg=general_bg, fg=widget_fg)
lbl_trg1_2_unit = tk.Label(frame_trg1_2, text="UNIT", bg=general_bg, fg=widget_fg)

lbl_ktx2_on = tk.Label(frame_ktx2, text="KTX ON", bg=general_bg, fg=widget_fg)
lbl_ktx2_off = tk.Label(frame_ktx2, text="OFF", bg=general_bg, fg=widget_fg)
lbl_ktx2_unit = tk.Label(frame_ktx2, text="UNIT", bg=general_bg, fg=widget_fg)
lbl_trg2_1_on = tk.Label(frame_trg2_1, text="TRG1 ON", bg=general_bg, fg=widget_fg)
lbl_trg2_1_off = tk.Label(frame_trg2_1, text="OFF", bg=general_bg, fg=widget_fg)
lbl_trg2_1_unit = tk.Label(frame_trg2_1, text="UNIT", bg=general_bg, fg=widget_fg)
lbl_trg2_2_on = tk.Label(frame_trg2_2, text="TRG2 ON", bg=general_bg, fg=widget_fg)
lbl_trg2_2_off = tk.Label(frame_trg2_2, text="OFF", bg=general_bg, fg=widget_fg)
lbl_trg2_2_unit = tk.Label(frame_trg2_2, text="UNIT", bg=general_bg, fg=widget_fg)

# text_csv = tk.Text(frame_csv, height=8, width=50, state=tk.DISABLED, bg=widget_bg, fg=widget_fg)
text_order = tk.Text(frame_right, height=34, width=45, state=tk.DISABLED, bg=widget_bg, fg=widget_fg)

err_out = tk.Text(frame_com, width=20)

combo_port = ttk.Combobox(frame_com, width=40, postcommand=get_com_port_list)
combo_ktx1_unit = ttk.Combobox(frame_ktx1, values=('ms', 'us'), width=4)
combo_trg1_1_unit = ttk.Combobox(frame_trg1_1, values=('ms', 'us'), width=4)
combo_trg1_2_unit = ttk.Combobox(frame_trg1_2, values=('ms', 'us'), width=4)
combo_ktx2_unit = ttk.Combobox(frame_ktx2, values=('ms', 'us'), width=4)
combo_trg2_1_unit = ttk.Combobox(frame_trg2_1, values=('ms', 'us'), width=4)
combo_trg2_2_unit = ttk.Combobox(frame_trg2_2, values=('ms', 'us'), width=4)

# btn_path = tk.Button(frame_csv, text='FILE LOCATION', command=browse_button, bg=widget_bg, fg=widget_fg,
#                      highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_connect = tk.Button(frame_com, text="CONNECT", command=connect_com, width=10, bg=widget_bg, fg=widget_fg,
                        highlightbackground=widget_fg, activebackground=general_bg, bd=2)

btn_start_ktx = tk.Button(frame_ktx1, text="START KTX", state=tk.DISABLED, command=start_ktx, width=8, bg=widget_bg,
                          fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_stop_ktx = tk.Button(frame_ktx1, text="STOP KTX", command=stop_ktx, state=tk.DISABLED, width=8, bg=widget_bg,
                         fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_start_t11 = tk.Button(frame_trg1_1, text="START SIG2", state=tk.DISABLED, command=start_sig2, width=8, bg=widget_bg,
                          fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_stop_t11 = tk.Button(frame_trg1_1, text="STOP SIG2", command=stop_sig2, state=tk.DISABLED, width=8, bg=widget_bg,
                         fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_pulse_t11 = tk.Button(frame_trg1_1, text="PULSE SIG2", state=tk.DISABLED, command=pulse_sig2, width=8, bg=widget_bg,
                          fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_ran_t11 = tk.Button(frame_trg1_1, text="RAND SIG2", state=tk.DISABLED, command=ran_sig2, width=8, bg=widget_bg,
                        fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_start_t12 = tk.Button(frame_trg1_2, text="START SIG2", state=tk.DISABLED, command=start_sig2, width=8, bg=widget_bg,
                          fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_stop_t12 = tk.Button(frame_trg1_2, text="STOP SIG2", command=stop_sig2, state=tk.DISABLED, width=8, bg=widget_bg,
                         fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_pulse_t12 = tk.Button(frame_trg1_2, text="PULSE SIG2", state=tk.DISABLED, command=pulse_sig2, width=8, bg=widget_bg,
                          fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_ran_t12 = tk.Button(frame_trg1_2, text="RAND SIG2", state=tk.DISABLED, command=ran_sig2, width=8, bg=widget_bg,
                        fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)

btn_rack1_start = tk.Button(frame_testrack1, text="START", state=tk.DISABLED, command=rack_start, bg=widget_bg,
                            fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_rack1_reset = tk.Button(frame_testrack1, text="RESET", state=tk.DISABLED, command=rack_reset, bg=widget_bg,
                            fg='lightblue', highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_rack1_shutdown = tk.Button(frame_testrack1, text="SHUTDOWN", state=tk.DISABLED, command=rack_shutdown, bg=widget_bg,
                               fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_rack1_recovery = tk.Button(frame_testrack1, text="RECOVERY", state=tk.DISABLED, command=rack_recovery, bg=widget_bg,
                               fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)

btn_rack2_start = tk.Button(frame_testrack2, text="START", state=tk.DISABLED, command=rack_start, bg=widget_bg,
                            fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_rack2_reset = tk.Button(frame_testrack2, text="RESET", state=tk.DISABLED, command=rack_reset, bg=widget_bg,
                            fg='lightblue', highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_rack2_shutdown = tk.Button(frame_testrack2, text="SHUTDOWN", state=tk.DISABLED, command=rack_shutdown, bg=widget_bg,
                               fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)
btn_rack2_recovery = tk.Button(frame_testrack2, text="RECOVERY", state=tk.DISABLED, command=rack_recovery, bg=widget_bg,
                               fg=widget_fg, highlightbackground=widget_fg, activebackground=general_bg, bd=2)

entry_ktx1_on_time = tk.Entry(frame_testrack1, width=5, bg=widget_bg, fg=widget_fg)
entry_ktx1_off_time = tk.Entry(frame_testrack1, width=5, bg=widget_bg, fg=widget_fg)
entry_trg11_on_time = tk.Entry(frame_testrack1, width=5, bg=widget_bg, fg=widget_fg)
entry_trg11_off_time = tk.Entry(frame_testrack1, width=5, bg=widget_bg, fg=widget_fg)
entry_trg12_on_time = tk.Entry(frame_testrack1, width=5, bg=widget_bg, fg=widget_fg)
entry_trg12_off_time = tk.Entry(frame_testrack1, width=5, bg=widget_bg, fg=widget_fg)

entry_ktx1_on_time = tk.Entry(frame_testrack2, width=5, bg=widget_bg, fg=widget_fg)
entry_ktx1_off_time = tk.Entry(frame_testrack2, width=5, bg=widget_bg, fg=widget_fg)
entry_trg11_on_time = tk.Entry(frame_testrack2, width=5, bg=widget_bg, fg=widget_fg)
entry_trg11_off_time = tk.Entry(frame_testrack2, width=5, bg=widget_bg, fg=widget_fg)
entry_trg12_on_time = tk.Entry(frame_testrack2, width=5, bg=widget_bg, fg=widget_fg)
entry_trg12_off_time = tk.Entry(frame_testrack2, width=5, bg=widget_bg, fg=widget_fg)

entry_ktx1_pin = tk.Entry(frame_testrack1, width=3, bg=widget_bg, fg=widget_fg)
entry_trg11_pin = tk.Entry(frame_testrack1, width=3, bg=widget_bg, fg=widget_fg)
entry_trg12_pin = tk.Entry(frame_testrack1, width=3, bg=widget_bg, fg=widget_fg)
entry_ktx2_pin = tk.Entry(frame_testrack2, width=3, bg=widget_bg, fg=widget_fg)
entry_trg21_pin = tk.Entry(frame_testrack2, width=3, bg=widget_bg, fg=widget_fg)
entry_trg22_pin = tk.Entry(frame_testrack2, width=3, bg=widget_bg, fg=widget_fg)

entry_reset_pin = tk.Entry(frame_testrack1, width=3, bg=widget_bg, fg=widget_fg)
entry_start_pin = tk.Entry(frame_testrack1, width=3, bg=widget_bg, fg=widget_fg)
entry_reset_pin = tk.Entry(frame_testrack2, width=3, bg=widget_bg, fg=widget_fg)
entry_start_pin = tk.Entry(frame_testrack2, width=3, bg=widget_bg, fg=widget_fg)

master.protocol("WM_DELETE_WINDOW", close_dialog)
master.after(2000, check_connection)

config = configparser.ConfigParser()
config.read('config.ini')

try:
    port = config.get('general', 'port')
    filename = config.get('general', 'file_path')
    ktx1 = ChannelSettings(config.get('ktx1', 'on_time'), config.get('ktx1', 'off_time'), config.get('ktx1', 'unit'),
                           config.get('ktx1', 'pin'), 0)
    trg11 = ChannelSettings(config.get('trg11', 'on_time'), config.get('trg11', 'off_time'),
                            config.get('trg11', 'unit'), config.get('trg11', 'pin'), 0)
    trg12 = ChannelSettings(config.get('trg12', 'on_time'), config.get('trg12', 'off_time'),
                            config.get('trg12', 'unit'), config.get('trg12', 'pin'), 0)

    ktx2 = ChannelSettings(config.get('ktx2', 'on_time'), config.get('ktx2', 'off_time'), config.get('ktx2', 'unit'),
                           config.get('ktx2', 'pin'), 0)
    trg21 = ChannelSettings(config.get('trg21', 'on_time'), config.get('trg21', 'off_time'),
                            config.get('trg21', 'unit'), config.get('trg21', 'pin'), 0)
    trg22 = ChannelSettings(config.get('trg22', 'on_time'), config.get('trg22', 'off_time'),
                            config.get('trg22', 'unit'), config.get('trg22', 'pin'), 0)

    reset1 = ChannelSettings(config.get('reset1', 'on_time'), 0, 0, config.get('reset1', 'pin'), 0)
    shutdown1 = ChannelSettings(config.get('shutdown1', 'on_time'), 0, 0, config.get('reset1', 'pin'), 0)
    start1 = ChannelSettings(config.get('start1', 'on_time'), 0, 0, config.get('start1', 'pin'), 0)
    recovery1 = ChannelSettings(config.get('recovery1', 'on_time'), 0, 0, config.get('start1', 'pin'), 0)

    reset2 = ChannelSettings(config.get('reset2', 'on_time'), 0, 0, config.get('reset2', 'pin'), 0)
    shutdown2 = ChannelSettings(config.get('shutdown2', 'on_time'), 0, 0, config.get('reset2', 'pin'), 0)
    start2 = ChannelSettings(config.get('start2', 'on_time'), 0, 0, config.get('start2', 'pin'), 0)
    recovery2 = ChannelSettings(config.get('recovery2', 'on_time'), 0, 0, config.get('start2', 'pin'), 0)
except (configparser.NoSectionError, configparser.NoOptionError) as err:
    print('no config')
    port = 'none'
    filename = ""
    trg = ChannelSettings('200', '800', 'ms', 0, 0)
    ktx = ChannelSettings('500', '500', 'us', 0, 0)
    sig1 = ChannelSettings('2500', '0', 'ms', 0, 0)
    sig2 = ChannelSettings('2500', '0', 'ms', 0, 0)
    reset = ChannelSettings('2000', '0', 'ms', 0, 0)
    shutdown = ChannelSettings('10000', '0', 'ms', 0, 0)
    start = ChannelSettings('2000', '0', 'ms', 0, 0)
    recovery = ChannelSettings('16000', '0', 'ms', 0, 0)

lst = serial.tools.list_ports.comports()
try:
    for item in lst:
        if item.device == port:
            combo_port.insert(0, item)
            break
    else:
        combo_port.insert(0, 'Choose COM port')
except NameError:
    combo_port.insert(0, 'Choose COM port')

# if filename.endswith('.csv'):
#     open_csv(filename)

ser = serial.Serial()

entry_trg11_on_time.insert(0, trg.on_time)
entry_trg11_off_time.insert(0, trg.off_ime)
combo_trg_unit.insert(0, trg.unit)
entry_ktx_on_time.insert(0, ktx.on_time)
entry_ktx_off_time.insert(0, ktx.off_ime)
combo_ktx_unit.insert(0, ktx.unit)
entry_sig1_on_time.insert(0, sig1.on_time)
entry_sig1_off_time.insert(0, sig1.off_ime)
combo_sig1_unit.insert(0, sig1.unit)
entry_sig2_on_time.insert(0, sig2.on_time)
entry_sig2_off_time.insert(0, sig2.off_ime)
combo_sig2_unit.insert(0, sig2.unit)
entry_sig2_seed.insert(0, sig2.seed)
entry_trg_pin.insert(0, trg.pin)
entry_ktx_pin.insert(0, ktx.pin)
entry_sig1_pin.insert(0, sig1.pin)
entry_sig2_pin.insert(0, sig2.pin)
entry_reset_pin.insert(0, reset.pin)
entry_start_pin.insert(0, start.pin)

combo_port['state'] = 'readonly'
combo_trg_unit['state'] = 'readonly'
combo_ktx_unit['state'] = 'readonly'
combo_sig1_unit['state'] = 'readonly'
combo_sig2_unit['state'] = 'readonly'

combostyle = ttk.Style()

combostyle.theme_create('combostyle', parent='alt', settings={'TCombobox': {'configure': {'selectbackground': widget_bg,
                                                                                          'fieldbackground': widget_bg,
                                                                                          'background': widget_fg,
                                                                                          'foreground': widget_fg}}})
combostyle.theme_use('combostyle')

# btn_path.grid(sticky='w', row=0, column=0, padx=5, pady=5)
# lbl_path.grid(sticky='w', row=1, column=0, padx=5, pady=0)
# text_csv.grid(sticky='w', row=2, column=0, padx=5, pady=2)

combo_port.grid(sticky='w', row=2, column=0, pady=3)
btn_connect.grid(row=2, column=1, padx=5)

lbl_trg_on.grid(sticky='w', row=0, column=0)
lbl_trg_off.grid(sticky='w', row=0, column=1)
lbl_trg_unit.grid(sticky='w', row=0, column=2)
entry_trg_pin.grid(row=0, column=3)
entry_trg_on_time.grid(row=1, column=0, pady=3)
entry_trg_off_time.grid(row=1, column=1, pady=3, padx=5)
combo_trg_unit.grid(row=1, column=2, pady=4, padx=5)
btn_start_trg.grid(row=1, column=3)
btn_stop_trg.grid(row=1, column=4, padx=2)
btn_pulse_trg.grid(row=1, column=5, padx=2)

lbl_ktx_on.grid(sticky='w', row=0, column=0)
lbl_ktx_off.grid(sticky='w', row=0, column=1)
lbl_ktx_unit.grid(sticky='w', row=0, column=2)
entry_ktx_pin.grid(row=0, column=3)
entry_ktx_on_time.grid(row=1, column=0, pady=3)
entry_ktx_off_time.grid(row=1, column=1, pady=3, padx=5)
combo_ktx_unit.grid(row=1, column=2, pady=4, padx=5)
btn_start_ktx.grid(row=1, column=3)
btn_stop_ktx.grid(row=1, column=4, padx=2)

lbl_sig1_on.grid(sticky='w', row=0, column=0)
lbl_sig1_off.grid(sticky='w', row=0, column=1)
lbl_sig1_unit.grid(sticky='w', row=0, column=2)
entry_sig1_pin.grid(row=0, column=3)
entry_sig1_on_time.grid(row=1, column=0, pady=3)
entry_sig1_off_time.grid(row=1, column=1, pady=3, padx=5)
combo_sig1_unit.grid(row=1, column=2, pady=4, padx=5)
btn_start_sig1.grid(row=1, column=3)
btn_stop_sig1.grid(row=1, column=4, padx=2)
btn_pulse_sig1.grid(row=1, column=5, padx=2)

lbl_sig2_on.grid(sticky='w', row=0, column=0)
lbl_sig2_off.grid(sticky='w', row=0, column=1)
lbl_sig2_unit.grid(sticky='w', row=0, column=2)
entry_sig2_pin.grid(row=0, column=3)
entry_sig2_on_time.grid(row=1, column=0, pady=3)
entry_sig2_off_time.grid(row=1, column=1, pady=3, padx=5)
combo_sig2_unit.grid(row=1, column=2, pady=4, padx=5)
btn_start_sig2.grid(row=1, column=3)
btn_stop_sig2.grid(row=1, column=4, padx=2)
btn_pulse_sig2.grid(row=1, column=5, padx=2)
btn_seq_sig2.grid(row=2, column=3, padx=2)
btn_ran_sig2.grid(row=2, column=5, padx=2)
entry_sig2_seed.grid(row=2, column=4, pady=3)

# btn_start_prod.grid(row=0, column=0)
# btn_stop_prod.grid(row=0, column=1, padx=5)

btn_rack_reset.grid(row=0, column=0)
btn_rack_start.grid(row=0, column=1, padx=50)
btn_rack_recovery.grid(row=0, column=2)
btn_rack_shutdown.grid(row=0, column=3, padx=50)
entry_reset_pin.grid(row=1, column=0, padx=5, pady=5)
entry_start_pin.grid(row=1, column=1, padx=5, pady=5)

frame_com.grid(sticky='w', row=1, column=0, padx=5, pady=3)
frame_trg.grid(sticky='w', row=2, column=0, padx=5, pady=0)
frame_ktx.grid(sticky='w', row=3, column=0, padx=5, pady=0)
frame_sig1.grid(sticky='w', row=4, column=0, padx=5, pady=0)
frame_sig2.grid(sticky='w', row=5, column=0, padx=5, pady=0)
# frame_prod.grid(sticky='w', row=6, column=0, padx=5, pady=15)
frame_admin.grid(sticky='w', row=7, column=0, padx=5, pady=15)
# frame_csv.grid(sticky='w', row=10, column=0, padx=5, pady=0)

text_order.grid(sticky='w', row=0, column=0, padx=5, pady=4)

frame_left.grid(sticky='nw', row=0, column=0, padx=0, pady=5)
frame_right.grid(sticky='w', row=0, column=1, padx=0, pady=5)

text_order.config(state=tk.NORMAL)

master.mainloop()
