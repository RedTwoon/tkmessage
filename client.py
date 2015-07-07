import socket
from tkui import *
from message import Message

class Client(tkWindow):
    def __init__(self, master):
        tkWindow.__init__(self, master)
        self.server_IP = LOCALHOST
        self.receiver = None
        self.user_name = None
        self.sessions = {}

    def connect_to_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.server_IP, int(self.port)))

    def get_information(self):
        self.class_ = CLIENT
        p_entry, p_label = self.make_port_entry()
        ip_entry = tk.Entry(self.master)
        ip_entry.insert(0, self.server_IP)
        ip_label = tk.Label(self.master, text='Server IP')
        n_entry = tk.Entry(self.master)
        n_label = tk.Label(self.master, text='User Name')
        n_entry.insert(0, DEFAULT_USERNAME)
        submit = tk.Button(self.master, text='Submit',
                           command=lambda: Client.setup(self, p_entry.get(),
                                                        ip_entry.get(),
                                                        n_entry.get()))
        self.append(p_entry, p_label, ip_entry, ip_label,
                    n_entry, n_label, submit)
        simple_grid(p_label, p_entry, ip_label, ip_entry,
                    n_label, n_entry, submit)

    def failed_to_connect(self):
        e = tk.Button(self.master, text='Failed to Connect',
                      command=lambda: e.destroy())
        self.append(e)
        e.grid()

    def setup(self, port, ip, user_name):
        self.port = port
        self.server_IP = ip
        self.user_name = user_name
        try:
            self.connect_to_server()
        except Exception as error:
            self.failed_to_connect()
            raise error
        else:
            self.destroy_widgets()
            thread = thr.Thread(target=self.receive_messages)
            thread.start()
            self.messenger()

    def messenger(self):
        self.make_message_box()
        m_entry, m_button = self.make_message_entry()
        r_entry, r_button = self.change_receivers()
        self.message_box.grid(row=0, column=0, columnspan=3)
        m_entry.grid(row=1, column=0, columnspan=3)
        r_button.grid(row=2, column=0)
        r_entry.grid(row=2, column=1)
        m_button.grid(row=2, column=2)
        self.display_time()
        self.send_message(args=JOIN_SERVER)
        self.append(m_entry, m_button, r_entry, r_button)

    def change_receivers(self):
        entry = tk.Entry(self.master)
        button = tk.Button(self.master, text='Recipient UserName:',
                           command=lambda: self.change_receiver(entry.get()))
        return entry, button

    def change_receiver(self, receiver):
        self.sessions[self.receiver] = self.message_box.get(1.0, tk.END)
        self.message_box.delete(1.0, tk.END)
        self.receiver = receiver
        if self.receiver in self.sessions:
            self.message_box.insert(tk.END, self.sessions[self.receiver])

    def receive_messages(self):
        in_ = self.server.recv(BUFFER)
        m = Message(in_)
        if m.args == EXIT:
            self.display_message('Server has been closed.')
            self.leave_server()
        else:
            if self.current_side != LEFT:
                log = '%s [%s]' % (m.sender, strftime('%I:%M%p').lower())
                self.display_message(log, side=LEFT)
            self.display_message(' > %s' % m.message, side=LEFT)
            self.current_side = LEFT

        if self.running:
            self.receive_messages()

    def send_message(self, entry=None, args=None):
        if entry:
            message = entry.get(1.0, tk.END)
            entry.delete(1.0, tk.END)
            print(str.encode(message))
        else:
            message=None
        m = Message(message=message,
                    sender=self.user_name,
                    receiver=self.receiver,
                    args=args)
        if self.message_box and m.message:
            if self.current_side != RIGHT:
                log = '[%s] %s' % (strftime('%I:%M%p').lower(), self.user_name)
                self.display_message(log, side=RIGHT)
            self.display_message('%s < ' % m.message, side=RIGHT)
            self.current_side = RIGHT
        self.server.send(m.encoded)

    def leave_server(self, server=False):
        if server:
            self.send_messages(args=EXIT)
        self.server.close()
        self.running = False


if __name__ == '__main__':
    pass
