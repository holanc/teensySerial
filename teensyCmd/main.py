import serial
import time
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsgbox
import tkinter as tk
import serial.tools.list_ports
import configparser
from ttkthemes import ThemedStyle
import subprocess

default_ini = "[general]\n" \
              "auto_connect = on           ; on / off\n" \
              "port = COM6                 ; COMx\n\n" \
              "; uncomment the one theme you want to use\n\n" \
              ";theme = elegance\n" \
              ";theme = blue\n" \
              ";theme = breeze\n" \
              "theme = yaru\n" \
              ";theme = radiance\n" \
              ";theme = equilux\n\n" \
              "[testrack1]\n" \
              "id = 2ZB000136              ; enter name or device number\n" \
              "speed = 500                 ; speed in mm/s\n" \
              "sig1_on = 200               ; on time in ms\n" \
              "sig1_off = 800              ; off time in ms\n" \
              "sig2_on = 0                 ; on time in ms\n" \
              "sig2_off = 0                ; off time in ms\n\n" \
              "[testrack2]\n" \
              "id = 2ZB000457              ; enter name or device number\n" \
              "speed = 500                 ; speed in mm/s\n" \
              "sig1_on = 200               ; on time in ms\n" \
              "sig1_off = 800              ; off time in ms\n" \
              "sig2_on = 0                 ; on time in ms\n" \
              "sig2_off = 0                ; off time in ms\n\n" \
              "[sig]\n" \
              "id = sig                    ; currently not used\n" \
              "pin = 32                    ; PIN according to teensy 4.1 pinout\n" \
              "on = 500                    ; on time in ms or us (according to unit)\n" \
              "off = 500                   ; off time in ms or us (according to unit)\n" \
              "unit = ms                   ; us / ms\n" \
              "rand = 0                    ; 0/1 lo-time will be between on-time*3 and off-time\n\n" \
              "[reset]\n" \
              "on_time = 2000              ; do not touch\n\n" \
              "[shutdown]\n" \
              "on_time = 10000             ; do not touch\n\n" \
              "[start]\n" \
              "on_time = 2000              ; do not touch\n\n" \
              "[recovery]\n" \
              "on_time = 16000             ; do not touch"

# board = 'teensy4.0'
board = 'teensy4.1'

if board == 'teensy4.1':
    pins = [31, 34, 35, 36, 37, 38, 39, 40, 41, 16, 17, 18, 19, 20, 21, 22, 23]
else:
    pins = [13]


class TestRackSetup:
    def __init__(self, name, on_pin, off_pin, ktx_pin, sig1_pin, sig2_pin):
        self.on_pin = on_pin
        self.off_pin = off_pin
        self.ktx_pin = ktx_pin
        self.sig1_pin = sig1_pin
        self.sig2_pin = sig2_pin
        self.name = name
        self.speed = "500"
        self.on1 = "200"
        self.off1 = '800'
        self.on2 = '200'
        self.off2 = '800'
        self.ktx_on = 0
        self.sig1_on = 0
        self.sig2_on = 0

    def set_settings(self, name, speed, sig1_on_time, sig1_off_time, sig2_on_time, sig2_off_time):
        if not name == 'dummy':
            self.name = name
        self.speed = speed
        self.on1 = sig1_on_time
        self.off1 = sig1_off_time
        self.on2 = sig2_on_time
        self.off2 = sig2_off_time


class SignalSetup:
    def __init__(self, pin, on, off, unit, rand):
        self.pin = pin
        self.on = on
        self.off = off
        self.unit = unit
        self.rand = int(rand)

    def update(self, pin, on, off, unit):
        self.pin = pin
        self.on = on
        self.off = off
        self.unit = unit


def get_com_port_list():
    port_list = serial.tools.list_ports.comports()
    combo_port['values'] = port_list


def check_port(port_device, port_name):
    port_lst = serial.tools.list_ports.comports()
    try:
        for port_item in port_lst:
            if (port_device and port_item.device == port_device) or (port_name != '' and str(port_item) == port_name):
                return port_item
        else:
            return 0
    except NameError:
        return 0


def connect_com():
    port_name = combo_port.get()
    comport = check_port(0, port_name)
    try:
        global _port_device
        if ser.is_open:
            ser.close()
        ser.port = comport.device
        ser.baudrate = 9600
        ser.parity = serial.PARITY_NONE
        ser.bytesize = serial.EIGHTBITS
        ser.timeout = 0
        # for arduino nano every:
        # ser.dsrdtr = None
        ser.open()
        time.sleep(0.5)
        if not ser.port == comport.device:
            text_order.insert('1.0',
                              time.strftime("%H:%M:%S", time.localtime()) + f' disconnect from {ser.port}\n')
            ser.close()
        else:
            _port_device = comport.device
        if ser.is_open:
            root.after(2000, check_connection)
            text_order.insert('1.0',
                              time.strftime("%H:%M:%S", time.localtime()) + f' connected to {ser.port} ' + '\n')
    except (ValueError, serial.SerialException, IndexError):
        text_order.insert('1.0',
                          time.strftime("%H:%M:%S", time.localtime()) + f' could not connect to {comport.device}\n')
    except AttributeError:
        text_order.insert('1.0',
                          time.strftime("%H:%M:%S", time.localtime()) + f' could not connect to port\n')


def write_ser(data):
    if ser.is_open:
        try:
            ser.write(data.encode())
            text_order.insert('1.0', time.strftime("%H:%M:%S ", time.localtime()) + data + '\n')
        except serial.SerialException:
            text_order.insert('1.0',
                              time.strftime("%H:%M:%S", time.localtime()) + ' SerialException: write failed\n')

    print(data)


def tr_start(idx):
    serial_data = f"{{SIG_{testrack[idx].on_pin}_{start_on_time}_0_0}}"
    write_ser(serial_data)
    if ser.is_open:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' testrack ' + f"{idx + 1}" +
                          ' start' + '\n')


def tr_recovery(idx):
    serial_data = f"{{SIG_{testrack[idx].on_pin}_{recovery_on_time}_0_0}}"
    write_ser(serial_data)
    if ser.is_open:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' testrack ' + f"{idx + 1}" +
                          ' recover' + '\n')


def tr_reset(idx):
    serial_data = f"{{SIG_{testrack[idx].off_pin}_{reset_on_time}_0_0}}"
    write_ser(serial_data)
    if ser.is_open:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' testrack ' + f"{idx + 1}" +
                          ' reset' + '\n')


def tr_shutdown(idx):
    serial_data = f"{{SIG_{testrack[idx].off_pin}_{shutdown_on_time}_0_0}}"
    write_ser(serial_data)
    if ser.is_open:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' testrack ' + f"{idx + 1}" +
                          ' shut down' + '\n')


def gui_entries_update():
    testrack[0].set_settings('dummy', entry_tr1_speed.get(), entry_tr1_sig1_on.get(), entry_tr1_sig1_off.get(),
                             entry_tr1_sig2_on.get(), entry_tr1_sig2_off.get())
    testrack[1].set_settings('dummy', entry_tr2_speed.get(), entry_tr2_sig1_on.get(), entry_tr2_sig1_off.get(),
                             entry_tr2_sig2_on.get(), entry_tr2_sig2_off.get())
    sig_settings.update(combo_sig_pin.get(), entry_sig_on.get(), entry_sig_off.get(), combo_sig_unit.current())


def switch_tr_speed(idx):
    gui_entries_update()

    if idx == 0:
        btn = btn_tr1_speed
    else:
        btn = btn_tr2_speed

    speed = int(testrack[idx].speed)
    try:
        if speed > 4000:
            speed = 2000
        speed = 1000000 // (2 * 2 * speed)
    except ZeroDivisionError:
        speed = 0

    if speed > 0 and not testrack[idx].ktx_on:
        speed = str(speed)
        testrack[idx].ktx_on = 1
        btn.state(['pressed'])
        serial_data = f"{{SIG_{testrack[idx].ktx_pin}_{speed}_{speed}_1}}"
        write_ser(serial_data)
    elif testrack[idx].ktx_on:
        testrack[idx].ktx_on = 0
        btn.state(['!pressed'])
        serial_data = f"{{SIG_{testrack[idx].ktx_pin}_0_0_0}}"
        write_ser(serial_data)


def switch_tr_sig(idx, sig):
    gui_entries_update()
    if sig == 0:
        on_time = int(testrack[idx].on1)
        off_time = int(testrack[idx].off1)
        if idx == 0:
            btn = btn_tr1_sig1
        else:
            btn = btn_tr2_sig1
        pin = testrack[idx].sig1_pin
        is_on = testrack[idx].sig1_on
    else:
        on_time = int(testrack[idx].on2)
        off_time = int(testrack[idx].off2)
        if idx == 0:
            btn = btn_tr1_sig2
        else:
            btn = btn_tr2_sig2
        pin = testrack[idx].sig2_pin
        is_on = testrack[idx].sig2_on
    if on_time > 0 and not is_on:
        if sig == 0:
            testrack[idx].sig1_on = 1
        else:
            testrack[idx].sig2_on = 1
        btn.state(['pressed'])
        serial_data = f"{{SIG_{pin}_{on_time}_{off_time}_0}}"
        write_ser(serial_data)
    elif on_time:
        if sig == 0:
            testrack[idx].sig1_on = 0
        else:
            testrack[idx].sig2_on = 0
        btn.state(['!pressed'])
        serial_data = f"{{SIG_{pin}_0}}"
        write_ser(serial_data)


def tr_submit(idx):
    gui_entries_update()

    speed = int(testrack[idx].speed)
    on1 = int(testrack[idx].on1)
    on2 = int(testrack[idx].on2)

    if idx == 0:
        btn_speed = btn_tr1_speed
        btn_sig1 = btn_tr1_sig1
        btn_sig2 = btn_tr1_sig2
    else:
        btn_speed = btn_tr2_speed
        btn_sig1 = btn_tr2_sig1
        btn_sig2 = btn_tr2_sig2

    try:
        if speed > 4000:
            speed = 2000
        speed = 1000000 // (2 * 2 * speed)
    except ZeroDivisionError:
        speed = 0

    # if speed != testrack[idx].ktx_on and not testrack[idx].ktx_on:
    if speed and speed != testrack[idx].ktx_on:
        speed = str(speed)
        testrack[idx].ktx_on = speed
        btn_speed.state(['pressed'])
        serial_data = f"{{SIG_{testrack[idx].ktx_pin}_{speed}_{speed}_1}}"
        write_ser(serial_data)
    elif speed == 0 and testrack[idx].ktx_on:
        testrack[idx].ktx_on = speed
        btn_speed.state(['!pressed'])
        serial_data = f"{{SIG_{testrack[idx].ktx_pin}_0_0_0}}"
        write_ser(serial_data)

    if on1 > 0 and not testrack[idx].sig1_on:
        testrack[idx].sig1_on = 1
        btn_sig1.state(['pressed'])
        serial_data = f"{{SIG_{testrack[idx].sig1_pin}_{testrack[idx].on1}_{testrack[idx].off1}_0}}"
        write_ser(serial_data)
    elif on1 == 0 and testrack[idx].sig1_on:
        testrack[idx].sig1_on = 0
        btn_sig1.state(['!pressed'])
        serial_data = f"{{SIG_{testrack[idx].sig1_pin}_0}}"
        write_ser(serial_data)

    if on2 > 0 and not testrack[idx].sig2_on:
        testrack[idx].sig2_on = 1
        btn_sig2.state(['pressed'])
        serial_data = f"{{SIG_{testrack[idx].sig2_pin}_{testrack[idx].on2}_{testrack[idx].off2}_0}}"
        write_ser(serial_data)
    elif on2 == 0 and testrack[idx].sig2_on:
        testrack[idx].sig2_on = 0
        btn_sig2.state(['!pressed'])
        serial_data = f"{{SIG_{testrack[idx].sig2_pin}_0}}"
        write_ser(serial_data)


def sig_set(order):
    gui_entries_update()
    pin = sig_settings.pin
    if pin == '41':
        pin = '14'

    sig_set_err = 0

    if order == 1:
        if sig_settings.rand:
            serial_data = f"{{SIG_{pin}_RAND_{sig_settings.on}_{sig_settings.off}}}"
            if not int(sig_settings.on) * 3 < int(sig_settings.off):
                sig_set_err = 1
        else:
            serial_data = f"{{SIG_{pin}_{sig_settings.on}_{sig_settings.off}_{sig_settings.unit}}}"
    elif order == 2:
        serial_data = f"{{SIG_{pin}_{sig_settings.on}_0_{sig_settings.unit}}}"
        # switch_btn()
    else:
        serial_data = f"{{SIG_{pin}_0_0_0}}"
    if sig_set_err == 0:
        write_ser(serial_data)
    else:
        text_order.insert('1.0', 'RAND: lo must be hi * 3\n')


def create_grid_button(frm, txt, width, cmd, sticky, row, col, padx, pady, colspan):
    button = ttk.Button(frm, text=txt, command=cmd, width=width)
    button.grid(sticky=sticky, row=row, column=col, padx=padx, pady=pady, columnspan=colspan)
    return button


def create_button(frm, txt, width, cmd):
    return ttk.Button(frm, text=txt, command=cmd, width=width)


def restart_teensy():
    serial_data = '{RESET}'
    write_ser(serial_data)


def close_dialog():
    res = tkmsgbox.askyesno('teensySerial', 'Do you want to quit the program?')
    restart_teensy()
    if res:
        if ser.is_open:
            ser.close()
        root.destroy()


def check_connection():
    port_lst = serial.tools.list_ports.comports()
    try:
        for port_item in port_lst:
            if port_item.device == _port_device:
                root.after(2000, check_connection)
                break
        else:
            text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' serial connection lost\n')
            ser.close()
    except NameError:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' serial connection lost\n')
        ser.close()


def create_ini():
    global config_created
    new_ini = open('teensySerial.ini', "w")
    new_ini.write(default_ini)
    config_created = 1
    text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + f" {new_ini.name} created\n")


def open_ini():
    if config_success or config_created:
        subprocess.call(['notepad.exe', 'teensySerial.ini'])
    else:
        text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' no config file found\n')


def switch_rand():
    if not sig_settings.rand:
        sig_settings.rand = 1
        btn_sig_rand.state(['pressed'])
    else:
        sig_settings.rand = 0
        btn_sig_rand.state(['!pressed'])


config_file = 'teensySerial.ini'
config = configparser.ConfigParser(inline_comment_prefixes=";")
config.read(config_file)

testrack = [TestRackSetup('testrack 1', 25, 29, 32, 31, 34), TestRackSetup('testrack 2', 24, 28, 21, 22, 23)]

try:
    theme = config.get('general', 'theme')
    _port_device = config.get('general', 'port')
    auto_connect = config.get('general', 'auto_connect')
    testrack[0].set_settings(config.get('testrack1', 'id'), config.get('testrack1', 'speed'),
                             config.get('testrack1', 'sig1_on'), config.get('testrack1', 'sig1_off'),
                             config.get('testrack1', 'sig2_on'), config.get('testrack1', 'sig2_off'))
    testrack[1].set_settings(config.get('testrack2', 'id'), config.get('testrack2', 'speed'),
                             config.get('testrack2', 'sig1_on'), config.get('testrack2', 'sig1_off'),
                             config.get('testrack2', 'sig2_on'), config.get('testrack2', 'sig2_off'))

    sig_settings = SignalSetup(config.get('sig', 'pin'), config.get('sig', 'on'), config.get('sig', 'off'),
                               config.get('sig', 'unit'), config.get('sig', 'rand'))

    reset_on_time = config.get('reset', 'on_time')
    shutdown_on_time = config.get('shutdown', 'on_time')
    start_on_time = config.get('start', 'on_time')
    recovery_on_time = config.get('recovery', 'on_time')
    config_success = 1
except (configparser.NoSectionError, configparser.NoOptionError) as err:
    theme = 'yaru'
    _port_device = 'none'
    auto_connect = 0
    sig_settings = SignalSetup(32, 500, 500, 'ms', 0)
    reset_on_time = 2000
    shutdown_on_time = 10000
    start_on_time = 2000
    recovery_on_time = 16000
    config_success = 0

if theme == 'blue':
    text_order_bg = 'Slategray1'
    use_text_order_fg = 0
    text_order_fg = 0
elif theme == 'equilux':
    text_order_bg = 'grey35'
    text_order_fg = 'grey80'
    use_text_order_fg = 1
else:
    text_order_bg = 'grey90'
    use_text_order_fg = 0
    text_order_fg = 0

root = tk.Tk()
config_created = 0

style = ThemedStyle(root)
style.set_theme(theme)

root.title("teensySerial")
frame_master = ttk.Frame(root)
frame_left = ttk.Frame(frame_master)
frame_right = ttk.Frame(frame_master)
frame_com = ttk.Frame(frame_left)
frame_tr1 = ttk.Frame(frame_left)
frame_tr1_1 = ttk.Frame(frame_tr1)
frame_tr1_2 = ttk.Frame(frame_tr1)
frame_tr1_3 = ttk.Frame(frame_tr1)
frame_tr2 = ttk.Frame(frame_left)
frame_tr2_1 = ttk.Frame(frame_tr2)
frame_tr2_2 = ttk.Frame(frame_tr2)
frame_tr2_3 = ttk.Frame(frame_tr2)
frame_sig = ttk.Frame(frame_left)
frame_sig_1 = ttk.Frame(frame_sig)
frame_sig_2 = ttk.Frame(frame_sig)
frame_sig_3 = ttk.Frame(frame_sig)
frame_sreg = ttk.Frame(frame_left)

frame_right.configure(relief='ridge', borderwidth=1)
frame_com.configure(relief='ridge', borderwidth=1, width=1000)
frame_tr1.configure(relief='ridge', borderwidth=1)
frame_tr2.configure(relief='ridge', borderwidth=1)
frame_sig.configure(relief='ridge', borderwidth=1, width=1000)
frame_sreg.configure(relief='ridge', borderwidth=1, width=1000)

lbl_tr1 = ttk.Label(frame_tr1_1, text="testrack 1", font=(None, 12))
lbl_tr2 = ttk.Label(frame_tr2_1, text="testrack 2", font=(None, 12))

lbl_tr1_sig1_on = ttk.Label(frame_tr1_3, text="signal 1\non [ms]", font=(None, 8))
lbl_tr1_sig1_off = ttk.Label(frame_tr1_3, text="signal 1\noff [ms]", font=(None, 8))
lbl_tr1_sig2_on = ttk.Label(frame_tr1_3, text="signal 2\non [ms]", font=(None, 8))
lbl_tr1_sig2_off = ttk.Label(frame_tr1_3, text="signal 2\noff [ms]", font=(None, 8))
lbl_tr1_speed = ttk.Label(frame_tr1_3, text="speed\nmm/s", font=(None, 8))

lbl_tr2_sig1_on = ttk.Label(frame_tr2_3, text="signal 1\non [ms]", font=(None, 8))
lbl_tr2_sig1_off = ttk.Label(frame_tr2_3, text="signal 1\noff [ms]", font=(None, 8))
lbl_tr2_sig2_on = ttk.Label(frame_tr2_3, text="signal 2\non [ms]", font=(None, 8))
lbl_tr2_sig2_off = ttk.Label(frame_tr2_3, text="signal 2\noff [ms]", font=(None, 8))
lbl_tr2_speed = ttk.Label(frame_tr2_3, text="speed\nmm/s", font=(None, 8))

lbl_sig = ttk.Label(frame_sig_1, text="signal", font=(None, 12))
lbl_sig_pin = ttk.Label(frame_sig_2, text="pin", font=(None, 8))
lbl_sig_on = ttk.Label(frame_sig_2, text="on\n[ms]", font=(None, 8))
lbl_sig_off = ttk.Label(frame_sig_2, text="off\n[ms]", font=(None, 8))
lbl_sig_unit = ttk.Label(frame_sig_2, text="unit\n[us/ms]", font=(None, 8))
# lbl_sig_rand = ttk.Label(frame_sig_2, text="rand", font=(None, 8))

if use_text_order_fg:
    text_order = tk.Text(frame_right, height=34, width=45, fg=text_order_fg, bg=text_order_bg)
else:
    text_order = tk.Text(frame_right, height=34, width=45, bg=text_order_bg)

err_out = tk.Text(frame_com, width=20)

btn_connect = create_button(frame_com, "CONNECT", 10, connect_com)
combo_port = ttk.Combobox(frame_com, width=40, postcommand=get_com_port_list, state='readonly')

btn_tr1_start = create_button(frame_tr1_2, "start", 4, lambda: tr_start(0))
btn_tr1_reset = create_button(frame_tr1_2, "reset", 4, lambda: tr_reset(0))
btn_tr1_recovery = create_button(frame_tr1_2, "recovery", 8, lambda: tr_recovery(0))
btn_tr1_shutdown = create_button(frame_tr1_2, "shut down", 10, lambda: tr_shutdown(0))
btn_tr1_submit = create_button(frame_tr1_3, "submit", 7, lambda: tr_submit(0))

btn_tr2_start = create_button(frame_tr2_2, "start", 4, lambda: tr_start(1))
btn_tr2_reset = create_button(frame_tr2_2, "reset", 4, lambda: tr_reset(1))
btn_tr2_recovery = create_button(frame_tr2_2, "recovery", 8, lambda: tr_recovery(1))
btn_tr2_shutdown = create_button(frame_tr2_2, "shut down", 10, lambda: tr_shutdown(1))
btn_tr2_submit = create_button(frame_tr2_3, "submit", 7, lambda: tr_submit(1))

btn_sig_start = create_button(frame_sig_3, "start", 4, lambda: sig_set(1))
btn_sig_stop = create_button(frame_sig_3, "stop", 4, lambda: sig_set(0))
btn_sig_pulse = create_button(frame_sig_3, "pulse", 5, lambda: sig_set(2))

btn_create_ini = create_grid_button(frame_com, "create config", 12, create_ini, 'w', 1, 0, (2, 0), (0, 4), 1)
btn_open_ini = create_grid_button(frame_com, "open config", 12, open_ini, 'w', 1, 1, (2, 0), (0, 4), 1)
btn_restart_teensy = create_grid_button(frame_com, "restart teensy", 12, restart_teensy, 'w', 1, 2, (2, 4), (0, 4), 1)

entry_tr1_speed = ttk.Entry(frame_tr1_3, width=6)
entry_tr1_sig1_on = ttk.Entry(frame_tr1_3, width=6)
entry_tr1_sig1_off = ttk.Entry(frame_tr1_3, width=6)
entry_tr1_sig2_on = ttk.Entry(frame_tr1_3, width=6)
entry_tr1_sig2_off = ttk.Entry(frame_tr1_3, width=6)

btn_tr1_speed = create_grid_button(frame_tr1_3, "ktx", 6, lambda: switch_tr_speed(0), 'w', 4, 0, (2, 0), (4, 4), 1)
btn_tr1_sig1 = create_grid_button(frame_tr1_3, "sig1 active", 10, lambda: switch_tr_sig(0, 0), '', 4, 1, (2, 0), (4, 4),
                                  2)
btn_tr1_sig2 = create_grid_button(frame_tr1_3, "sig2 active", 10, lambda: switch_tr_sig(0, 1), '', 4, 3, (2, 0), (4, 4),
                                  2)

btn_tr2_speed = create_grid_button(frame_tr2_3, "ktx", 6, lambda: switch_tr_speed(1), 'w', 4, 0, (2, 0), (4, 4), 1)
btn_tr2_sig1 = create_grid_button(frame_tr2_3, "sig1 active", 10, lambda: switch_tr_sig(1, 0), '', 4, 1, (2, 0), (4, 4),
                                  2)
btn_tr2_sig2 = create_grid_button(frame_tr2_3, "sig2 active", 10, lambda: switch_tr_sig(1, 1), '', 4, 3, (2, 0), (4, 4),
                                  2)

entry_tr2_id = ttk.Entry(frame_tr2, width=10)
entry_tr2_speed = ttk.Entry(frame_tr2_3, width=6)
entry_tr2_sig1_on = ttk.Entry(frame_tr2_3, width=6)
entry_tr2_sig1_off = ttk.Entry(frame_tr2_3, width=6)
entry_tr2_sig2_on = ttk.Entry(frame_tr2_3, width=6)
entry_tr2_sig2_off = ttk.Entry(frame_tr2_3, width=6)

entry_sig_on = ttk.Entry(frame_sig_2, width=6)
entry_sig_off = ttk.Entry(frame_sig_2, width=6)
# entry_sig_rand = ttk.Entry(frame_sig_2, width=6)
btn_sig_rand = create_button(frame_sig_2, "rand", 6, switch_rand)

if sig_settings.rand:
    btn_sig_rand.state(['pressed'])

combo_sig_unit = ttk.Combobox(frame_sig_2, values=('ms', 'us'), width=7, state='readonly')
combo_sig_pin = ttk.Combobox(frame_sig_2, values=pins, width=4, state='readonly')

lst = serial.tools.list_ports.comports()
try:
    for item in lst:
        if item.device == _port_device:
            combo_port.set(item)
            break
    else:
        combo_port.set('Choose COM port')
except NameError:
    combo_port.set('Choose COM port')
ser = serial.Serial()

lbl_tr1.config(text=testrack[0].name)
entry_tr1_speed.insert(0, testrack[0].speed)
entry_tr1_sig1_on.insert(0, testrack[0].on1)
entry_tr1_sig1_off.insert(0, testrack[0].off1)
entry_tr1_sig2_on.insert(0, testrack[0].on2)
entry_tr1_sig2_off.insert(0, testrack[0].off2)

lbl_tr2.config(text=testrack[1].name)
entry_tr2_speed.insert(0, testrack[1].speed)
entry_tr2_sig1_on.insert(0, testrack[1].on1)
entry_tr2_sig1_off.insert(0, testrack[1].off1)
entry_tr2_sig2_on.insert(0, testrack[1].on2)
entry_tr2_sig2_off.insert(0, testrack[1].off2)

entry_sig_on.insert(0, sig_settings.on)
entry_sig_off.insert(0, sig_settings.off)
combo_sig_pin.set(sig_settings.pin)
combo_sig_unit.set(sig_settings.unit)
# entry_sig_rand.insert(0, sig_settings.rand)

combo_port.grid(sticky='w', row=0, column=0, padx=2, pady=3, columnspan=3)
btn_connect.grid(row=0, column=3, padx=5)
frame_com.grid(sticky='w', row=0, column=0, padx=2, pady=2)
# print(frame_com.winfo_width())

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

lbl_tr1_speed.grid(sticky='w', row=2, column=0, padx=2, pady=(5, 0))
entry_tr1_speed.grid(row=3, column=0, padx=2)
lbl_tr1_sig1_on.grid(sticky='w', row=2, column=1, padx=2, pady=(5, 0))
entry_tr1_sig1_on.grid(row=3, column=1, padx=2)
lbl_tr1_sig1_off.grid(sticky='w', row=2, column=2, padx=2, pady=(5, 0))
entry_tr1_sig1_off.grid(sticky='w', row=3, column=2, padx=2)
lbl_tr1_sig2_on.grid(sticky='w', row=2, column=3, padx=2, pady=(5, 0))
entry_tr1_sig2_on.grid(row=3, column=3, padx=2)
lbl_tr1_sig2_off.grid(sticky='w', row=2, column=4, padx=2, pady=(5, 0))
entry_tr1_sig2_off.grid(sticky='w', row=3, column=4, padx=2)

lbl_tr2_speed.grid(sticky='w', row=2, column=0, padx=2, pady=(5, 0))
entry_tr2_speed.grid(row=3, column=0, padx=2)
lbl_tr2_sig1_on.grid(sticky='w', row=2, column=1, padx=2, pady=(5, 0))
entry_tr2_sig1_on.grid(row=3, column=1, padx=2)
lbl_tr2_sig1_off.grid(sticky='w', row=2, column=2, padx=2, pady=(5, 0))
entry_tr2_sig1_off.grid(sticky='w', row=3, column=2, padx=2)
lbl_tr2_sig2_on.grid(sticky='w', row=2, column=3, padx=2, pady=(5, 0))
entry_tr2_sig2_on.grid(row=3, column=3, padx=2)
lbl_tr2_sig2_off.grid(sticky='w', row=2, column=4, padx=2, pady=(5, 0))
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
# lbl_sig_rand.grid(sticky='w', row=0, column=4, padx=2)

entry_sig_on.grid(sticky='w', row=1, column=1, padx=2)
entry_sig_off.grid(sticky='w', row=1, column=2, padx=2)
# entry_sig_rand.grid(sticky='w', row=1, column=4, padx=2)
btn_sig_rand.grid(sticky='w', row=1, column=4, padx=(2, 5))

combo_sig_pin.grid(sticky='w', row=1, column=0, padx=2)
combo_sig_unit.grid(sticky='w', row=1, column=3, padx=2)

btn_sig_start.grid(row=0, column=0, padx=2)
btn_sig_stop.grid(row=0, column=1, padx=2)
btn_sig_pulse.grid(row=0, column=2, padx=2)

frame_sig_1.grid(sticky='w', row=0, column=0)
frame_sig_2.grid(sticky='w', row=1, column=0)
frame_sig_3.grid(sticky='w', row=2, column=0, pady=5)
frame_sig.grid(sticky='w', row=3, column=0, padx=2, pady=5)

frame_left.grid(sticky='nw', row=0, column=0, padx=2, pady=5)

text_order.grid(sticky='w', row=0, column=0, padx=5, pady=4)
frame_right.grid(sticky='w', row=0, column=1, padx=0, pady=5)

frame_master.grid()

text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + f' mode: {board}\n')

if config_success:
    text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + f" {config_file} processed\n")
else:
    text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' no config file found\n')

if check_port(_port_device, '') and auto_connect == 'on':
    connect_com()
else:
    text_order.insert('1.0', time.strftime("%H:%M:%S", time.localtime()) + ' cannot connect to port / no port\n')

root.protocol("WM_DELETE_WINDOW", close_dialog)

try:
    root.mainloop()
except KeyboardInterrupt:
    print('process quit')
    pass
