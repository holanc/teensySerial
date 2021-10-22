# from _testcapi import traceback_print

import serial
import time
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsgbox
import tkinter as tk
import serial.tools.list_ports
import configparser
from tkinter import filedialog as fd

tr = [
    {
        'id': 1,
        'on_pin': 25,
        'off_pin': 29,
        'ktx_pin': 32,
        'sig1_pin': 31,
        'sig2_pin': 34
    },
    {
        'id': 2,
        'on_pin': 24,
        'off_pin': 28,
        'ktx_pin': 21,
        'sig1_pin': 22,
        'sig2_pin': 23
    }
]

pins = [31, 34, 35, 36, 37, 38, 39, 40, 41, 16., 17, 18, 19, 20, 21, 22, 23]


class TestRackSetup:
    def __init__(self, identifier, speed, sig1_on_time, sig1_off_time, sig2_on_time, sig2_off_time):
        self.id = identifier
        self.speed = speed
        self.sig1_on_time = sig1_on_time
        self.sig1_off_time = sig1_off_time
        self.sig2_on_time = sig2_on_time
        self.sig2_off_time = sig2_off_time


class SignalSetup:
    def __init__(self, pin, on, off, unit, rand):
        self.pin = pin
        self.on = on
        self.off = off
        self.unit = unit
        self.rand = rand


def get_com_port_list():
    port_list = serial.tools.list_ports.comports()
    combo_port['values'] = port_list


def connect_com():
    try:
        if ser.is_open:
            ser.close()
        port_list = serial.tools.list_ports.comports()
        ser.port = port_list[combo_port.current()].device
        ser.baudrate = 9600
        ser.parity = serial.PARITY_NONE
        ser.bytesize = serial.EIGHTBITS
        ser.timeout = 0
        # for arduino nano every:
        # ser.dsrdtr = None
        ser.open()
        # time.sleep(1.5)
        if ser.is_open:
            master.after(2000, check_connection)
            # btn_start_trg['state'] = tk.NORMAL
            # btn_pulse_trg['state'] = tk.NORMAL
            # btn_start_ktx['state'] = tk.NORMAL
            # btn_start_sig1['state'] = tk.NORMAL
            # btn_start_sig2['state'] = tk.NORMAL
            # btn_pulse_sig1['state'] = tk.NORMAL
            # btn_pulse_sig2['state'] = tk.NORMAL
            # btn_start_prod['state'] = tk.NORMAL
            # btn_rack_start['state'] = tk.NORMAL
            # btn_rack_recovery['state'] = tk.NORMAL
            # btn_rack_reset['state'] = tk.NORMAL
            # btn_rack_shutdown['state'] = tk.NORMAL
            # btn_pulse_sig1['state'] = tk.NORMAL
            # btn_pulse_sig2['state'] = tk.NORMAL
            # btn_seq_sig2['state'] = tk.NORMAL
            # btn_ran_sig2['state'] = tk.NORMAL
            text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + f' connected to {ser.port} ' + '\n')
    except (ValueError, serial.SerialException, IndexError):
        except_string = 'could not connect to port'
        # print(except_string)
        text_order.insert('1.0', except_string + '\n')


def write_ser(data):
    global num_order
    num_order += 1
    if ser.is_open:
        try:
            ser.write(data.encode())
            text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' >> ' + str(
                num_order) + ': ' + data + '\n')
        except serial.SerialException:
            text_order.insert('1.0',
                              time.strftime("%H:%M:%S", time.localtime()) + ' SerialException: write failed\n')

        print(data)


def tr_start(testrack):
    serial_data = f"{{SIG_{testrack['on_pin']}_{start_on_time}_0_0}}"
    text_order_data = 'testrack ' + f"{testrack['id']}" + ' start' + '\n'
    write_ser(serial_data)
    text_order.insert('1.0', text_order_data)


def tr_recovery(testrack):
    serial_data = f"{{SIG_{testrack['on_pin']}_{recovery_on_time}_0_0}}"
    text_order_data = 'recover testrack ' + f"{testrack['id']}" + '\n'
    write_ser(serial_data)
    text_order.insert('1.0', text_order_data)


def tr_reset(testrack):
    serial_data = f"{{SIG_{testrack['off_pin']}_{reset_on_time}_0_0}}"
    text_order_data = 'reset testrack ' + f"{testrack['id']}" + '\n'
    write_ser(serial_data)
    text_order.insert('1.0', text_order_data)


def tr_shutdown(testrack):
    serial_data = f"{{SIG_{testrack['off_pin']}_{shutdown_on_time}_0_0}}"
    text_order_data = 'shut down testrack ' + f"{testrack['id']}" + '\n'
    write_ser(serial_data)
    text_order.insert('1.0', text_order_data)


def tr_submit(testrack):
    tr[0]['speed'] = entry_tr1_speed.get()
    tr[0]['on1'] = entry_tr1_sig1_on.get()
    tr[0]['off1'] = entry_tr1_sig1_off.get()
    tr[0]['on2'] = entry_tr1_sig2_on.get()
    tr[0]['off2'] = entry_tr1_sig2_off.get()
    tr[1]['speed'] = entry_tr2_speed.get()
    tr[1]['on1'] = entry_tr2_sig1_on.get()
    tr[1]['off1'] = entry_tr2_sig1_off.get()
    tr[1]['on2'] = entry_tr2_sig2_on.get()
    tr[1]['off2'] = entry_tr2_sig2_off.get()

    # try:
    #     # on_time = int(testrack['speed'])
    #     # on_time = int(1000000 / (on_time / 2))
    # except (ValueError, ZeroDivisionError):
    #     on_time = 0
    #     text_order.insert('1.0', "no value defined\n")

    serial_data = f"{{SIG_{testrack['ktx_pin']}_{testrack['speed']}_{testrack['speed']}_1}}"
    # except ValueError:
    #     print("no value defined")
    # else:

    write_ser(serial_data)

    serial_data = f"{{SIG_{testrack['sig1_pin']}_{testrack['on1']}_{testrack['off1']}_0}}"
    write_ser(serial_data)

    serial_data = f"{{SIG_{testrack['sig2_pin']}_{testrack['on2']}_{testrack['off2']}_0}}"
    write_ser(serial_data)


def sig_set(order):
    pin = combo_sig_pin.get()
    on = entry_sig_on.get()
    off = entry_sig_off.get()
    unit = combo_sig_unit.current()
    rand = entry_sig_pin.get()

    if order == 0:
        serial_data = f"{{SIG_{pin}_0_0_0}}"
    elif order == 1:
        serial_data = f"{{SIG_{pin}_{on}_{off}_{unit}}}"
    elif order == 2:
        serial_data = f"{{SIG_{pin}_{on}_0_{unit}}}"
    write_ser(serial_data)


def create_button(frm, txt, width, cmd):
    return tk.Button(frm, text=txt, command=cmd, width=width, bg=bg, fg=fg, compound="center",
                     highlightbackground=fg, activebackground=general_bg, bd=2, image=pixel, height=12)


def close_dialog():
    res = tkmsgbox.askyesno('teensyCtrl', 'Do you want to quit the program?')
    if res:
        if ser.is_open:
            ser.close()
        master.destroy()


def check_connection():
    port_lst = serial.tools.list_ports.comports()
    try:
        for port_item in port_lst:
            if port_item.device == port:
                master.after(2000, check_connection)
                break
        else:
            text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' serial connection lost\n')
            ser.close()
    except NameError:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' serial connection lost\n')
        ser.close()


def create_ini():
    default_ini = open('defaults.ini')
    data = default_ini.read()
    new_ini = open('teensyCtrl.ini', "w")
    new_ini.write(data)


master = tk.Tk()
general_bg = 'grey47'
bg = 'grey20'
fg = 'whitesmoke'
num_order = 0

master.title("teensyCtrl")
master.geometry("825x570+100+100")
frame_left = tk.Frame(master)
frame_right = tk.Frame(master)
frame_com = tk.Frame(frame_left)
frame_tr1 = tk.Frame(frame_left)
frame_tr1_1 = tk.Frame(frame_tr1)
frame_tr1_2 = tk.Frame(frame_tr1)
frame_tr1_3 = tk.Frame(frame_tr1)
frame_tr2 = tk.Frame(frame_left)
frame_tr2_1 = tk.Frame(frame_tr2)
frame_tr2_2 = tk.Frame(frame_tr2)
frame_tr2_3 = tk.Frame(frame_tr2)
frame_sig = tk.Frame(frame_left)
frame_sig_1 = tk.Frame(frame_sig)
frame_sig_2 = tk.Frame(frame_sig)
frame_sig_3 = tk.Frame(frame_sig)
frame_sreg = tk.Frame(frame_left)

pixel = tk.PhotoImage(width=1, height=1)

master.configure(background=general_bg)
frame_left.configure(background=general_bg)
frame_right.configure(background=general_bg, relief='ridge', borderwidth=2)
frame_com.configure(background=general_bg, relief='ridge', borderwidth=2)
frame_tr1.configure(background=general_bg, relief='ridge', borderwidth=2)
frame_tr1_1.configure(background=general_bg)
frame_tr1_2.configure(background=general_bg)
frame_tr1_3.configure(background=general_bg)
frame_tr2.configure(background=general_bg, relief='ridge', borderwidth=2)
frame_tr2_1.configure(background=general_bg)
frame_tr2_2.configure(background=general_bg)
frame_tr2_3.configure(background=general_bg)
frame_sig.configure(background=general_bg, relief='ridge', borderwidth=2)
frame_sig_1.configure(background=general_bg)
frame_sig_2.configure(background=general_bg)
frame_sig_3.configure(background=general_bg)
frame_sreg.configure(background=general_bg, relief='ridge', borderwidth=2)

lbl_tr1 = tk.Label(frame_tr1_1, text="testrack 1", bg=general_bg, fg=fg, font=(None, 12))
lbl_tr2 = tk.Label(frame_tr2_1, text="testrack 2", bg=general_bg, fg=fg, font=(None, 12))

lbl_tr1_sig1_on = tk.Label(frame_tr1_3, text="signal 1\non [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr1_sig1_off = tk.Label(frame_tr1_3, text="signal 1\noff [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr1_sig2_on = tk.Label(frame_tr1_3, text="signal 2\non [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr1_sig2_off = tk.Label(frame_tr1_3, text="signal 2\noff [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr1_speed = tk.Label(frame_tr1_3, text="speed\nmm/s", bg=general_bg, fg=fg, font=(None, 7))

lbl_tr2_sig1_on = tk.Label(frame_tr2_3, text="signal 1\non [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr2_sig1_off = tk.Label(frame_tr2_3, text="signal 1\noff [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr2_sig2_on = tk.Label(frame_tr2_3, text="signal 2\non [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr2_sig2_off = tk.Label(frame_tr2_3, text="signal 2\noff [ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_tr2_speed = tk.Label(frame_tr2_3, text="speed\nmm/s", bg=general_bg, fg=fg, font=(None, 7))

lbl_sig = tk.Label(frame_sig_1, text="signal", bg=general_bg, fg=fg, font=(None, 12))
lbl_sig_pin = tk.Label(frame_sig_2, text="pin", bg=general_bg, fg=fg, font=(None, 7))
lbl_sig_on = tk.Label(frame_sig_2, text="on\n[ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_sig_off = tk.Label(frame_sig_2, text="off\n[ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_sig_unit = tk.Label(frame_sig_2, text="unit\n[us/ms]", bg=general_bg, fg=fg, font=(None, 7))
lbl_sig_rand = tk.Label(frame_sig_2, text="rand\n[ms]", bg=general_bg, fg=fg, font=(None, 7))

text_order = tk.Text(frame_right, height=34, width=45, bg=bg, fg=fg)

err_out = tk.Text(frame_com, width=20)

btn_connect = create_button(frame_com, "CONNECT", 65, connect_com)
combo_port = ttk.Combobox(frame_com, width=40, postcommand=get_com_port_list)

btn_tr1_start = create_button(frame_tr1_2, "start", 25, lambda: tr_start(tr[0]))
btn_tr1_reset = create_button(frame_tr1_2, "reset", 25, lambda: tr_reset(tr[0]))
btn_tr1_recovery = create_button(frame_tr1_2, "recovery", 45, lambda: tr_recovery(tr[0]))
btn_tr1_shutdown = create_button(frame_tr1_2, "shut down", 55, lambda: tr_shutdown(tr[0]))
btn_tr1_submit = create_button(frame_tr1_3, "submit", 55, lambda: tr_submit(tr[0]))

btn_tr2_start = create_button(frame_tr2_2, "start", 25, lambda: tr_start(tr[1]))
btn_tr2_reset = create_button(frame_tr2_2, "reset", 25, lambda: tr_reset(tr[1]))
btn_tr2_recovery = create_button(frame_tr2_2, "recovery", 45, lambda: tr_recovery(tr[1]))
btn_tr2_shutdown = create_button(frame_tr2_2, "shut down", 55, lambda: tr_shutdown(tr[1]))
btn_tr2_submit = create_button(frame_tr2_3, "submit", 55, lambda: tr_submit(tr[1]))

btn_sig_start = create_button(frame_sig_3, "start", 25, lambda: sig_set(1))
btn_sig_stop = create_button(frame_sig_3, "stop", 25, lambda: sig_set(0))
btn_sig_pulse = create_button(frame_sig_3, "pulse", 25, lambda: sig_set(2))

btn_create_ini = create_button(frame_com, "create ini", 55, create_ini)

combo_ktx1_unit = ttk.Combobox(frame_tr1, values=('ms', 'us'), width=4)
combo_trg1_1_unit = ttk.Combobox(frame_tr1, values=('ms', 'us'), width=4)
combo_trg1_2_unit = ttk.Combobox(frame_tr1, values=('ms', 'us'), width=4)
combo_ktx2_unit = ttk.Combobox(frame_tr2, values=('ms', 'us'), width=4)
combo_trg2_1_unit = ttk.Combobox(frame_tr2, values=('ms', 'us'), width=4)
combo_trg2_2_unit = ttk.Combobox(frame_tr2, values=('ms', 'us'), width=4)

entry_tr1_speed = tk.Entry(frame_tr1_3, width=6, bg=bg, fg=fg)
entry_tr1_sig1_on = tk.Entry(frame_tr1_3, width=6, bg=bg, fg=fg)
entry_tr1_sig1_off = tk.Entry(frame_tr1_3, width=6, bg=bg, fg=fg)
entry_tr1_sig2_on = tk.Entry(frame_tr1_3, width=6, bg=bg, fg=fg)
entry_tr1_sig2_off = tk.Entry(frame_tr1_3, width=6, bg=bg, fg=fg)

entry_tr2_id = tk.Entry(frame_tr2, width=10, bg=bg, fg=fg)
entry_tr2_speed = tk.Entry(frame_tr2_3, width=6, bg=bg, fg=fg)
entry_tr2_sig1_on = tk.Entry(frame_tr2_3, width=6, bg=bg, fg=fg)
entry_tr2_sig1_off = tk.Entry(frame_tr2_3, width=6, bg=bg, fg=fg)
entry_tr2_sig2_on = tk.Entry(frame_tr2_3, width=6, bg=bg, fg=fg)
entry_tr2_sig2_off = tk.Entry(frame_tr2_3, width=6, bg=bg, fg=fg)

entry_sig_pin = tk.Entry(frame_sig_2, width=6, bg=bg, fg=fg)
entry_sig_on = tk.Entry(frame_sig_2, width=6, bg=bg, fg=fg)
entry_sig_off = tk.Entry(frame_sig_2, width=6, bg=bg, fg=fg)
entry_sig_rand = tk.Entry(frame_sig_2, width=6, bg=bg, fg=fg)

combo_sig_unit = ttk.Combobox(frame_sig_2, values=('ms', 'us'), width=7)
combo_sig_pin = ttk.Combobox(frame_sig_2, values=pins, width=2)

master.protocol("WM_DELETE_WINDOW", close_dialog)
# master.after(2000, check_connection)

config_file = 'teensyCtrl.ini'
config = configparser.ConfigParser()
config.read(config_file)

try:
    port = config.get('general', 'port')
    auto_connect = config.get('general', 'auto_connect')
    tr1_settings = TestRackSetup(config.get('tr1', 'id'), config.get('tr1', 'speed'), config.get('tr1', 'sig1_on'),
                                 config.get('tr1', 'sig1_off'), config.get('tr1', 'sig2_on'),
                                 config.get('tr1', 'sig2_off'))
    tr2_settings = TestRackSetup(config.get('tr2', 'id'), config.get('tr2', 'speed'), config.get('tr2', 'sig1_on'),
                                 config.get('tr2', 'sig1_off'), config.get('tr2', 'sig2_on'),
                                 config.get('tr2', 'sig2_off'))

    sig_settings = SignalSetup(config.get('sig', 'pin'), config.get('sig', 'on'), config.get('sig', 'off'),
                               config.get('sig', 'unit'), config.get('sig', 'rand'))

    reset_on_time = config.get('reset', 'on_time')
    shutdown_on_time = config.get('shutdown', 'on_time')
    start_on_time = config.get('start', 'on_time')
    recovery_on_time = config.get('recovery', 'on_time')
    text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + f" {config_file} processed\n")
except (configparser.NoSectionError, configparser.NoOptionError) as err:
    text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' no config file found\n')
    port = 'none'
    auto_connect = 0
    tr1_settings = TestRackSetup("testrack 1", 500, 200, 800, 0, 0)
    tr2_settings = TestRackSetup("testrack 2", 500, 200, 800, 0, 0)
    sig_settings = SignalSetup(32, 500, 500, 0, 0)
    reset_on_time = 2000
    shutdown_on_time = 10000
    start_on_time = 2000
    recovery_on_time = 16000

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
ser = serial.Serial()

lbl_tr1.config(text=tr1_settings.id)
entry_tr1_speed.insert(0, tr1_settings.speed)
entry_tr1_sig1_on.insert(0, tr1_settings.sig1_on_time)
entry_tr1_sig1_off.insert(0, tr1_settings.sig1_off_time)
entry_tr1_sig2_on.insert(0, tr1_settings.sig2_on_time)
entry_tr1_sig2_off.insert(0, tr1_settings.sig2_off_time)

lbl_tr2.config(text=tr2_settings.id)
entry_tr2_speed.insert(0, tr2_settings.speed)
entry_tr2_sig1_on.insert(0, tr2_settings.sig1_on_time)
entry_tr2_sig1_off.insert(0, tr2_settings.sig1_off_time)
entry_tr2_sig2_on.insert(0, tr2_settings.sig2_on_time)
entry_tr2_sig2_off.insert(0, tr2_settings.sig2_off_time)

entry_sig_pin.insert(0, sig_settings.pin)
entry_sig_on.insert(0, sig_settings.on)
entry_sig_off.insert(0, sig_settings.off)
entry_sig_rand.insert(0, sig_settings.rand)
combo_sig_pin.insert(0, sig_settings.pin)
combo_sig_unit.insert(0, sig_settings.unit)

combo_port.grid(sticky='w', row=0, column=0, pady=3)
btn_connect.grid(row=0, column=1, padx=5)
btn_create_ini.grid(sticky='w', row=1, column=0, padx=5)
frame_com.grid(sticky='w', row=0, column=0, padx=5, pady=3)

lbl_tr1.grid(sticky='nw', row=0, column=0, padx=2)
btn_tr1_start.grid(sticky='nw', row=1, column=0, padx=2)
btn_tr1_reset.grid(row=1, column=1, padx=2)
btn_tr1_recovery.grid(row=1, column=2, padx=2)
btn_tr1_shutdown.grid(row=1, column=3, padx=2)
btn_tr1_submit.grid(row=3, column=5, padx=(5, 5), pady=(0, 4))

lbl_tr2.grid(sticky='nw', row=0, column=0, padx=2)
btn_tr2_start.grid(sticky='nw', row=1, column=0, padx=2)
btn_tr2_reset.grid(row=1, column=1, padx=2)
btn_tr2_recovery.grid(row=1, column=2, padx=2)
btn_tr2_shutdown.grid(row=1, column=3, padx=2)
btn_tr2_submit.grid(row=3, column=5, padx=(5, 5), pady=(0, 4))

lbl_tr1_speed.grid(sticky='w', row=2, column=0, padx=2)
entry_tr1_speed.grid(row=3, column=0, padx=2)
lbl_tr1_sig1_on.grid(sticky='w', row=2, column=1, padx=2)
entry_tr1_sig1_on.grid(row=3, column=1, padx=2)
lbl_tr1_sig1_off.grid(sticky='w', row=2, column=2, padx=2)
entry_tr1_sig1_off.grid(sticky='w', row=3, column=2, padx=2)
lbl_tr1_sig2_on.grid(sticky='w', row=2, column=3, padx=2)
entry_tr1_sig2_on.grid(row=3, column=3, padx=2)
lbl_tr1_sig2_off.grid(sticky='w', row=2, column=4, padx=2)
entry_tr1_sig2_off.grid(sticky='w', row=3, column=4, padx=2)

lbl_tr2_speed.grid(sticky='w', row=2, column=0, padx=2)
entry_tr2_speed.grid(row=3, column=0, padx=2)
lbl_tr2_sig1_on.grid(sticky='w', row=2, column=1, padx=2)
entry_tr2_sig1_on.grid(row=3, column=1, padx=2)
lbl_tr2_sig1_off.grid(sticky='w', row=2, column=2, padx=2)
entry_tr2_sig1_off.grid(sticky='w', row=3, column=2, padx=2)
lbl_tr2_sig2_on.grid(sticky='w', row=2, column=3, padx=2)
entry_tr2_sig2_on.grid(row=3, column=3, padx=2)
lbl_tr2_sig2_off.grid(sticky='w', row=2, column=4, padx=2)
entry_tr2_sig2_off.grid(sticky='w', row=3, column=4, padx=2)

frame_tr1_1.grid(sticky='w', row=0, column=0)
frame_tr1_2.grid(sticky='w', row=1, column=0)
frame_tr1_3.grid(sticky='w', row=2, column=0)
frame_tr1.grid(sticky='w', row=1, column=0, padx=2, pady=5)

lbl_tr2.grid(sticky='w', row=0, column=0, padx=2, columnspan=2)
btn_tr2_start.grid(row=1, column=0, padx=2)
btn_tr2_reset.grid(row=1, column=1, padx=2)
btn_tr2_recovery.grid(row=1, column=2, padx=2)
btn_tr2_shutdown.grid(row=1, column=3, padx=2)

frame_tr2_1.grid(sticky='w', row=0, column=0)
frame_tr2_2.grid(sticky='w', row=1, column=0)
frame_tr2_3.grid(sticky='w', row=2, column=0)
frame_tr2.grid(sticky='w', row=2, column=0, padx=2, pady=5)

lbl_sig.grid(sticky='w', row=3, column=0, padx=2)
lbl_sig_pin.grid(sticky='w', row=0, column=0, padx=2)
lbl_sig_on.grid(sticky='w', row=0, column=1, padx=2)
lbl_sig_off.grid(sticky='w', row=0, column=2, padx=2)
lbl_sig_unit.grid(sticky='w', row=0, column=3, padx=2)
lbl_sig_rand.grid(sticky='w', row=0, column=4, padx=2)

entry_sig_on.grid(sticky='w', row=1, column=1, padx=2)
entry_sig_off.grid(sticky='w', row=1, column=2, padx=2)
entry_sig_rand.grid(sticky='w', row=1, column=4, padx=2)

combo_sig_pin.grid(sticky='w', row=1, column=0, padx=2)
combo_sig_unit.grid(sticky='w', row=1, column=3, padx=2)

btn_sig_start.grid(row=0, column=0, padx=2)
btn_sig_stop.grid(row=0, column=1, padx=2)
btn_sig_pulse.grid(row=0, column=2, padx=2)

frame_sig_1.grid(sticky='w', row=0, column=0)
frame_sig_2.grid(sticky='w', row=1, column=0)
frame_sig_3.grid(sticky='w', row=2, column=0)
frame_sig.grid(sticky='w', row=3, column=0, padx=2, pady=5)

frame_left.grid(sticky='nw', row=0, column=0, padx=2, pady=5)

text_order.grid(sticky='w', row=0, column=0, padx=5, pady=4)
frame_right.grid(sticky='w', row=0, column=1, padx=0, pady=5)

# text_order.config(state=tk.NORMAL)

if port != 'none' and auto_connect == 'on':
    connect_com()

master.mainloop()
