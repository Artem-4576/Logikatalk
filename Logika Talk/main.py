import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.label = None
        self.entry = None
        self.save_button = None

        # меню
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=5, y=5)

        # чат
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disabled')
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.username = 'Artem'
        self.sock = None
        self.connect_to_server()

        self.adaptive_ui()

    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"[SYSTEM] Не вдалося підключитися до сервера: {e}")

    def toggle_show_menu(self):
        self.is_show_menu = not self.is_show_menu
        self.speed_animate_menu *= -1
        self.btn.configure(text='◀️' if self.is_show_menu else '▶️')
        self.show_menu()

        if self.is_show_menu:
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()
            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_username)
            self.save_button.pack(pady=10)

    def save_username(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"[SYSTEM] Ім’я змінено на {self.username}")

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if self.is_show_menu and self.menu_frame.winfo_width() < 200:
            self.after(10, self.show_menu)
        elif not self.is_show_menu and self.menu_frame.winfo_width() > 40:
            self.after(10, self.show_menu)
        elif not self.is_show_menu:
            if self.label:
                self.label.destroy()
                self.label = None
            if self.entry:
                self.entry.destroy()
                self.entry = None
            if self.save_button:
                self.save_button.destroy()
                self.save_button = None

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        self.after(50, self.adaptive_ui)

    def add_message(self, text, is_self=False):
        self.chat_field.configure(state='normal')
        prefix = "Я: " if is_self else ""
        self.chat_field.insert(END, prefix + text + '\n')
        self.chat_field.see(END)
        self.chat_field.configure(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}", is_self=True)
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_message("[SYSTEM] Помилка відправлення повідомлення.")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise ConnectionError("Зʼєднання закрите сервером.")
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except Exception as e:
                self.add_message(f"[SYSTEM] Зʼєднання втрачено: {e}")
                break
        if self.sock:
            self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                if author != self.username:
                    self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)


win = MainWindow()
win.mainloop()
