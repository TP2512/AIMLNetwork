import logging
import ldap3
from tkinter import *
from PIL import Image, ImageTk
import threading

""" 
In this py file have 1 class
    - LogInApplicationClass
"""


class LogInApplicationClass:
    """ This class ("LogInApplicationClass") responsible for login users to applications """
    """ To use with this function, need to call the "login_fronted" function """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def authentication(self, window_main, domain_name, server_ip, user_domain, password_domain):
        """
        This function responsible to create authentication

        The function get 5 parameter:
            - "window_main" - the TK root of Tkinter
            - "domain_name" - the domain name (string type)
            - "server_ip" - the server ip (string type)
            - "user_domain" - the domain user (string type)
            - "password_domain" - the domain password (string type)

        The function return 1 parameters:
            - "res" - pass or fail authentication
        """

        global signature1
        res = None
        try:
            user = user_domain + domain_name
            password = password_domain
            server = ldap3.Server(server_ip)
            connection = ldap3.Connection(server, user=user, password=password)
            res = connection.bind()
            if not res:
                signature1.after(1, signature1.destroy)
                signature1 = Label(window_main, text="The Username or Password is incorrect",
                                   font="Verdana 10 underline")
                signature1.grid(row=50, column=7, columnspan=3)
        except Exception:
            self.logger.exception('')
            signature1.after(1, signature1.destroy)
            signature1 = Label(window_main, text="The Username or Password is incorrect", font="Verdana 10 underline")
            signature1.grid(row=50, column=7, columnspan=3)
        return res

    def open_application(self, access_flag, window_main, domain_name, server_ip, e_user_name_label, e_password_label, v_guest,
                         v_admin,
                         username_guest_list, password_guest_value):
        """
        This function responsible for deciding whether to open the application and in what mode

        The function get 10 parameter:
            - "access_flag" - flag for running the application
            - "window_main" - the TK root of Tkinter
            - "domain_name" - the domain name (string type)
            - "server_ip" - the server ip (string type)
            - "e_user_name_label" - the username - is received from the user (gui) (string type)
            - "e_password_label" - the password - is received from the user (gui) (string type)
            - "v_guest" - the relevant guest mode - is received from the user (gui) (string type)
            - "v_admin" - the relevant admin mode - is received from the user (gui) (string type)
            - "username_guest_list" - admin username value (string or list type)
            - "password_guest_value" - admin password value (string type)

        The function return 0 parameters:
        """

        global signature1
        global guest_mode
        global admin_mode
        global user_gui
        global password_gui
        if v_guest.get() == 1:  # guest mode
            user_guest_gui = str(e_user_name_label.get())
            password_guest_gui = str(e_password_label.get())
            guest_mode = 1
            if user_guest_gui in username_guest_list and password_guest_gui in password_guest_value:
                if v_admin.get() == 1:
                    guest_username_admin_list = ['Administrator']
                    guest_password_admin_list = 'EZ210892Life'
                    if user_guest_gui in guest_username_admin_list and password_guest_gui in guest_password_admin_list:
                        admin_mode = 1
                    else:
                        signature1.after(1, signature1.destroy)
                        signature1 = Label(window_main, text="The username is not an administrator\nplease try again",
                                           font="Verdana 10 underline")
                        signature1.grid(row=50, column=7, columnspan=3)
                        return
                else:
                    admin_mode = 0
                try:
                    window_main.destroy()  # close window login
                    access_flag.set()
                    user_gui = user_guest_gui
                    password_gui = password_guest_gui
                    # DatabaseClass.database_creator(user_guest_gui, password_guest_gui, guest_mode, admin_mode)
                except Exception:
                    self.logger.exception('')
            else:
                signature1.after(1, signature1.destroy)
                signature1 = Label(window_main, text="The Username or Password is incorrect",
                                   font="Verdana 10 underline")
                signature1.grid(row=50, column=7, columnspan=3)
        if v_guest.get() == 0:  # domain mode
            user_domain = str(e_user_name_label.get())
            password_domain = str(e_password_label.get())
            guest_mode = 0
            if v_admin.get() == 1:
                admin_list = ['azaguri']
                admin_mode = 1 if user_domain in admin_list else 0
            else:
                admin_mode = 0
            if LogInApplicationClass().authentication(window_main, domain_name, server_ip, user_domain, password_domain):
                try:
                    window_main.destroy()  # close window login
                    access_flag.set()
                    user_gui = user_domain
                    password_gui = password_domain
                    # DatabaseClass.database_creator(user_domain, password_domain, guest_mode, admin_mode)
                except Exception:
                    self.logger.exception('')

    def activate_guest(self, v_guest):
        if v_guest.get() == 1:
            self.logger.info("ACTIVE guest")
        elif v_guest.get() == 0:
            self.logger.info("DISABLED guest")

    def activate_admin(self, v_admin):
        if v_admin.get() == 1:
            self.logger.info("ACTIVE admin")
        elif v_admin.get() == 0:
            self.logger.info("DISABLED admin")

    def login_fronted(self, access_flag, domain_name, server_ip, username_guest='', password_guest='',
                      icon_path=None, img_path=None):
        """
        This function responsible for deciding whether to open the application and in what mode

        The function get 8 parameter:
            - "access_flag" - flag for running the application
            - "domain_name" - the domain name (string type) {Airspan domain name = @airspan.com}
            - "server_ip" - the server ip (string type) {Airspan server ip = 10.3.10.5:3268}
            - "username_guest" - admin username value (string or list type)
            - "password_guest" - admin password value (string type)
            - "icon_path" - the path to icon of the Log-in application (string type) [Optional]
            - "img_path" - the path to image of the Log-in application (string type) [Optional]

        The function return 4 parameters:
            - "user_gui" - the username that came from the GUI (from the user) (string type)
            - "password_gui" - the password that came from the GUI (from the user) (string type)
            - "guest_mode" - the "guest" mode allows login with local username and password - came from the GUI (from
              the user selection) (integer type)
                * 0 = not guest
                * 1 = guest
            - "admin_mode" - the "admin" mode allows login as administrator -  came from the GUI (from the user
              selection) (integer type)
                * 0 = not admin
                * 1 = admin

        How to call this function and open the application:
            - create access_flag:
                access_flag = threading.Event()

            - call the "login_fronted" function:
                user_gui, password_gui, guest_mode, admin_mode = LogInApplicationClass().login_fronted(access_flag,
                                                                                                     domain_name_,
                                                                                                     server_ip_,
                                                                                                     username_guest_,
                                                                                                     password_guest_,
                                                                                                     icon_path_,
                                                                                                     img_path_)

        - call the specific function:
            if access_flag.isSet():
                print("xxx")
                print(guest_mode)
                print(admin_mode)
                className.function_name(user_gui, password_gui, guest_mode, admin_mode)
            else:
                print("Exit from the "login_fronted" application")
        """

        def on_close():
            """ This function responsible close the window and exit from the loop ("while True:") """

            close_app.set()
            window_main.destroy()

        global close_app
        close_app = threading.Event()

        while True:
            global signature1

            window_main = Tk()
            try:
                window_main.iconbitmap(icon_path)
            except Exception:
                self.logger.exception('')

            window_main.title("Log-in")

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=0, column=0)

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=0, column=1)

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=0, column=2)

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=0, column=3)

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=0, column=4)

            user_name_label = Label(window_main, text='UserName:')
            user_name_label.grid(row=5, column=7, columnspan=3)

            password_label = Label(window_main, text='Password:')
            password_label.grid(row=7, column=7, columnspan=3)

            e_user_name_label = Entry(window_main, textvariable=StringVar())
            e_user_name_label.grid(row=6, column=7, columnspan=3)

            e_password_label = Entry(window_main, show='*', textvariable=StringVar())
            e_password_label.grid(row=8, column=7, columnspan=3)

            try:
                img = ImageTk.PhotoImage(Image.open(img_path))
                l13img = Label(window_main, image=img)
                l13img.grid(row=52, column=7, columnspan=3)
                b1 = Button(window_main, text='Log-in',
                            command=lambda: LogInApplicationClass().open_application(access_flag, window_main,
                                                                                     domain_name, server_ip,
                                                                                     e_user_name_label, e_password_label,
                                                                                     v_guest, v_admin,
                                                                                     username_guest, password_guest))
                b1.grid(row=10, column=7, columnspan=3)

                g_space_label = Label(window_main, text=' ')
                g_space_label.grid(row=10, column=8)

                v_guest = IntVar(window_main)
                guest_check = Checkbutton(window_main, text="Guest", variable=v_guest,
                                          command=lambda: LogInApplicationClass().activate_guest(v_guest))
                guest_check.grid(row=10, column=9, sticky=W)

                g_space_label = Label(window_main, text='                                                             ')
                g_space_label.grid(row=11, column=8)

                v_admin = IntVar(window_main)
                admin_check = Checkbutton(window_main, text="Administrator", variable=v_admin,
                                          command=lambda: LogInApplicationClass().activate_admin(v_admin))
                admin_check.grid(row=11, column=9, sticky=W)
            except Exception:
                self.logger.exception('')
                img = None
                b1 = Button(window_main, text='Log-in',
                            command=lambda: LogInApplicationClass().open_application(access_flag, window_main,
                                                                                     domain_name, server_ip,
                                                                                     e_user_name_label, e_password_label,
                                                                                     v_guest, v_admin,
                                                                                     username_guest, password_guest))
                b1.grid(row=10, column=7, columnspan=3)
                # b1.grid(row=10, column=8, columnspan=1)
                v_guest = IntVar(window_main)
                guest_check = Checkbutton(window_main, text="Guest", variable=v_guest,
                                          command=lambda: LogInApplicationClass().activate_guest(v_guest))
                guest_check.grid(row=10, column=9, sticky=W)
                # guest_check.grid(row=10, column=10)

                #

                g_space_label = Label(window_main, text='                                                             ')
                g_space_label.grid(row=11, column=8)

                v_admin = IntVar(window_main)
                admin_check = Checkbutton(window_main, text="Administrator", variable=v_admin,
                                          command=lambda: LogInApplicationClass().activate_admin(v_admin))
                admin_check.grid(row=11, column=9, sticky=W)
                #
            ##

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=51, column=5, columnspan=3)

            g_space_label = Label(window_main, text=' ')
            g_space_label.grid(row=53, column=5, columnspan=3)

            # signature1 = Label(window_main, text="", font="Verdana 10 underline")
            signature1 = Label(window_main, text="                                                     ",
                               font="Verdana 10")
            signature1.grid(row=50, column=7, columnspan=3)
            window_main.bind('<Return>',
                             lambda event: LogInApplicationClass().open_application(access_flag, window_main, domain_name,
                                                                                    server_ip, e_user_name_label,
                                                                                    e_password_label, v_guest, v_admin,
                                                                                    username_guest,
                                                                                    password_guest))  # press enter key

            """ Center screen """
            w = user_name_label.winfo_reqwidth()
            h = user_name_label.winfo_reqheight()
            ws = window_main.winfo_screenwidth()
            hs = window_main.winfo_screenheight()
            x = (ws / 2) - (w / 2)
            y = (hs / 2) - (h / 2)
            # print(w, h, x, y)
            window_main.geometry('%dx%d+%d+%d' % (w, h, x, y))

            if img:
                window_main.wm_geometry("410x410")
            else:
                window_main.wm_geometry("480x200")
            window_main.attributes('-topmost', 'true')  # put the login screen on top
            window_main.protocol("WM_DELETE_WINDOW", on_close)
            window_main.mainloop()

            if access_flag.isSet():
                return user_gui, password_gui, guest_mode, admin_mode
            else:
                # return None, None, None, None
                pass
            if close_app.isSet():
                return None, None, None, None
            else:
                pass
