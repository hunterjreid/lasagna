# lasagna
Password Strength Checker: Create a tool that checks the strength of passwords and provides recommendations for stronger passwords.

Desktop app (no website). Built with Python Tkinter.

Branding: The app identifies itself as "lasanga" on Windows (AppUserModelID),
and the window title shows "lasanga – Password Strength Checker".

## Features
- Live password strength meter (0–100) with color labels
- Suggestions to improve weak passwords
- Entropy estimate and rough crack-time estimate
- One-click strong password generator
- Human-friendly passphrase generator (configurable words, caps, numbers)
- Show/Hide input, Copy, Clear
- Custom background color: pick any color or reset to default.

## Windows usage
1) Install Python 3 (if not already installed).
   - Download from `https://www.python.org/downloads/windows/` and check "Add Python to PATH" during setup.
2) Run the app:
   - Option A: Right-click `run.ps1` → Run with PowerShell
   - Option B: In PowerShell from this folder: `./run.ps1`
   - Option C: Directly run with Python launcher: `py -3 app.py`

No internet access or extra packages required.

## Notes
- Strength scoring is heuristic and for educational guidance. Use unique passwords per site and enable 2FA where possible.
- Passphrases are generated from a small built-in wordlist for offline use.