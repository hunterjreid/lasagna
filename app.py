import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import ctypes
import math
import re
import secrets
import string


# ---------------------------
# Password evaluation helpers
# ---------------------------

SAFE_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb: tuple) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"

def _brightness(rgb: tuple) -> float:
    r, g, b = rgb
    return (r * 299 + g * 587 + b * 114) / 1000.0

def _best_text_color(bg_hex: str) -> str:
    br = _brightness(_hex_to_rgb(bg_hex))
    return "#000000" if br >= 128 else "#ffffff"

def _shade(hex_color: str, amount: float) -> str:
    # amount: -1.0..1.0 negative=darken, positive=lighten
    r, g, b = _hex_to_rgb(hex_color)
    if amount >= 0:
        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)
    else:
        amt = 1 + amount
        r = int(r * amt)
        g = int(g * amt)
        b = int(b * amt)
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return _rgb_to_hex((r, g, b))

COMMON_PASSWORDS = {
    "123456","password","123456789","12345","12345678","qwerty","1234567","111111","123123",
    "abc123","password1","1234","iloveyou","000000","qwerty123","1q2w3e4r","admin","letmein",
    "welcome","monkey","dragon","football","baseball","sunshine","princess","qwertyuiop","login",
    "starwars","hello","freedom","whatever","qazwsx","trustno1","password123","zaq12wsx","asdfghjkl",
    "passw0rd","pokemon","michael","superman","batman","charlie","shadow","killer","mustang","jordan",
    "harley","hunter","hannah","secret","master","flower","lovely","ginger","letmein1","test1234"
}

COMMON_WORDS = {
    "password","qwerty","admin","welcome","login","dragon","sunshine","monkey","football","baseball",
    "princess","iloveyou","letmein","secret","master","shadow","killer","summer","winter","autumn",
    "spring","flower","ginger","hannah","pokemon","superman","batman","starwars","computer","internet",
    "music","guitar","soccer","basketball","hockey","jordan","harley","mustang","chevy","ford","nissan",
    "toyota","apple","orange","banana","grape","coffee","chocolate","cookie","pepper","storm","thunder",
    "welcome1","admin1","hello","freedom","trust","whatever","qazwsx","asdf","zxcv","zaq","iloveu"
}

PASSPHRASE_WORDS = [
    "able","acid","aged","also","area","army","away","baby","back","ball","band","bank","base",
    "bath","bear","beat","been","beer","bell","belt","best","bill","bird","blow","blue","boat",
    "body","bomb","bond","bone","book","boom","born","both","bowl","bulk","burn","bush","busy",
    "cake","call","calm","came","camp","card","care","case","cash","cast","chat","chip","city",
    "club","coal","coat","code","cold","come","cook","cool","cope","copy","core","cost","crew",
    "crop","dark","data","date","dawn","days","dead","deal","dear","debt","deep","deny","desk",
    "dial","diet","dish","disk","dive","doll","door","dose","down","draw","dust","duty","each",
    "earn","ease","east","edge","else","even","ever","face","fact","fail","fair","fall","farm",
    "fast","fate","fear","feed","feel","file","fill","find","fine","fire","fish","five","flat",
    "flow","food","foot","form","fort","four","free","from","fuel","full","fund","game","gate",
    "gear","gift","girl","give","glad","goal","goes","gold","golf","gone","good","gray","grew",
    "grow","gulf","hair","half","hall","hand","hang","hard","harm","hate","have","head","hear",
    "heat","held","help","here","hero","high","hill","hire","hold","hole","holy","home","hope",
    "host","hour","huge","hung","hunt","hurt","idea","inch","into","iron","item","jazz","join",
    "jump","kept","kick","kind","king","kiss","knee","knew","know","lack","lady","laid","lake",
    "land","lane","last","late","lead","left","less","life","lift","like","limb","line","link",
    "list","live","load","loan","lock","logo","long","look","lord","lose","loss","lost","love",
    "luck","made","mail","main","make","male","many","mark","mass","meal","mean","meat","meet",
    "menu","mere","mike","mile","milk","mind","mine","miss","mode","mood","moon","more","most",
    "move","much","must","name","navy","near","neck","need","news","next","nice","nick","nine",
    "none","nose","note","okay","once","only","onto","open","oral","over","pace","pack","page",
    "paid","pain","pair","palm","park","part","pass","past","path","peak","pick","pile","pipe",
    "plan","play","plot","plug","plus","poem","poet","pole","pool","poor","port","pose","post",
    "pull","pure","push","race","rail","rain","rank","rare","rate","read","real","rear","rely",
    "rent","rest","rice","rich","ride","ring","rise","risk","road","rock","role","roll","roof",
    "room","root","rose","rule","rush","safe","said","sail","salt","same","sand","save","seat",
    "seed","seek","seem","seen","self","sell","send","ship","shop","shot","show","shut","sick",
    "side","sign","silk","sing","site","size","skin","slip","slow","snow","soft","soil","sold",
    "sole","some","song","soon","sort","soul","spot","star","stay","step","stop","such","suit",
    "sure","take","tale","talk","tall","tape","task","team","tech","tell","tend","term","test",
    "text","than","that","them","then","they","thin","this","thus","tide","till","time","tiny",
    "told","toll","tone","took","tool","tour","town","tree","trip","true","tune","turn","twin",
    "type","unit","upon","user","vast","very","vice","view","vote","wage","wait","wake","walk",
    "wall","want","warm","wash","wave","weak","wear","week","well","went","were","west","what",
    "when","whom","wide","wife","wild","will","wind","wine","wing","wire","wise","wish","with",
    "wood","wool","word","wore","work","yard","yeah","year","your"
]


def _deleet(text: str) -> str:
    mapping = str.maketrans({
        '0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '7': 't', '@': 'a', '$': 's', '!': 'i'
    })
    return text.translate(mapping)


def _sequences_count(password: str) -> int:
    if len(password) < 3:
        return 0
    sequences = 0
    # Check ascending sequences in letters and digits
    for i in range(len(password) - 2):
        a, b, c = password[i], password[i + 1], password[i + 2]
        if a.isalpha() and b.isalpha() and c.isalpha():
            if ord(b) == ord(a) + 1 and ord(c) == ord(b) + 1:
                sequences += 1
        if a.isdigit() and b.isdigit() and c.isdigit():
            if int(b) == int(a) + 1 and int(c) == int(b) + 1:
                sequences += 1
    return sequences


def _charset_size(password: str) -> int:
    size = 0
    lowers = any(c.islower() for c in password)
    uppers = any(c.isupper() for c in password)
    digits = any(c.isdigit() for c in password)
    symbols = any(c in SAFE_SYMBOLS for c in password)
    size += 26 if lowers else 0
    size += 26 if uppers else 0
    size += 10 if digits else 0
    size += len(SAFE_SYMBOLS) if symbols else 0
    return max(size, 1)


def _entropy_bits(password: str) -> float:
    size = _charset_size(password)
    return len(password) * math.log2(size)


def _human_time(seconds: float) -> str:
    if seconds < 1:
        return "< 1 second"
    intervals = [
        (60, "seconds"),
        (60, "minutes"),
        (24, "hours"),
        (365, "days"),
        (100, "years"),
        (10, "centuries")
    ]
    amount = seconds
    unit = "seconds"
    for factor, name in intervals:
        if amount < factor:
            break
        amount /= factor
        unit = name
    if amount > 1e6:
        return "> 1 million {}".format(unit)
    return f"{amount:.1f} {unit}"


def evaluate_password(password: str) -> dict:
    if not password:
        return {
            "score": 0,
            "label": "",
            "color": "#666666",
            "entropy_bits": 0.0,
            "crack_time": "",
            "suggestions": ["Type a password to evaluate it."],
        }

    suggestions = []
    length = len(password)
    lowers = any(c.islower() for c in password)
    uppers = any(c.isupper() for c in password)
    digits = any(c.isdigit() for c in password)
    symbols = any(c in SAFE_SYMBOLS for c in password)

    # Base score from length (up to 40)
    score = min(length, 20) * 2

    # Character set variety (up to 40)
    score += 10 if lowers else 0
    score += 10 if uppers else 0
    score += 10 if digits else 0
    score += 10 if symbols else 0

    categories = sum([lowers, uppers, digits, symbols])
    if categories >= 3:
        score += 10
    if categories == 4:
        score += 5

    # Penalties
    if password.isalpha():
        score -= 15
        suggestions.append("Avoid only letters; add digits and symbols.")
    if password.isdigit():
        score -= 20
        suggestions.append("Avoid only numbers; add letters and symbols.")

    unique_ratio = len(set(password)) / max(1, len(password))
    repeated_ratio = 1 - unique_ratio
    if repeated_ratio > 0.40:
        score -= 15
        suggestions.append("Avoid repeating the same characters.")
    elif repeated_ratio > 0.25:
        score -= 10

    seqs = _sequences_count(password)
    if seqs:
        score -= min(20, 10 * seqs)
        suggestions.append("Avoid sequences like 'abc' or '123'.")

    lower_p = password.lower()
    deleeted = _deleet(lower_p)
    if lower_p in COMMON_PASSWORDS or deleeted in COMMON_PASSWORDS:
        score -= 40
        suggestions.append("This password is commonly used. Pick something more unique.")

    # Dictionary substrings
    for word in COMMON_WORDS:
        if len(word) >= 4 and (word in lower_p or word in deleeted):
            score -= 15
            suggestions.append("Avoid dictionary words or obvious phrases.")
            break

    # Positive guidance
    if length < 12:
        suggestions.append("Use at least 12–16 characters.")
    if not lowers:
        suggestions.append("Add lowercase letters.")
    if not uppers:
        suggestions.append("Add uppercase letters.")
    if not digits:
        suggestions.append("Add digits.")
    if not symbols:
        suggestions.append("Add special characters (e.g., !@#...).")
    if categories >= 3 and length >= 12 and not seqs and repeated_ratio <= 0.25:
        # Already quite good; add optional advice
        suggestions.append("Consider a 4–5 word passphrase for memorability.")

    score = max(0, min(100, score))

    if score < 30:
        label = "Very Weak"
        color = "#e74c3c"
    elif score < 50:
        label = "Weak"
        color = "#e67e22"
    elif score < 70:
        label = "Fair"
        color = "#f1c40f"
    elif score < 85:
        label = "Good"
        color = "#2ecc71"
    else:
        label = "Very Strong"
        color = "#27ae60"

    ent = _entropy_bits(password)
    # Assume 1e9 guesses/second (powerful rig), average-case half the keyspace
    seconds = (2 ** ent) / (1e9 * 2)
    return {
        "score": score,
        "label": label,
        "color": color,
        "entropy_bits": ent,
        "crack_time": _human_time(seconds),
        "suggestions": suggestions[:6] if suggestions else ["Looks good. Keep it unique for each site."]
    }


def generate_password(length: int = 16) -> str:
    length = max(8, min(64, int(length)))
    alphabet_letters = string.ascii_letters
    alphabet_digits = string.digits
    alphabet_symbols = SAFE_SYMBOLS
    # Ensure all categories appear at least once
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(alphabet_symbols),
    ]
    remaining_length = max(0, length - len(required))
    all_chars = alphabet_letters + alphabet_digits + alphabet_symbols
    body = [secrets.choice(all_chars) for _ in range(remaining_length)]
    pwd_list = required + body
    secrets.SystemRandom().shuffle(pwd_list)
    return ''.join(pwd_list)


def generate_passphrase(num_words: int = 4, separator: str = '-', capitalize: bool = False, add_number: bool = True) -> str:
    num_words = max(3, min(10, int(num_words)))
    words = [secrets.choice(PASSPHRASE_WORDS) for _ in range(num_words)]
    if capitalize:
        words = [w.capitalize() for w in words]
    phrase = separator.join(words)
    if add_number:
        phrase = f"{phrase}{separator}{secrets.choice(string.digits)}{secrets.choice(string.digits)}"
    return phrase


# ---------------------------
# Tkinter Desktop Application
# ---------------------------

class PasswordCheckerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        # Set Windows AppUserModelID for taskbar grouping and identity
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lasanga")
        except Exception:
            pass
        self.title("lasanga – Password Strength Checker")
        self.geometry("720x520")
        self.minsize(640, 480)

        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        # Determine default background and set current
        default_bg = self.style.lookup('TFrame', 'background') or self.cget('background') or '#f0f0f0'
        if default_bg in ("SystemButtonFace", "systemWindowBody"):
            default_bg = '#f0f0f0'
        self.default_bg = default_bg
        self.current_bg = default_bg

        self._build_ui()
        self._apply_bg_color(self.current_bg)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill=tk.BOTH, expand=True)

        # Password input row
        row1 = ttk.Frame(root)
        row1.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(row1, text="Password:").pack(side=tk.LEFT)

        self.password_var = tk.StringVar()
        self.entry = ttk.Entry(row1, textvariable=self.password_var, show='•', width=50, style='App.TEntry')
        self.entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        self.entry.bind('<KeyRelease>', self._on_password_change)

        self.show_var = tk.BooleanVar(value=False)
        show_cb = ttk.Checkbutton(row1, text="Show", variable=self.show_var, command=self._toggle_show)
        show_cb.pack(side=tk.LEFT, padx=(0, 8))

        copy_btn = ttk.Button(row1, text="Copy", command=self._copy_password)
        copy_btn.pack(side=tk.LEFT)
        clear_btn = ttk.Button(row1, text="Clear", command=self._clear_password)
        clear_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Generator row
        row2 = ttk.Frame(root)
        row2.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(row2, text="Generator:").pack(side=tk.LEFT)

        self.gen_len_var = tk.IntVar(value=16)
        ttk.Label(row2, text="Length").pack(side=tk.LEFT, padx=(8, 4))
        gen_len = ttk.Spinbox(row2, from_=8, to=64, textvariable=self.gen_len_var, width=5, style='App.TSpinbox')
        gen_len.pack(side=tk.LEFT)

        ttk.Button(row2, text="Generate Strong", command=self._gen_password).pack(side=tk.LEFT, padx=(12, 8))
        self.pass_words_var = tk.IntVar(value=4)
        ttk.Label(row2, text="Words").pack(side=tk.LEFT, padx=(8, 4))
        pass_words = ttk.Spinbox(row2, from_=3, to=10, textvariable=self.pass_words_var, width=4, style='App.TSpinbox')
        pass_words.pack(side=tk.LEFT)
        self.pass_caps_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2, text="Caps", variable=self.pass_caps_var).pack(side=tk.LEFT, padx=(8, 4))
        self.pass_nums_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Add Numbers", variable=self.pass_nums_var).pack(side=tk.LEFT)
        ttk.Button(row2, text="Generate Passphrase", command=self._gen_passphrase).pack(side=tk.LEFT, padx=(12, 0))

        # Background color row
        row3 = ttk.Frame(root)
        row3.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(row3, text="Background:").pack(side=tk.LEFT)
        ttk.Button(row3, text="Pick...", command=self._pick_bg_color).pack(side=tk.LEFT, padx=(8, 4))
        ttk.Button(row3, text="Reset", command=self._reset_bg_color).pack(side=tk.LEFT)

        # Meter section
        meter = ttk.LabelFrame(root, text="Strength")
        meter.pack(fill=tk.X, pady=(0, 12))

        self.style.configure("meter.Horizontal.TProgressbar", troughcolor="#e6e6e6", background="#27ae60")
        self.pb = ttk.Progressbar(meter, style="meter.Horizontal.TProgressbar", maximum=100)
        self.pb.pack(fill=tk.X, padx=12, pady=8)

        stats_row = ttk.Frame(meter)
        stats_row.pack(fill=tk.X, padx=12, pady=(0, 8))
        self.strength_label = ttk.Label(stats_row, text="", width=16)
        self.strength_label.pack(side=tk.LEFT)
        self.entropy_label = ttk.Label(stats_row, text="")
        self.entropy_label.pack(side=tk.LEFT, padx=(16, 0))
        self.time_label = ttk.Label(stats_row, text="")
        self.time_label.pack(side=tk.RIGHT)

        # Suggestions
        sug = ttk.LabelFrame(root, text="Suggestions")
        sug.pack(fill=tk.BOTH, expand=True)
        self.sug_text = tk.Text(sug, height=10, wrap=tk.WORD)
        self.sug_text.configure(state=tk.DISABLED)
        self.sug_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Initial state
        self._update_ui(evaluate_password(""))

    def _toggle_show(self) -> None:
        self.entry.configure(show='' if self.show_var.get() else '•')

    def _copy_password(self) -> None:
        text = self.password_var.get()
        if not text:
            messagebox.showinfo("Copy", "Nothing to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copy", "Password copied to clipboard.")

    def _clear_password(self) -> None:
        self.password_var.set("")
        self.entry.focus_set()

    def _gen_password(self) -> None:
        try:
            n = int(self.gen_len_var.get())
        except Exception:
            n = 16
        pwd = generate_password(n)
        self.password_var.set(pwd)
        self._on_password_change()

    def _gen_passphrase(self) -> None:
        try:
            n = int(self.pass_words_var.get())
        except Exception:
            n = 4
        pwd = generate_passphrase(
            num_words=n,
            separator='-',
            capitalize=bool(self.pass_caps_var.get()),
            add_number=bool(self.pass_nums_var.get())
        )
        self.password_var.set(pwd)
        self._on_password_change()

    def _on_password_change(self, _event=None) -> None:
        result = evaluate_password(self.password_var.get())
        self._update_ui(result)

    def _update_ui(self, result: dict) -> None:
        score = result.get("score", 0)
        label = result.get("label", "")
        color = result.get("color", "#666666")
        ent = result.get("entropy_bits", 0.0)
        crack = result.get("crack_time", "")
        suggestions = result.get("suggestions", [])

        self.pb['value'] = score
        self.style.configure("meter.Horizontal.TProgressbar", background=color)
        if label:
            self.strength_label.configure(text=f"{label} ({score}/100)")
        else:
            self.strength_label.configure(text="")
        if ent:
            self.entropy_label.configure(text=f"Entropy: {ent:.1f} bits")
        else:
            self.entropy_label.configure(text="")
        if crack:
            self.time_label.configure(text=f"Est. crack time: {crack}")
        else:
            self.time_label.configure(text="")

        self.sug_text.configure(state=tk.NORMAL)
        self.sug_text.delete("1.0", tk.END)
        for s in suggestions:
            self.sug_text.insert(tk.END, f"• {s}\n")
        self.sug_text.configure(state=tk.DISABLED)

    def _apply_bg_color(self, bg_hex: str) -> None:
        try:
            fg_hex = _best_text_color(bg_hex)
            bright = _brightness(_hex_to_rgb(bg_hex))
            field_bg = _shade(bg_hex, 0.09 if bright < 128 else -0.06)
            trough = _shade(bg_hex, 0.12 if bright < 128 else -0.10)

            # Window background
            self.configure(background=bg_hex)

            # ttk styles
            self.style.configure('TFrame', background=bg_hex)
            self.style.configure('TLabel', background=bg_hex, foreground=fg_hex)
            self.style.configure('TCheckbutton', background=bg_hex, foreground=fg_hex)
            self.style.configure('TButton', background=bg_hex, foreground=fg_hex)
            self.style.configure('TLabelframe', background=bg_hex, foreground=fg_hex)
            self.style.configure('TLabelframe.Label', background=bg_hex, foreground=fg_hex)
            self.style.configure('App.TEntry', fieldbackground=field_bg, foreground=fg_hex)
            self.style.configure('App.TSpinbox', fieldbackground=field_bg, foreground=fg_hex, background=bg_hex)
            self.style.configure('meter.Horizontal.TProgressbar', troughcolor=trough)

            # Text widget
            if hasattr(self, 'sug_text'):
                self.sug_text.configure(bg=bg_hex, fg=fg_hex, insertbackground=fg_hex)
        except Exception:
            pass

    def _pick_bg_color(self) -> None:
        try:
            _, hexcolor = colorchooser.askcolor(title="Choose background color", initialcolor=self.current_bg)
            if hexcolor:
                self.current_bg = hexcolor
                self._apply_bg_color(self.current_bg)
        except Exception:
            pass

    def _reset_bg_color(self) -> None:
        self.current_bg = self.default_bg
        self._apply_bg_color(self.current_bg)


def main() -> None:
    app = PasswordCheckerApp()
    app.mainloop()


if __name__ == "__main__":
    main()


