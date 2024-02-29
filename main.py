import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.validation import add_numeric_validation, add_range_validation
from ttkbootstrap.style import Bootstyle
from ttkbootstrap.toast import ToastNotification
from PIL import Image
import random
import string

Image.CUBIC = Image.BICUBIC


class CollapsingFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.cumulative_rows = 0
        self.images = [
            ttk.PhotoImage(file='icon0.png'),
            ttk.PhotoImage(file='icon1.png')
        ]

    def add(self, child, title="", bootstyle=PRIMARY, **kwargs):
        if child.winfo_class() != 'TFrame':
            return

        style_color = Bootstyle.ttkstyle_widget_color(bootstyle)
        frm = ttk.Frame(self, bootstyle=style_color)
        frm.grid(row=self.cumulative_rows, column=0, sticky=EW)

        header = ttk.Label(
            master=frm,
            text=title,
            bootstyle=(style_color, INVERSE)
        )
        if kwargs.get('textvariable'):
            header.configure(textvariable=kwargs.get('textvariable'))
        header.pack(side=LEFT, fill=BOTH, padx=10)

        def _func(c=child): return self._toggle_open_close(c)
        btn = ttk.Button(
            master=frm,
            image=self.images[0],
            bootstyle=style_color,
            command=_func
        )
        btn.pack(side=RIGHT)

        child.btn = btn
        child.grid(row=self.cumulative_rows + 1, column=0, sticky=NSEW)
        self.cumulative_rows += 2

    def _toggle_open_close(self, child):
        if child.winfo_viewable():
            child.grid_remove()
            child.btn.configure(image=self.images[1])
        else:
            child.grid()
            child.btn.configure(image=self.images[0])


class Container(ttk.Frame):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.volume = None
        self.generatedPassword = None
        self.result=None
        self.pack(fill=BOTH, expand=YES, pady=10, padx=15)
        self.passwordLength = ttk.IntVar(value=8)
        self.digits = ttk.BooleanVar(value=True)
        self.alphabet = ttk.BooleanVar(value=True)
        self.characters = ttk.BooleanVar(value=False)
        self.colors = mainWindow.style.colors
        passwordLengthInputContainer = ttk.Frame(self)
        passwordLengthInputContainer.pack(
            fill=X, expand=YES, pady=[10,30])
        passwordLengthLabel = ttk.Label(
            passwordLengthInputContainer, text='Password Length:', width=15)
        passwordLengthLabel.pack(side=LEFT, padx=15)
        passwordLengthInput = ttk.Spinbox(
            master=passwordLengthInputContainer, textvariable=self.passwordLength, from_=5, to=20)
        passwordLengthInput.pack(side=LEFT, fill=X, padx=15)
        add_numeric_validation(passwordLengthInput, when='all')
        add_range_validation(passwordLengthInput, startrange=self.passwordLength.get(
        ), endrange=20, when='all')
        cf = CollapsingFrame(self)
        cf.pack(fill=BOTH)
        options = ttk.Frame(cf, padding=10)
        ttk.Checkbutton(options, text=f'digits', variable=self.digits, bootstyle="round-toggle").pack(
            fill=X, pady=5)
        ttk.Checkbutton(options, text=f'alphabet', variable=self.alphabet, bootstyle="round-toggle").pack(
            fill=X, pady=5)
        ttk.Checkbutton(options, text=f'characters', variable=self.characters, bootstyle="round-toggle").pack(
            fill=X, pady=5)
        cf.add(child=options, title='Options')
        buttonContainer = ttk.Frame(self)
        buttonContainer.pack(fill=X, expand=YES, pady=[20, 15])
        generateBtn = ttk.Button(master=buttonContainer,
                                 text='Generate', command=self.generate, bootstyle="info-outline", width=10)
        generateBtn.pack()
        ttk.Separator(master=self, bootstyle="danger").pack(fill=X)

    def createVolume(self, value):
        style = None
        if value < 100 and value > 75:
            style = LIGHT
        elif value <= 75 and value > 50:
            style = WARNING
        elif value <= 50:
            style = DANGER
        else:
            style = SUCCESS
        volume = ttk.Meter(master=self.result, metersize=150, padding=5, amounttotal=100, amountused=value,
                           subtext='Secure Score in %', interactive=False, bootstyle=style)
        volume.pack()
        return volume

    def generatePaassword(self):
        options = ''
        if self.digits.get():
            options += string.digits
        if self.alphabet.get():
            options += string.ascii_letters
        if self.characters.get():
            options += string.punctuation

        length = self.passwordLength.get()
        password = ''.join(random.choice(options) for _ in range(length))
        return password

    def securityScore(self, password):
        length_weight = 0.3
        complexity_weight = 0.7

        lowercase_letters = set(string.ascii_lowercase)
        uppercase_letters = set(string.ascii_uppercase)
        digits = set(string.digits)
        symbols = set(string.punctuation)

        has_lowercase = any(char in lowercase_letters for char in password)
        has_uppercase = any(char in uppercase_letters for char in password)
        has_digits = any(char in digits for char in password)
        has_symbols = any(char in symbols for char in password)

        length_score = min(len(password) / 20, 1) if len(password) <= 20 else 1

        complexity = (has_lowercase + has_uppercase + has_digits + has_symbols) / 4

        strength = (length_weight * length_score + complexity_weight * complexity) * 100
        if min(strength, 100) != 100:
            strength = int(str(min(strength, 100))[:2])
        else:
            strength = 100
        return strength

    def validateOptions(self):
        return self.digits.get() or self.alphabet.get() or self.characters.get()
    def copy_password(self):
        self.clipboard_clear()
        self.clipboard_append(self.generatedPassword.cget("text"))
        self.update()
        notif = ToastNotification(
            title='Copied!', message='Password copied to clipboard.', duration=2000, bootstyle=INFO, position=[200, 100, 'n'])
        notif.show_toast()
    def generate(self):
        if not self.validateOptions():
            notif = ToastNotification(title='Caution!', message='At least one option must be selected.', duration=5000, bootstyle=WARNING, alert=True, position=[200, 100, 'n'])
            notif.show_toast()
            return
        if self.result:self.result.destroy()
        self.result=ttk.Frame(self)
        self.result.pack(pady=[10,20],expand=YES,fill=X)
        password = self.generatePaassword()
        self.generatedPassword = ttk.Label(self.result, text=password)
        self.generatedPassword.pack(pady=[20, 20])
        self.copyBtn = ttk.Button(master=self.result,
                             text='Copy', command=self.copy_password, bootstyle="light-outline", width=10)
        self.copyBtn.pack(pady=4)
        self.volume = self.createVolume(self.securityScore(password))
        notif = ToastNotification(
            title='Generated!', message='Password Generated.', duration=2000, bootstyle=SUCCESS, position=[200, 100, 'n'])
        notif.show_toast()
if __name__ == '__main__':
    root = ttk.Window(title='Password Generator', themename='solar', resizable=[False, False])
    root.eval('tk::PlaceWindow . center')
    Container(root)
    root.mainloop()
