"""
setupbuild.py — สแกนโปรเจกต์แล้ว build เป็นโปรแกรมให้อัตโนมัติ (ไม่จำกัดแค่ Python)

วางไฟล์นี้ไว้ในโฟลเดอร์โปรเจกต์ แล้วรัน  python setupbuild.py  — ไม่ต้องเขียน config

ชนิดโปรเจกต์ที่รองรับ (ตรวจจากไฟล์หลักของโปรเจกต์เอง)
  Python (PyInstaller) · Electron · Tauri · Flutter · .NET (csproj) · Rust (Cargo.toml)
  Go (go.mod) · Java (pom.xml / gradle) · C/C++ (CMakeLists.txt) · Node.js CLI (pkg) · เว็บ Node.js
  ถ้าเจอหลายชนิดจะถามให้เลือก (หรือบังคับด้วย --type) · build เสร็จแสดง SHA256 ของ EXE ให้

สคริปต์จะสแกนโปรเจกต์ แล้วตัดสินใจเองว่า
  • ชนิดโปรเจกต์ · ไฟล์หลัก · ชื่อแอป · เวอร์ชัน · เป็นโปรแกรมหน้าต่างหรือ console
  • Python: ไลบรารีที่ต้องติดตั้ง (แยก "จำเป็น"/"ไม่จำเป็น") · ไฟล์ข้อมูล/โฟลเดอร์ทรัพยากร · hidden-import
  • ภาษาอื่น: เครื่องมือ build ที่ต้องมี (Node, Go, cargo, .NET SDK, JDK, CMake, Flutter — ถามก่อนติดตั้งผ่าน winget)
    และคำสั่ง install/build ที่เหมาะกับโครงสร้างโปรเจกต์
  • เครื่องมือเสริมที่โค้ดเรียกใช้ (ffmpeg, 7-Zip, Ghostscript, Tesseract ...)
  • ไอคอน: ค้นหาในโฟลเดอร์หลักและโฟลเดอร์ย่อย (assets/icons/resources/build ...) ลึกไม่เกิน 3 ชั้น
    ถ้าเจอ .ico ใช้เลย ถ้าเจอแต่ .png (สี่เหลี่ยมจัตุรัส ≥ 64px) จะแปลงเป็น .ico ให้ตอน build
    ถ้าไม่เจอก็ข้าม ใช้ไอคอนเริ่มต้น · ปิดด้วย {"icon": false} · ระบุเองด้วย {"icon": "path"}
  • ไฟล์ Inno Setup (.iss) · ไฟล์ .exe/.dll ที่วางไว้ข้างสคริปต์ (Python)

ระบบ log + แก้เองอัตโนมัติ (โปรเจกต์ Python)
  • EXE ที่ build ออกมาจะเขียน log ตัวเองที่ %LOCALAPPDATA%\\<ชื่อแอป>\\logs\\app.log
    (รวมข้อความ error / traceback ทั้งหมด แม้เป็นโปรแกรมแบบไม่มีหน้าต่าง console)
  • ตอนทดสอบเปิด EXE สคริปต์จะอ่าน log นั้นมาวิเคราะห์ ถ้าพบ "ไม่มีโมดูล X" จะเพิ่มให้เอง
    (บันทึกลง autobuild.json คีย์ extra_hidden_imports) แล้ว build + ทดสอบซ้ำ
  • ทุกครั้งที่รันจะสร้าง autobuild_report.txt รวมทุกอย่างไว้ไฟล์เดียว ส่งต่อให้คนช่วยดูได้เลย
  • python setupbuild.py --logs  ดึง log ล่าสุดของโปรแกรมมาวิเคราะห์ โดยไม่ build ใหม่

ถ้าสแกนผิดจุดไหน สร้างไฟล์ autobuild.json แล้วใส่เฉพาะค่าที่ต้องการแก้ — จะทับผลสแกนเฉพาะคีย์นั้น
  เช่น {"project_type": "go", "build_commands": [["go","build","-o","dist/app.exe","."]], "icon": false}

ตัวเลือก
  --scan-only     สแกนแล้วแสดงผลอย่างเดียว ไม่ build
  --init          บันทึกผลสแกนเป็น autobuild.json ไว้แก้ต่อ
  --dry-run       แสดงคำสั่ง build โดยไม่รันจริง
  --yes           ตอบรับค่าเริ่มต้นทุกคำถาม (รันโดยไม่ต้องมีคนคอย)
  --type TYPE     บังคับชนิดโปรเจกต์ (python/electron/tauri/flutter/dotnet/rust/go/java/cmake/node-cli/node-web)
  --project DIR   สแกนโฟลเดอร์อื่น (ค่าเริ่มต้น: โฟลเดอร์ของสคริปต์)
  --config FILE   ใช้ไฟล์ config อื่นแทน autobuild.json
  --no-scan       ปิดการสแกน ใช้เฉพาะ config
  --logs          ดึง/วิเคราะห์ log ของโปรแกรม Python ที่ build แล้ว แล้วสรุปเป็นรายงาน

ขั้นตอน
  1  สแกนโปรเจกต์อัตโนมัติ
  2  ตรวจไฟล์โปรเจกต์ (Python: ตรวจเวอร์ชัน Python ด้วย)
  3  Python: ติดตั้งไลบรารี  |  ภาษาอื่น: ตรวจ/ติดตั้งเครื่องมือ build
  4  Python: ติดตั้งเครื่องมือเสริม  |  ภาษาอื่น: ติดตั้ง dependencies (npm install ฯลฯ)
  5  Windows Defender: ตรวจ/เสนอยกเว้นโฟลเดอร์โปรเจกต์ (ถามยืนยันก่อนเสมอ)
  6  Build (จบแล้วแสดง SHA256; ถ้า EXE หายจะตรวจประวัติ Defender)
  7  ทดสอบเปิดโปรแกรม
  8  สร้างตัวติดตั้ง (Inno Setup — ถ้าพบไฟล์ .iss)
"""
import argparse
import ast
import copy
import glob
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zipfile

SELF = os.path.abspath(__file__)
SELF_KEY = os.path.normcase(SELF)
HERE = os.path.dirname(SELF)      # โฟลเดอร์โปรเจกต์ (เปลี่ยนได้ด้วย --project)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
if os.name == "nt":
    os.system("")          # เปิดการแสดงสี ANSI ใน cmd

NOWIN = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}

# ── สี / ข้อความ ──────────────────────────────────────────────
R, G, Y, B, M, D, X = ("\033[91m", "\033[92m", "\033[93m", "\033[94m",
                       "\033[95m", "\033[90m", "\033[0m")
OK, WARN, FAIL, SKIP = "ok", "warn", "fail", "skip"
ICON = {OK: f"{G}✓{X}", WARN: f"{Y}⚠{X}", FAIL: f"{R}✗{X}", SKIP: f"{D}–{X}"}

ASSUME_YES = False          # --yes
CFG = {}                    # โหลดจาก autobuild.json
CFG_PATH = ""               # path ของ autobuild.json (ใช้บันทึกสิ่งที่เรียนรู้)
BUILD_LOG = os.path.join(HERE, "build_log.txt")

DEFAULT_CONFIG = {
    "app_name": "MyApp",
    "version": "1.0",
    "entry_script": "",
    "icon": None,
    "onefile": True,
    "windowed": True,
    "min_python": [3, 9],
    "required_files": [],
    "add_data": [],
    "add_binary": [],
    "add_binary_first_found": [],
    "hidden_imports": [],
    "collect_all": [],
    "extra_pyinstaller_args": [],
    "requirements_file": None,
    "python_packages": [
        {"module": "PyInstaller", "pip": "pyinstaller", "required": True,
         "desc": "ตัว build EXE"}
    ],
    "external_tools": [],
    "test_launch_seconds": 8,
    "runtime_log": True,
    "auto_fix": True,
    "defender": {"check": True, "offer_exclusion": True},
    "max_auto_retries": 2,
    "extra_hidden_imports": [],
    "extra_add_data": [],
    "extra_collect_all": [],
    "project_type": None,          # None = ตรวจเอง · python/electron/tauri/flutter/dotnet/rust/go/java/cmake/node-cli/node-web
    "builder": {},                 # แผน build ของโปรเจกต์ที่ไม่ใช่ Python (สแกนสร้างให้)
    "install_commands": None,      # ทับคำสั่งติดตั้ง dependencies (รายการของรายการ)
    "build_commands": None,        # ทับคำสั่ง build
    "installer": {"enabled": False, "iss_file": "installer.iss",
                  "output_dir": "installer_output", "output_glob": "*Setup*.exe"},
    "help_hints": {"run_without_build": "run.bat"}
}

# ── ตัวช่วยพื้นฐาน ────────────────────────────────────────────
def line(ch="─", n=60, color=D):
    print(f"{color}{ch * n}{X}")


def header(i, total, title):
    print()
    print(f"{M}  ขั้นตอนที่ {i}/{total}{X}  {title}\n")


def say(msg, color=""):
    print(f"  {color}{msg}{X}")


def ask_yes(question, default=True):
    if ASSUME_YES:
        return default
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        try:
            a = input(f"  {B}?{X} {question} {hint} ").strip().lower()
        except EOFError:
            return default
        if not a:
            return default
        if a in ("y", "yes", "ใช่", "1"):
            return True
        if a in ("n", "no", "ไม่", "0"):
            return False


def ask_choice(question, options):
    """options = {'r': 'ลองใหม่', 'q': 'ออก'} → คืนตัวอักษรที่เลือก"""
    if ASSUME_YES:
        return "q"          # โหมดไม่โต้ตอบ: ล้มแล้วออก ไม่วนลูปไม่รู้จบ
    opts = " / ".join(f"{k.upper()} = {v}" for k, v in options.items())
    while True:
        try:
            a = input(f"  {B}?{X} {question}  ({opts}) ").strip().lower()
        except EOFError:
            return "q"
        if a in options:
            return a


def run_quiet(cmd, timeout=None):
    """รันคำสั่งโดยเก็บผลลัพธ์ → (returncode, ข้อความ)"""
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, **NOWIN)
    except subprocess.TimeoutExpired:
        return 1, "หมดเวลา (timeout)"
    except OSError as ex:
        return 1, str(ex)
    out = (p.stdout or b"") + (p.stderr or b"")
    return p.returncode, out.decode("utf-8", "replace")


def run_with_spinner(cmd, label, log_path=None, env=None, cwd=None):
    """รันคำสั่งยาว ๆ พร้อมตัวนับเวลา · เก็บ log ลงไฟล์ → (returncode, ข้อความ log)"""
    log_path = log_path or BUILD_LOG
    t0 = time.time()
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    k = 0
    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        try:
            proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env, cwd=cwd, **NOWIN)
        except OSError as ex:
            return 1, str(ex)
        while proc.poll() is None:
            el = int(time.time() - t0)
            print(f"\r  {B}{frames[k % len(frames)]}{X} {label}  {D}{el // 60:02d}:{el % 60:02d}{X}   ",
                  end="", flush=True)
            k += 1
            time.sleep(0.12)
    print("\r" + " " * 78 + "\r", end="")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
    except OSError:
        txt = ""
    return proc.returncode, txt


def tail(text, n=8):
    rows = [r for r in text.strip().splitlines() if r.strip()]
    return rows[-n:]


def force_rmtree(path):
    """ลบโฟลเดอร์แบบบังคับ (ปลด read-only ก่อน) · คืน True ถ้าลบหมดแล้ว"""
    if not os.path.isdir(path):
        return True
    if os.name == "nt":
        run_quiet(["cmd", "/c", "attrib", "-r", "-s", "-h", os.path.join(path, "*"), "/s", "/d"], timeout=120)
        run_quiet(["cmd", "/c", "rmdir", "/s", "/q", path], timeout=120)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    return not os.path.isdir(path)


def has_module(name):
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def here(*parts):
    return os.path.join(HERE, *parts)


def exe_path():
    if BUILT_EXE:
        return BUILT_EXE
    ext = ".exe" if os.name == "nt" else ""
    return here("dist", CFG["app_name"] + ext)


def installer_outputs():
    inst = CFG["installer"]
    pattern = here(inst["output_dir"], inst["output_glob"])
    return glob.glob(pattern)


# ═══ ตัวสแกนโปรเจกต์อัตโนมัติ ═══════════════════════════════════
SKIP_DIRS = {"dist", "build", "venv", ".venv", "env", "__pycache__", "node_modules",
             "installer_output", "site-packages", "tests", "test"}
GUI_LIBS = {"tkinter", "customtkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "wx",
            "kivy", "pygame", "flet", "ttkbootstrap", "dearpygui", "toga", "webview", "eel",
            "flaskwebgui", "pystray"}
# ชื่อที่ import ≠ ชื่อที่ pip install
IMPORT_TO_PIP = {
    "PIL": "pillow", "cv2": "opencv-python", "yaml": "pyyaml", "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn", "skimage": "scikit-image", "win32api": "pywin32",
    "win32com": "pywin32", "win32gui": "pywin32", "win32con": "pywin32", "pythoncom": "pywin32",
    "serial": "pyserial", "docx": "python-docx", "pptx": "python-pptx", "fitz": "pymupdf",
    "dotenv": "python-dotenv", "dateutil": "python-dateutil", "jwt": "pyjwt",
    "OpenSSL": "pyopenssl", "Crypto": "pycryptodome", "usb": "pyusb", "magic": "python-magic",
    "attr": "attrs", "git": "gitpython", "zmq": "pyzmq", "PyQt5": "pyqt5", "PyQt6": "pyqt6",
    "PySide2": "pyside2", "webview": "pywebview", "fontTools": "fonttools", "PySide6": "pyside6", "wx": "wxpython", "tkinterdnd2": "tkinterdnd2",
}
# แพ็กเกจที่ต้องใช้ --collect-all จึงจะแนบไฟล์ข้อมูลครบ
COLLECT_ALL = {"tkinterdnd2", "customtkinter", "ttkbootstrap", "sv_ttk", "pyfiglet", "uvicorn"}
DATA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".json", ".txt", ".csv",
            ".ttf", ".otf", ".woff", ".woff2", ".yaml", ".yml", ".ini", ".cfg", ".xml",
            ".html", ".css", ".js", ".mp3", ".wav", ".ogg", ".mp4", ".db", ".sqlite", ".ui", ".qss"}
ALWAYS_DIRS = {"assets", "resources", "resource", "images", "img", "icons", "fonts", "static", "templates"}
REF_DIRS = {"data", "locales", "lang", "i18n", "sounds", "sound", "config", "themes"}
GENERIC_NAMES = {"main", "app", "__main__", "run", "gui", "start", "index", "launcher"}
ENTRY_HINTS = ("main", "app", "run", "gui", "launcher")
VERSION_VARS = {"__version__", "VERSION", "APP_VERSION", "version"}

# เครื่องมือภายนอก: aliases = ชื่อคำสั่งที่อาจโผล่ในโค้ด
KNOWN_TOOLS = [
    {"name": "7-Zip", "aliases": ["7z", "7za", "7zr"], "desc": "บีบอัด/แตกไฟล์ .7z หลายคอร์",
     "winget_id": "7zip.7zip", "commands": ["7z", "7za", "7zr"],
     "paths": [r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"]},
    {"name": "ffmpeg", "aliases": ["ffmpeg", "ffprobe"], "desc": "ประมวลผลวิดีโอ/เสียง",
     "winget_id": "Gyan.FFmpeg", "commands": ["ffmpeg"]},
    {"name": "Ghostscript", "aliases": ["gs", "gswin64c", "gswin32c"], "desc": "ประมวลผล PDF คุณภาพสูง",
     "winget_id": "ArtifexSoftware.Ghostscript", "commands": ["gswin64c", "gswin32c", "gs"],
     "globs": [r"C:\Program Files\gs\*\bin\gswin*c.exe", r"C:\Program Files (x86)\gs\*\bin\gswin*c.exe"]},
    {"name": "Tesseract", "aliases": ["tesseract"], "needs_pkg": "pytesseract", "desc": "OCR อ่านข้อความจากรูป",
     "winget_id": "UB-Mannheim.TesseractOCR", "commands": ["tesseract"],
     "paths": [r"C:\Program Files\Tesseract-OCR\tesseract.exe"]},
    {"name": "Pandoc", "aliases": ["pandoc"], "needs_pkg": "pypandoc", "desc": "แปลงรูปแบบเอกสาร",
     "winget_id": "JohnMacFarlane.Pandoc", "commands": ["pandoc"]},
    {"name": "ImageMagick", "aliases": ["magick"], "desc": "ประมวลผลรูปภาพ",
     "winget_id": "ImageMagick.ImageMagick", "commands": ["magick"]},
    {"name": "LibreOffice", "aliases": ["soffice", "libreoffice"], "desc": "แปลงเอกสาร Office",
     "winget_id": "TheDocumentFoundation.LibreOffice", "commands": ["soffice", "libreoffice"],
     "paths": [r"C:\Program Files\LibreOffice\program\soffice.exe"]},
    {"name": "Poppler", "aliases": [], "needs_pkg": "pdf2image", "desc": "แปลง PDF เป็นรูป (pdf2image ต้องใช้)",
     "winget_id": "oschwartz10612.Poppler", "commands": ["pdftoppm"],
     "globs": [r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\oschwartz10612.Poppler*\poppler-*\Library\bin\pdftoppm.exe",
               r"C:\Program Files\poppler*\Library\bin\pdftoppm.exe"]},
    {"name": "yt-dlp", "aliases": ["yt-dlp"], "desc": "ดาวน์โหลดวิดีโอ",
     "winget_id": "yt-dlp.yt-dlp", "commands": ["yt-dlp"]},
]


def is_stdlib(name):
    sn = getattr(sys, "stdlib_module_names", None)
    if sn is not None:
        return name in sn
    import importlib.util
    import sysconfig
    try:
        spec = importlib.util.find_spec(name)
    except Exception:
        return False
    if spec is None:
        return False
    o = spec.origin or ""
    if o in ("built-in", "frozen"):
        return True
    return o.startswith(sysconfig.get_paths()["stdlib"]) and "site-packages" not in o


def _exc_names(t):
    if t is None:
        return {"Exception"}
    if isinstance(t, ast.Name):
        return {t.id}
    if isinstance(t, ast.Attribute):
        return {t.attr}
    if isinstance(t, ast.Tuple):
        out = set()
        for e in t.elts:
            out |= _exc_names(e)
        return out
    return set()


class _Visitor(ast.NodeVisitor):
    """เก็บ import / ข้อความคงที่ / dynamic import / ไฟล์นี้เป็นจุดเริ่มโปรแกรมไหม"""

    def __init__(self):
        self.imports = []            # (ชื่อบนสุด, อยู่ใน try/except ImportError ไหม)
        self.consts = set()
        self.dynamic = set()
        self.main_guard = False
        self.version = None
        self._guard = 0

    def visit_Try(self, node):
        guarded = any(_exc_names(h.type) & {"ImportError", "ModuleNotFoundError", "Exception"}
                      for h in node.handlers)
        if guarded:
            self._guard += 1
            for n in node.body:
                self.visit(n)
            self._guard -= 1
            for n in node.handlers + node.orelse + node.finalbody:
                self.visit(n)
        else:
            self.generic_visit(node)

    visit_TryStar = visit_Try

    def visit_Import(self, node):
        for a in node.names:
            self.imports.append((a.name.split(".")[0], bool(self._guard)))

    def visit_ImportFrom(self, node):
        if node.level == 0 and node.module:
            self.imports.append((node.module.split(".")[0], bool(self._guard)))

    def visit_Call(self, node):
        f = node.func
        is_dyn = (isinstance(f, ast.Name) and f.id == "__import__") or \
                 (isinstance(f, ast.Attribute) and f.attr == "import_module")
        if is_dyn and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            self.dynamic.add(node.args[0].value)
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) < 260:
            self.consts.add(node.value)

    def visit_If(self, node):
        t = node.test
        if isinstance(t, ast.Compare) and isinstance(t.left, ast.Name) and t.left.id == "__name__":
            self.main_guard = True
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in VERSION_VARS and self.version is None:
                    self.version = node.value.value
        self.generic_visit(node)


def _iter_py(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")
                  and not os.path.isfile(os.path.join(dp, d, "pyvenv.cfg"))]
        for fn in fns:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dp, fn)
            if os.path.normcase(os.path.abspath(p)) == SELF_KEY or fn.lower().replace("_", "").startswith("setupbuild"):
                continue
            if fn in ("setup.py", "conftest.py") or fn.startswith("test_") or fn.endswith("_test.py"):
                continue
            yield p


def _rel(root, p):
    return os.path.relpath(p, root).replace(os.sep, "/")


def _norm_cmd(const):
    base = const.strip().strip("\"'").replace("\\", "/").split("/")[-1].lower()
    return base[:-4] if base.endswith(".exe") else base


def auto_config(root):
    """สแกนโปรเจกต์ → (config ที่สร้างให้, บรรทัดรายงาน [(สถานะ, ข้อความ)])"""
    rep = []
    cfg = {}
    analyses = {}
    for p in _iter_py(root):
        try:
            with open(p, encoding="utf-8-sig", errors="replace") as f:
                src = f.read()
            tree = ast.parse(src)
        except (SyntaxError, ValueError, OSError) as ex:
            rep.append((WARN, f"อ่าน {_rel(root, p)} ไม่ได้ ({type(ex).__name__}) — ข้ามไฟล์นี้"))
            continue
        v = _Visitor()
        v.visit(tree)
        analyses[p] = (v, len(src))

    if not analyses:
        rep.append((FAIL, "ไม่พบไฟล์ .py ในโปรเจกต์"))
        return cfg, rep
    rep.append((OK, f"สแกนไฟล์ Python {len(analyses)} ไฟล์"))

    # ── โมดูลในโปรเจกต์เอง (ไม่ต้อง pip) ──
    local = set()
    for p in analyses:
        parts = _rel(root, p).split("/")
        local.add(parts[0][:-3] if len(parts) == 1 else parts[0])

    imported_by = {}
    for p, (v, _) in analyses.items():
        me = os.path.splitext(os.path.basename(p))[0]
        for top, _opt in v.imports:
            if top in local and top != me:
                imported_by[top] = imported_by.get(top, 0) + 1

    # ── เลือกไฟล์หลัก ──
    all_tops = {t for v, _ in analyses.values() for t, _o in v.imports}
    cands = []
    for p, (v, size) in analyses.items():
        stem = os.path.splitext(os.path.basename(p))[0]
        if stem.startswith("build"):
            continue
        depth = _rel(root, p).count("/")
        score = (5 if any(h in stem.lower() for h in ENTRY_HINTS) else 0) + (3 if v.main_guard else 0) \
            + (2 if {t for t, _o in v.imports} & GUI_LIBS else 0) \
            - 3 * imported_by.get(stem, 0) - 2 * depth
        cands.append((score, size, p))
    if not cands:
        rep.append((FAIL, "ไม่พบไฟล์หลักของโปรแกรม"))
        return cfg, rep
    cands.sort(key=lambda c: (c[0], c[1]), reverse=True)
    entry = cands[0][2]
    if len(cands) > 1 and cands[0][0] == cands[1][0] and not ASSUME_YES:
        top = cands[:min(4, len(cands))]
        top = [c for c in top if c[0] == cands[0][0]]
        rep_opts = {str(i + 1): _rel(root, c[2]) for i, c in enumerate(top)}
        print()
        say("พบไฟล์ที่เป็นไปได้หลายไฟล์ — เลือกไฟล์หลักของโปรแกรม", Y)
        ch = ask_choice("ไฟล์หลักคือ", rep_opts)
        entry = top[int(ch) - 1][2] if ch in rep_opts else entry
    entry_rel = _rel(root, entry)
    cfg["entry_script"] = entry_rel
    rep.append((OK, f"ไฟล์หลัก: {entry_rel}"))

    # ── ชื่อแอป / เวอร์ชัน ──
    stem = os.path.splitext(os.path.basename(entry))[0]
    tokens = [t for t in re.split(r"[_\-\s]+", stem.lower()) if t]
    if tokens and all(t in GENERIC_NAMES | {"desktop", "server", "launch", "launcher", "start"} for t in tokens):
        name = os.path.basename(root.rstrip("\\/")) or "App"
    else:
        name = stem
    name = re.sub(r"[^\w\-]+", "_", name).strip("_") or "App"
    if name.islower() and "_" not in name:
        name = name[:1].upper() + name[1:]
    ev = analyses[entry][0]
    ver = next((v.version for v, _ in [analyses[entry]] if v.version), None) or \
        next((v.version for v, _ in analyses.values() if v.version), None)
    if not ver:
        for c in sorted(ev.consts):
            m = re.search(r"\b[Vv](?:ersion)?\s*(\d+\.\d+(?:\.\d+)?)\b", c)
            if m:
                ver = m.group(1)
                break
    cfg["app_name"] = name
    cfg["version"] = ver or "1.0"
    rep.append((OK, f"ชื่อแอป: {name}   เวอร์ชัน: {cfg['version']}"))

    # ── ประเภทโปรแกรม ──
    gui = sorted(all_tops & GUI_LIBS)
    cfg["windowed"] = bool(gui)
    rep.append((OK, ("โปรแกรมหน้าต่าง (GUI: " + ", ".join(gui) + ") → build แบบไม่มีหน้าต่าง console")
                if gui else "โปรแกรม console → build แบบมีหน้าต่าง console"))

    # ── ไลบรารี ──
    pkgs = {}                         # ชื่อ import → {optional, file}
    for p, (v, _) in analyses.items():
        for top, opt in v.imports:
            if top in local or is_stdlib(top) or top == "PyInstaller":
                continue
            d = pkgs.setdefault(top, {"optional": True, "file": _rel(root, p)})
            d["optional"] = d["optional"] and opt
    for p, (v, _) in analyses.items():          # import แบบ dynamic = ไม่บังคับ
        for m in v.dynamic:
            top = m.split(".")[0]
            if top not in local and not is_stdlib(top) and top not in pkgs and top != "PyInstaller":
                pkgs[top] = {"optional": True, "file": _rel(root, p)}
    plist = [{"module": "PyInstaller", "pip": "pyinstaller", "required": True, "desc": "ตัว build EXE"}]
    for top in sorted(pkgs, key=lambda t: (pkgs[t]["optional"], t.lower())):
        d = pkgs[top]
        plist.append({"module": top, "pip": IMPORT_TO_PIP.get(top, top),
                      "required": not d["optional"],
                      "desc": ("ไม่บังคับ · " if d["optional"] else "") + "พบใน " + d["file"]})
    cfg["python_packages"] = plist
    nreq = sum(1 for d in pkgs.values() if not d["optional"])
    rep.append((OK, f"ไลบรารีภายนอก {len(pkgs)} ตัว (จำเป็น {nreq} · ไม่บังคับ {len(pkgs) - nreq}): "
                + (", ".join(sorted(pkgs)) or "ไม่มี")))
    if os.path.isfile(os.path.join(root, "requirements.txt")):
        cfg["requirements_file"] = "requirements.txt"
        rep.append((OK, "พบ requirements.txt — จะติดตั้งจากไฟล์นี้ก่อน"))

    consts_pre = {c for v, _ in analyses.values() for c in v.consts}
    hidden = set()
    for top, d in pkgs.items():
        if d["optional"]:
            hidden.add(top)           # import ใน try/except — ใส่ hidden-import กันพลาด
    for v, _ in analyses.values():
        hidden |= {m for m in v.dynamic if m.split(".")[0] not in local}
    for c in consts_pre:                  # "backend.main:app" (uvicorn/gunicorn) → module ที่โหลดด้วยข้อความ
        m = re.fullmatch(r"([A-Za-z_]\w*(?:\.\w+)*):[A-Za-z_]\w*", c)
        if m and m.group(1).split(".")[0] in local:
            hidden.add(m.group(1))
    cfg["hidden_imports"] = sorted(hidden)
    cfg["collect_all"] = sorted(t for t in pkgs if t in COLLECT_ALL)
    if cfg["collect_all"]:
        rep.append((OK, "แนบไฟล์ข้อมูลของแพ็กเกจ: " + ", ".join(cfg["collect_all"])))

    # ── ไฟล์ข้อมูล / โฟลเดอร์ทรัพยากร ──
    consts = set()
    for v, _ in analyses.values():
        consts |= v.consts
    consts_n = {c.replace("\\", "/") for c in consts}
    data_dirs = []
    for d in sorted(os.listdir(root)):
        full = os.path.join(root, d)
        if not os.path.isdir(full) or d.startswith(".") or d in SKIP_DIRS:
            continue
        has_files = any(fn for _dp, _dn, fns in os.walk(full) for fn in fns if not fn.endswith((".py", ".pyc")))
        if not has_files:
            continue
        referenced = any(c == d or c.startswith(d + "/") for c in consts_n)
        if d.lower() in ALWAYS_DIRS or (referenced and d not in local):
            data_dirs.append(d)
    data = [f"{d};{d}" for d in data_dirs]
    seen_files = []
    for c in sorted(consts_n):
        if c.startswith("/") or ".." in c or ":" in c[:3] or not c:
            continue
        ext = os.path.splitext(c)[1].lower()
        if ext not in DATA_EXT or not os.path.isfile(os.path.join(root, c)):
            continue
        if c.split("/")[0] in SKIP_DIRS or any(c.startswith(d + "/") for d in data_dirs):
            continue
        dest = os.path.dirname(c) or "."
        data.append(f"{c};{dest}")
        seen_files.append(c)
    cfg["add_data"] = data
    if data:
        rep.append((OK, "ไฟล์ข้อมูลที่จะแนบ: " + ", ".join(x.split(";")[0] for x in data)))
    else:
        rep.append((SKIP, "ไม่พบไฟล์ข้อมูลที่โค้ดอ้างอิง"))

    # ── ไอคอน (ถ้ามีไฟล์ในโปรเจกต์ก็ใช้ ไม่มีก็ข้าม) ──
    ic = find_icon(root, name)
    cfg["icon"] = ic
    rep.append(icon_report(ic))
    cfg["required_files"] = [entry_rel] + ([ic] if ic else [])

    # ── binary ที่วางไว้ข้างสคริปต์ ──
    first_found, add_bin = [], []
    for f in sorted(os.listdir(root)):
        low = f.lower()
        if not os.path.isfile(os.path.join(root, f)) or not low.endswith((".exe", ".dll")):
            continue
        if "setup" in low or "unins" in low:
            continue
        if low in ("7za.exe", "7zr.exe"):
            if not first_found:
                first_found.append(["7za.exe", "7zr.exe"])
        else:
            add_bin.append(f"{f};.")
    cfg["add_binary_first_found"] = first_found
    cfg["add_binary"] = add_bin
    if first_found or add_bin:
        rep.append((OK, "จะแนบ binary: " + ", ".join(
            ["7za.exe/7zr.exe"] * bool(first_found) + [b.split(";")[0] for b in add_bin])))

    # ── เครื่องมือเสริมที่โค้ดเรียกใช้ ──
    used = {_norm_cmd(c) for c in consts}
    tools = []
    for t in KNOWN_TOOLS:
        if (used & set(t["aliases"])) or (t.get("needs_pkg") and t["needs_pkg"] in pkgs):
            tools.append({k: v for k, v in t.items() if k not in ("aliases", "needs_pkg")})
    cfg["external_tools"] = tools
    if tools:
        rep.append((OK, "เครื่องมือเสริมที่โค้ดเรียกใช้: " + ", ".join(t["name"] for t in tools)))
    else:
        rep.append((SKIP, "ไม่พบการเรียกเครื่องมือภายนอก"))

    # ── ตัวติดตั้ง .iss ──
    iss = sorted(f for f in os.listdir(root) if f.lower().endswith(".iss"))
    if iss:
        inst = {"enabled": True, "iss_file": iss[0]}
        try:
            with open(os.path.join(root, iss[0]), encoding="utf-8-sig", errors="replace") as f:
                txt = f.read()
            m = re.search(r"^\s*OutputDir\s*=\s*(.+?)\s*$", txt, re.M)
            if m and "{" not in m.group(1):
                inst["output_dir"] = m.group(1).replace("\\", "/")
            m = re.search(r"^\s*OutputBaseFilename\s*=\s*(.+?)\s*$", txt, re.M)
            if m and "{" not in m.group(1):
                inst["output_glob"] = m.group(1) + ".exe"
        except OSError:
            pass
        cfg["installer"] = inst
        rep.append((OK, f"พบไฟล์ตัวติดตั้ง: {iss[0]}"))
    else:
        rep.append((SKIP, "ไม่พบไฟล์ .iss — ไม่สร้างตัวติดตั้ง"))

    for hint in ("run.bat", "run.cmd"):
        if os.path.isfile(os.path.join(root, hint)):
            cfg["help_hints"] = {"run_without_build": hint}
            break
    return cfg, rep


def merge_cfg(base, over):
    for k, v in over.items():
        if k.startswith("_"):
            continue                      # คีย์ที่ขึ้นต้นด้วย _ = คอมเมนต์
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k].update(v)
        else:
            base[k] = v


# ═══ ระบบ log: hook ใน EXE + ตัววิเคราะห์ ═══════════════════════
# โค้ดนี้ถูกใส่เข้า EXE ตอน build (--runtime-hook) เพื่อให้โปรแกรมเขียน log ตัวเองลงไฟล์
RUNTIME_HOOK = r"""
import sys, os, time, traceback

def _autobuild_setup():
    if not getattr(sys, "frozen", False):
        return
    try:
        base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
        d = os.path.join(base, "__APP__", "logs")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "app.log")
        try:
            if os.path.getsize(p) > 2 * 1024 * 1024:
                os.replace(p, os.path.join(d, "app.old.log"))
        except OSError:
            pass
        f = open(p, "a", buffering=1, encoding="utf-8", errors="replace")
    except Exception:
        return

    class _Tee:
        encoding = "utf-8"
        def __init__(self, orig):
            self.o = orig
        def write(self, s):
            try:
                f.write(s)
            except Exception:
                pass
            if self.o is not None:
                try:
                    self.o.write(s)
                except Exception:
                    pass
            return len(s) if isinstance(s, str) else 0
        def flush(self):
            try:
                f.flush()
            except Exception:
                pass
            if self.o is not None:
                try:
                    self.o.flush()
                except Exception:
                    pass
        def isatty(self):
            return False

    sys.stdout = _Tee(sys.stdout)
    sys.stderr = _Tee(sys.stderr)
    stamp = lambda: time.strftime("%Y-%m-%d %H:%M:%S")
    f.write("\n===== START %s | python %s | meipass=%s | argv=%s =====\n" % (
        stamp(), sys.version.split()[0], getattr(sys, "_MEIPASS", ""), sys.argv))

    def _hook(t, v, tb):
        try:
            f.write("".join(traceback.format_exception(t, v, tb)))
            f.flush()
        except Exception:
            pass
    sys.excepthook = _hook
    try:
        import threading
        threading.excepthook = lambda a: _hook(a.exc_type, a.exc_value, a.exc_traceback)
    except Exception:
        pass
    try:
        import faulthandler
        faulthandler.enable(f)
    except Exception:
        pass
    try:
        import atexit
        atexit.register(lambda: f.write("===== EXIT %s =====\n" % stamp()))
    except Exception:
        pass

_autobuild_setup()
"""

_PLATFORM_ONLY = {"org", "java", "jnius", "android", "vms_lib", "_scproxy", "asyncio.DefaultEventLoopPolicy"}


def runtime_log_path():
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, CFG.get("app_name", "App"), "logs", "app.log")


def _read_from(path, offset=0):
    try:
        if os.path.getsize(path) < offset:
            offset = 0                       # ไฟล์ถูก rotate
        with open(path, "rb") as f:
            f.seek(offset)
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def _last_session(text):
    i = text.rfind("===== START")
    return text[i:] if i >= 0 else text


def analyze_log(text):
    """อ่านข้อความ log → รายการสิ่งที่พบ [{kind, ...}]"""
    out, seen = [], set()

    def add(kind, **kw):
        key = (kind, tuple(sorted(kw.items())))
        if key not in seen:
            seen.add(key)
            out.append({"kind": kind, **kw})

    for m in re.finditer(r"No module named ['\"]([\w\.]+)['\"]", text):
        add("missing_module", module=m.group(1))
    if re.search(r"DLL load failed|Failed to load Python DLL", text):
        add("dll")
    for m in re.finditer(r"(?:FileNotFoundError|No such file or directory)[^\n]*?['\"]([^'\"\n]+)['\"]", text):
        add("missing_file", path=m.group(1))
    if re.search(r"WinError 10048|address already in use|Errno 98", text, re.I):
        add("port_busy")
    if "webview2" in text.lower():
        add("webview2")
    if "Traceback (most recent call last)" in text:
        excs = re.findall(r"^([A-Za-z_][\w\.]*(?:Error|Exception)): ?(.*)$", text, re.M)
        for n, msg in excs[-3:]:
            add("exception", name=n, msg=msg[:160])
    return out


def show_findings(findings):
    hints = {
        "dll": "DLL โหลดไม่ได้ — มักขาด Visual C++ Redistributable หรือไลบรารี/เครื่องมือเสริมบางตัว",
        "port_busy": "พอร์ตถูกใช้อยู่ — ปิดโปรแกรมที่เปิดค้างไว้ หรือเปลี่ยนพอร์ตในโค้ด",
        "webview2": "พบข้อความเกี่ยวกับ WebView2 — เครื่องต้องมี Microsoft Edge WebView2 Runtime",
    }
    for f in findings:
        k = f["kind"]
        if k == "missing_module":
            say(f"✗ โมดูลที่หาไม่เจอ: {f['module']}", R)
        elif k == "missing_file":
            say(f"✗ ไฟล์ที่หาไม่เจอ: {f['path']}", R)
            say("    ถ้าเป็นไฟล์ของโปรเจกต์ → เพิ่มใน autobuild.json คีย์ extra_add_data เช่น \"โฟลเดอร์;โฟลเดอร์\"", D)
        elif k == "exception":
            say(f"✗ ข้อผิดพลาด: {f['name']}: {f['msg']}", R)
        else:
            say("✗ " + hints.get(k, k), Y)


def _save_learned(key, items):
    """บันทึกสิ่งที่เรียนรู้ลง autobuild.json (คีย์ extra_*) โดยไม่แตะค่าอื่นที่ผู้ใช้เขียนไว้"""
    new = []
    if CFG_PATH:
        data = {}
        if os.path.isfile(CFG_PATH):
            try:
                with open(CFG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                data = {}
        cur = data.get(key, [])
        new = [i for i in items if i not in cur]
        if new:
            data[key] = cur + new
            data.setdefault("_comment", "สคริปต์เรียนรู้เพิ่มคีย์ extra_* ให้เอง · แก้หรือลบได้")
            with open(CFG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    for i in items:
        if i not in CFG[key]:
            CFG[key].append(i)
    return new


def apply_fixes(findings):
    """แก้อัตโนมัติจากผลวิเคราะห์ log · คืนรายการข้อความที่แก้ (ว่าง = ไม่มีอะไรให้แก้)"""
    done = []
    if not CFG.get("auto_fix", True):
        return done
    hidden = []
    for f in findings:
        if f["kind"] != "missing_module":
            continue
        mod = f["module"]
        top = mod.split(".")[0]
        if mod in CFG["hidden_imports"] or mod in CFG["extra_hidden_imports"]:
            continue                         # เคยใส่แล้วแต่ยังพัง — ไม่วนซ้ำ ให้คนดู log
        local_hit = os.path.exists(here(top)) or os.path.exists(here(top + ".py"))
        if has_module(top) or local_hit:
            hidden.append(mod)
        elif not is_stdlib(top):
            pipname = IMPORT_TO_PIP.get(top, top)
            rc, _ = _pip_install([pipname])
            if rc == 0:
                done.append(f"ติดตั้ง {pipname} (ขาดโมดูล {top})")
                hidden.append(mod)
            else:
                say(f"ติดตั้ง {pipname} อัตโนมัติไม่สำเร็จ — ลอง pip install {pipname} เอง", Y)
    for m in _save_learned("extra_hidden_imports", hidden):
        done.append(f"เพิ่ม hidden-import: {m}  (บันทึกใน autobuild.json)")
    return done


def collect_warn(workdir, name):
    """อ่านไฟล์ warn ของ PyInstaller → โมดูลที่หาไม่เจอแบบ top-level (เสี่ยง EXE พัง)"""
    p = os.path.join(workdir, name, f"warn-{name}.txt")
    if not os.path.isfile(p):
        return []
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
        os.makedirs(here("logs"), exist_ok=True)
        with open(here("logs", "build_warn_last.txt"), "w", encoding="utf-8") as f:
            f.write(txt)
    except OSError:
        return []
    miss = []
    for m in re.finditer(r"^missing module named (\S+) - imported by (.+)$", txt, re.M):
        mod, by = m.group(1).strip("'\""), m.group(2)
        top = mod.split(".")[0]
        if "(top-level)" in by and not is_stdlib(top) and top not in _PLATFORM_ONLY:
            miss.append(mod)
    return sorted(set(miss))


# ═══ ไอคอน: ถ้ามีไฟล์ในโปรเจกต์ก็ใช้ ถ้าไม่มีก็ข้าม ═══════════════
ICON_SKIP_DIRS = {"node_modules", ".git", "venv", ".venv", "env", "__pycache__", "target", "dist", "obj",
                  "bin", "out", "release", ".gradle", ".dart_tool", "site-packages", "docs", "doc", "test",
                  "tests", "examples", "samples", "screenshots", "installer_output", "logs"}
ICON_DIR_HINTS = {"icons", "icon", "assets", "resources", "resource", "res", "images", "img",
                  "build", "public", "static", "branding"}


def _png_size(path):
    try:
        with open(path, "rb") as f:
            h = f.read(24)
        if h[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", h[16:24])
    except (OSError, struct.error):
        pass
    return None


def find_icon(root, name_hint=""):
    """หาไอคอนในโปรเจกต์ (โฟลเดอร์หลัก + โฟลเดอร์ย่อยลึกไม่เกิน 3 ชั้น) → path แบบ relative หรือ None"""
    if os.name == "nt":
        pref = (".ico", ".png")
    elif sys.platform == "darwin":
        pref = (".icns", ".png")
    else:
        pref = (".png", ".ico")
    hint = re.sub(r"\W+", "", (name_hint or "").lower())
    best, best_score = None, -999
    for dp, dns, fns in os.walk(root):
        rel_dir = os.path.relpath(dp, root).replace(os.sep, "/")
        depth = 0 if rel_dir == "." else rel_dir.count("/") + 1
        base = os.path.basename(dp).lower()
        dns[:] = [d for d in dns if d.lower() not in ICON_SKIP_DIRS and not d.startswith(".")
                  and not os.path.isfile(os.path.join(dp, d, "pyvenv.cfg"))]
        if depth >= 3 or base == "build":          # build/ = ดูแค่ไฟล์ชั้นแรก (กันไฟล์ชั่วคราวของ PyInstaller)
            dns[:] = []
        for fn in fns:
            stem, ext = os.path.splitext(fn)
            ext = ext.lower()
            if ext not in pref:
                continue
            p = os.path.join(dp, fn)
            score = 20 - 10 * pref.index(ext)
            if ext == ".png":
                sz = _png_size(p)
                if not sz or sz[0] != sz[1] or sz[0] < 64:
                    continue                        # PNG ต้องเป็นสี่เหลี่ยมจัตุรัส ≥ 64px
                score += min(sz[0], 512) / 256.0
            s = stem.lower()
            score += 6 if "icon" in s else 0
            score += 3 if "logo" in s else 0
            score += 2 if "app" in s else 0
            score += 3 if hint and hint in re.sub(r"\W+", "", s) else 0
            score -= 5 if s.startswith("favicon") else 0
            score -= 2 * depth
            score += 1 if base in ICON_DIR_HINTS else 0
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            if score > best_score or (score == best_score and best and len(rel) < len(best)):
                best, best_score = rel, score
    return best


def resolve_icon(need=".ico"):
    """ไอคอนที่พร้อมใช้ตอน build (แปลง PNG → ICO ให้ถ้าจำเป็น) → path แบบ relative หรือ None (= ข้าม)"""
    ic = CFG.get("icon")
    if not ic:
        return None
    p = here(ic)
    if not os.path.isfile(p):
        say(f"ไม่พบไฟล์ไอคอน {ic} — ข้ามไอคอน", D)
        return None
    ext = os.path.splitext(p)[1].lower()
    if need is None or ext == need:
        return ic.replace("\\", "/")
    if ext == ".png" and need == ".ico":
        try:
            from PIL import Image
        except ImportError:
            say("แปลง PNG เป็น .ico ต้องใช้ Pillow — กำลังติดตั้ง", D)
            _pip_install(["pillow"])
            try:
                from PIL import Image
            except ImportError:
                say("ติดตั้ง Pillow ไม่ได้ — ข้ามไอคอน", Y)
                return None
        try:
            os.makedirs(here("logs"), exist_ok=True)
            out = here("logs", "app_icon.ico")
            Image.open(p).convert("RGBA").save(
                out, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            say(f"แปลง {ic} → logs/app_icon.ico แล้ว", D)
            return "logs/app_icon.ico"
        except Exception as ex:
            say(f"แปลงไอคอนไม่สำเร็จ ({type(ex).__name__}) — ข้ามไอคอน", Y)
            return None
    say(f"ไอคอน {ic} เป็นชนิดที่ build นี้ใช้ไม่ได้ — ข้ามไอคอน", D)
    return None


def icon_report(ic):
    """ข้อความรายงานไอคอนสำหรับขั้นสแกน"""
    if not ic:
        return (SKIP, "ไม่พบไฟล์ไอคอน (.ico/.png) — ข้าม ใช้ไอคอนเริ่มต้น")
    note = ""
    if ic.lower().endswith(".png") and os.name == "nt":
        note = "  (PNG → จะแปลงเป็น .ico ตอน build)"
    return (OK, f"ไอคอน: {ic}{note}")


# ═══ รองรับหลายภาษา/หลายเฟรมเวิร์ก ══════════════════════════════
LABELS = {
    "python": "Python (PyInstaller)", "electron": "Electron (Node.js)", "tauri": "Tauri (Rust + เว็บ)",
    "flutter": "Flutter", "dotnet": ".NET (C#/F#/VB)", "rust": "Rust (cargo)", "go": "Go",
    "java": "Java (Maven/Gradle)", "cmake": "C/C++ (CMake)", "node-cli": "Node.js CLI (pkg)",
    "node-web": "เว็บ Node.js (npm run build)",
}
PRIORITY = ["tauri", "electron", "flutter", "dotnet", "rust", "go", "java", "cmake",
            "python", "node-cli", "node-web"]
STRONG = set(PRIORITY[:9])               # ชนิดที่ถือว่า "ชัดเจน" — ถ้าเจอหลายชนิดจะถามให้เลือก

# เครื่องมือ build ของแต่ละภาษา (ติดตั้งผ่าน winget ได้ — ถามก่อนเสมอ)
TOOLCHAINS = {
    "node": {"name": "Node.js", "desc": "รัน/build โปรเจกต์ JavaScript", "winget_id": "OpenJS.NodeJS.LTS",
             "commands": ["node"], "paths": [r"C:\Program Files\nodejs\node.exe"]},
    "go": {"name": "Go", "desc": "คอมไพล์โปรเจกต์ Go", "winget_id": "GoLang.Go",
           "commands": ["go"], "paths": [r"C:\Program Files\Go\bin\go.exe"]},
    "rust": {"name": "Rust (cargo)", "desc": "คอมไพล์โปรเจกต์ Rust", "winget_id": "Rustlang.Rustup",
             "commands": ["cargo"], "paths": [r"%USERPROFILE%\.cargo\bin\cargo.exe"],
             "after_install": "ถ้ายังไม่พบ cargo ให้เปิดเทอร์มินัลใหม่ หรือรัน  rustup default stable  "
                              "(บน Windows ต้องมี Visual Studio Build Tools แบบ C++ ด้วย)"},
    "dotnet": {"name": ".NET SDK", "desc": "build โปรเจกต์ .NET", "winget_id": "Microsoft.DotNet.SDK.8",
               "commands": ["dotnet"], "paths": [r"C:\Program Files\dotnet\dotnet.exe"]},
    "jdk": {"name": "JDK", "desc": "คอมไพล์โปรเจกต์ Java", "winget_id": "EclipseAdoptium.Temurin.21.JDK",
            "commands": ["javac"],
            "globs": [r"C:\Program Files\Eclipse Adoptium\jdk-*\bin\javac.exe",
                      r"C:\Program Files\Java\jdk*\bin\javac.exe", r"%JAVA_HOME%\bin\javac.exe"]},
    "maven": {"name": "Maven", "desc": "build โปรเจกต์ Maven (ถ้าไม่มี mvnw)", "winget_id": "Apache.Maven",
              "commands": ["mvn"],
              "globs": [r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Apache.Maven*\apache-maven-*\bin\mvn.cmd"]},
    "gradle": {"name": "Gradle", "desc": "build โปรเจกต์ Gradle (ถ้าไม่มี gradlew)", "winget_id": "Gradle.Gradle",
               "commands": ["gradle"]},
    "cmake": {"name": "CMake", "desc": "build โปรเจกต์ C/C++", "winget_id": "Kitware.CMake",
              "commands": ["cmake"], "paths": [r"C:\Program Files\CMake\bin\cmake.exe"],
              "after_install": "บน Windows ต้องมี Visual Studio Build Tools แบบ C++ ด้วย"},
    "flutter": {"name": "Flutter SDK", "desc": "build แอป Flutter", "winget_id": None,
                "commands": ["flutter"],
                "paths": [r"C:\src\flutter\bin\flutter.bat", r"%USERPROFILE%\flutter\bin\flutter.bat",
                          r"%USERPROFILE%\dev\flutter\bin\flutter.bat"],
                "manual": "ติดตั้งเองตามคู่มือ https://docs.flutter.dev/get-started/install"},
}
EXTRA_PATH = []          # โฟลเดอร์ของเครื่องมือที่เพิ่งติดตั้ง (ใส่ PATH ให้คำสั่ง build)
BUILT_EXE = ""           # EXE ที่ builder ทั่วไปสร้างได้
_LOG_STARTED = False


def _tools(*keys):
    out = []
    for k in keys:
        t = dict(TOOLCHAINS[k])
        t["required"] = True
        out.append(t)
    return out


def _is_generic():
    return CFG.get("project_type", "python") != "python"


def _safe_name(s, fallback="App"):
    return re.sub(r"[^\w\-\.]+", "_", s or "").strip("_") or fallback


def _read_text(p):
    try:
        with open(p, "r", encoding="utf-8-sig", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _read_json(p):
    try:
        return json.loads(_read_text(p))
    except ValueError:
        return {}


def _plat():
    return "win" if os.name == "nt" else ("macos" if sys.platform == "darwin" else "linux")


def _pm(root):
    for lock, pm in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn")):
        if os.path.isfile(os.path.join(root, lock)) and shutil.which(pm):
            return pm
    return "npm"


def _toml_field(text, field, section="package"):
    m = re.search(r"^\[" + re.escape(section) + r"\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not m:
        return None
    f = re.search(r"^\s*" + re.escape(field) + r"\s*=\s*\"([^\"]+)\"", m.group(1), re.M)
    return f.group(1) if f else None


_WEB_FW = {"vite", "react-scripts", "next", "nuxt", "vue", "svelte", "@angular/core", "webpack",
           "parcel", "astro", "gatsby", "@sveltejs/kit"}
_ELECTRON_KEYS = {"electron", "electron-builder", "@electron-forge/cli", "electron-packager", "@electron/packager"}
_DOTNET_SKIP = {"bin", "obj", "node_modules", ".git", "packages", "dist", "venv", ".venv"}


def _find_dotnet_projects(root):
    """หาไฟล์ .csproj/.fsproj/.vbproj ที่สร้างเป็นโปรแกรม (ไม่ใช่ไลบรารี) → [(path, info)]"""
    out = []
    for dp, dns, fns in os.walk(root):
        rel = os.path.relpath(dp, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        dns[:] = [d for d in dns if d.lower() not in _DOTNET_SKIP and not d.startswith(".")]
        if depth >= 3:
            dns[:] = []
        for fn in fns:
            if not fn.lower().endswith((".csproj", ".fsproj", ".vbproj")):
                continue
            p = os.path.join(dp, fn)
            txt = _read_text(p)
            m = re.search(r"<OutputType>\s*(\w+)\s*</OutputType>", txt, re.I)
            otype = m.group(1) if m else ""
            web = re.search(r'Sdk="Microsoft\.NET\.Sdk\.(Web|Worker)"', txt) is not None
            if otype.lower() not in ("exe", "winexe") and not web:
                continue
            g = lambda tag: (re.search(r"<" + tag + r">\s*([^<]+?)\s*</" + tag + ">", txt) or [None, None])[1]
            out.append((p, {
                "otype": otype or "Exe", "assembly": g("AssemblyName"), "version": g("Version"),
                "tfm": g("TargetFramework") or (g("TargetFrameworks") or "").split(";")[0],
                "has_icon": "<ApplicationIcon>" in txt,
            }))
    out.sort(key=lambda x: (0 if x[1]["otype"].lower() == "winexe" else 1, x[0]))
    return out


def detect_projects(root):
    """ตรวจชนิดโปรเจกต์จากไฟล์หลัก (manifest) → [(ชนิด, info)] เรียงตามความสำคัญ"""
    found = {}
    pj_path = os.path.join(root, "package.json")
    pj = _read_json(pj_path) if os.path.isfile(pj_path) else None
    deps = {}
    if pj is not None:
        deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})}
    if os.path.isfile(os.path.join(root, "src-tauri", "Cargo.toml")):
        found["tauri"] = {}
    if pj is not None and "tauri" not in found and _ELECTRON_KEYS & set(deps):
        found["electron"] = {}
    pub = _read_text(os.path.join(root, "pubspec.yaml"))
    if pub and re.search(r"^\s*sdk:\s*flutter\s*$", pub, re.M):
        found["flutter"] = {}
    dn = _find_dotnet_projects(root)
    if dn:
        found["dotnet"] = {"projects": dn}
    if os.path.isfile(os.path.join(root, "Cargo.toml")) and "tauri" not in found:
        found["rust"] = {}
    if os.path.isfile(os.path.join(root, "go.mod")):
        found["go"] = {}
    if any(os.path.isfile(os.path.join(root, f)) for f in ("pom.xml", "build.gradle", "build.gradle.kts")):
        found["java"] = {}
    if os.path.isfile(os.path.join(root, "CMakeLists.txt")):
        found["cmake"] = {}
    if any(True for _ in _iter_py(root)):
        found["python"] = {}
    if pj is not None and "electron" not in found and "tauri" not in found:
        scripts = pj.get("scripts") or {}
        if pj.get("bin"):
            found["node-cli"] = {}
        elif "build" in scripts:
            found["node-web"] = {}
    return [(t, found[t]) for t in PRIORITY if t in found]


def _plan_base(root, ptype, name, version, gui, tools, builder, manifest, rep):
    """ประกอบ config ส่วนกลางของ builder ทุกชนิด"""
    cfg = {"project_type": ptype, "app_name": _safe_name(name, os.path.basename(root) or "App"),
           "version": version or "1.0", "windowed": gui, "external_tools": tools,
           "builder": builder, "required_files": manifest, "entry_script": "", "python_packages": []}
    rep.append((OK, f"ชื่อแอป: {cfg['app_name']}   เวอร์ชัน: {cfg['version']}"))
    ic = find_icon(root, cfg["app_name"])
    cfg["icon"] = ic
    rep.append(icon_report(ic))
    if builder.get("icon_note") and ic:
        rep.append((WARN, builder["icon_note"]))
    rep.append((OK, "จะรัน: " + " → ".join(" ".join(c[:4]) + (" …" if len(c) > 4 else "")
                                           for c in (builder.get("deps", []) + builder["build"]))))
    rep.append((OK, "เครื่องมือ build ที่ต้องมี: " + ", ".join(t["name"] for t in tools)))
    iss = sorted(f for f in os.listdir(root) if f.lower().endswith(".iss"))
    if iss:
        cfg["installer"] = {"enabled": True, "iss_file": iss[0]}
        rep.append((OK, f"พบไฟล์ตัวติดตั้ง: {iss[0]}"))
    for hint in ("run.bat", "run.cmd"):
        if os.path.isfile(os.path.join(root, hint)):
            cfg["help_hints"] = {"run_without_build": hint}
            break
    return cfg, rep


def _plan_electron(root, info):
    rep = []
    pj = _read_json(os.path.join(root, "package.json"))
    scripts = pj.get("scripts") or {}
    name = pj.get("productName") or (pj.get("build") or {}).get("productName") or pj.get("name") or os.path.basename(root)
    name = _safe_name(name)
    pm = _pm(root)
    pack = next((s for s in ("dist", "package", "make", "pack", "dist:win", "build:win",
                             "electron:build", "build:electron") if s in scripts), None)
    plat = {"win": "win32", "macos": "darwin", "linux": "linux"}[_plat()]
    if pack:
        build = [[pm, "run", pack]]
        rep.append((OK, f"ใช้สคริปต์แพ็กเกจของโปรเจกต์: {pm} run {pack}"))
    else:
        build = ([[pm, "run", "build"]] if "build" in scripts else []) + [[
            "npx", "--yes", "@electron/packager", ".", name, f"--platform={plat}", "--arch=x64",
            "--out=dist", "--overwrite", "--ignore=^/dist", "--icon={ICON_ICO}"]]
        rep.append((OK, "ไม่พบสคริปต์แพ็กเกจ — ใช้ @electron/packager แพ็กเกจให้"))
    builder = {"label": LABELS["electron"], "deps": [[pm, "install"]], "build": build, "gui": True,
               "out_dirs": ["dist", "out", "release"], "out_depth": 3, "exe_names": [name.lower()],
               "installer_dirs": ["dist", "out", "release"], "expect_exe": True}
    return _plan_base(root, "electron", name, pj.get("version"), True, _tools("node"), builder,
                      ["package.json"], rep)


def _plan_tauri(root, info):
    rep = []
    conf = _read_json(os.path.join(root, "src-tauri", "tauri.conf.json"))
    cargo = _read_text(os.path.join(root, "src-tauri", "Cargo.toml"))
    cname = _toml_field(cargo, "name") or "app"
    pname = conf.get("productName") or (conf.get("package") or {}).get("productName") or cname
    version = conf.get("version") or (conf.get("package") or {}).get("version") or _toml_field(cargo, "version")
    has_pj = os.path.isfile(os.path.join(root, "package.json"))
    pm = _pm(root)
    scripts = (_read_json(os.path.join(root, "package.json")).get("scripts") or {}) if has_pj else {}
    if has_pj and "tauri" in scripts:
        build = [[pm, "run", "tauri", "--", "build"]]
    elif has_pj:
        build = [["npx", "--yes", "@tauri-apps/cli", "build"]]
    else:
        build = [["cargo", "tauri", "build"]]
        rep.append((WARN, "ไม่มี package.json — ต้องติดตั้ง tauri-cli เอง (cargo install tauri-cli)"))
    builder = {"label": LABELS["tauri"], "deps": [[pm, "install"]] if has_pj else [], "build": build,
               "gui": True, "out_dirs": ["src-tauri/target/release"], "out_depth": 0,
               "exe_names": [cname.lower(), _safe_name(pname).lower()],
               "installer_dirs": ["src-tauri/target/release/bundle"], "expect_exe": True,
               "icon_note": "Tauri ใช้ไอคอนใน src-tauri/icons ตามค่าของโปรเจกต์ (ไม่ฝังซ้ำให้)"}
    tools = _tools("rust") + (_tools("node") if has_pj else [])
    return _plan_base(root, "tauri", pname, version, True, tools, builder,
                      ["src-tauri/Cargo.toml"], rep)


def _plan_flutter(root, info):
    rep = []
    pub = _read_text(os.path.join(root, "pubspec.yaml"))
    name = (re.search(r"^name:\s*(\S+)", pub, re.M) or [None, os.path.basename(root)])[1]
    ver = (re.search(r"^version:\s*(\S+)", pub, re.M) or [None, "1.0"])[1].split("+")[0]
    target = {"win": "windows", "macos": "macos", "linux": "linux"}[_plat()]
    builder = {"label": LABELS["flutter"], "deps": [["flutter", "pub", "get"]],
               "build": [["flutter", "build", target, "--release"]], "gui": True,
               "out_dirs": ["build/windows/x64/runner/Release", "build/windows/runner/Release",
                            "build/linux/x64/release/bundle"], "out_depth": 0,
               "exe_names": [name.lower()], "expect_exe": True,
               "icon_note": "Flutter ใช้ไอคอนใน windows/runner/resources ตามค่าของโปรเจกต์ (ไม่ฝังซ้ำให้)"}
    return _plan_base(root, "flutter", name, ver, True, _tools("flutter"), builder, ["pubspec.yaml"], rep)


def _plan_dotnet(root, info):
    rep = []
    projs = info.get("projects") or _find_dotnet_projects(root)
    if not projs:
        return {}, [(FAIL, "ไม่พบโปรเจกต์ .NET ที่สร้างเป็นโปรแกรม (Exe/WinExe)")]
    pick = projs[0]
    if len(projs) > 1:
        opts = {str(i + 1): _rel(root, p) for i, (p, _) in enumerate(projs[:6])}
        if not ASSUME_YES:
            say("พบโปรเจกต์ .NET ที่เป็นโปรแกรมหลายตัว — เลือกตัวที่จะ build", Y)
            ch = ask_choice("โปรเจกต์คือ", opts)
            pick = projs[int(ch) - 1] if ch in opts else projs[0]
    proj, meta = pick
    rel = _rel(root, proj)
    rep.append((OK, f"โปรเจกต์ที่จะ build: {rel}"))
    name = meta["assembly"] or os.path.splitext(os.path.basename(proj))[0]
    rid = {"win": "win-x64", "macos": "osx-x64", "linux": "linux-x64"}[_plat()]
    icon_arg = [] if (meta["has_icon"] or os.name != "nt") else ["-p:ApplicationIcon={ICON_ICO}"]
    if (meta["tfm"] or "").lower().startswith("net4"):
        build = [["dotnet", "build", rel, "-c", "Release", "-o", "dist/publish"] + icon_arg]
        rep.append((WARN, ".NET Framework — build แบบปกติ (ไม่รวม runtime ในไฟล์เดียว)"))
    else:
        build = [["dotnet", "publish", rel, "-c", "Release", "-r", rid, "--self-contained", "true",
                  "-p:PublishSingleFile=true", "-p:IncludeNativeLibrariesForSelfExtract=true",
                  "-o", "dist/publish"] + icon_arg]
    builder = {"label": LABELS["dotnet"], "deps": [], "build": build,
               "gui": meta["otype"].lower() == "winexe", "out_dirs": ["dist/publish"], "out_depth": 0,
               "exe_names": [name.lower()], "expect_exe": True,
               "icon_note": ("โปรเจกต์กำหนดไอคอนเองอยู่แล้ว (ApplicationIcon) — ไม่ทับให้" if meta["has_icon"] else "")}
    return _plan_base(root, "dotnet", name, meta["version"], builder["gui"], _tools("dotnet"), builder, [rel], rep)


def _plan_rust(root, info):
    rep = []
    cargo = _read_text(os.path.join(root, "Cargo.toml"))
    name = _toml_field(cargo, "name") or os.path.basename(root)
    ver = _toml_field(cargo, "version")
    if not _toml_field(cargo, "name"):
        rep.append((WARN, "Cargo.toml เป็น workspace — จะ build ทุกโปรแกรมในนั้น"))
    main_rs = _read_text(os.path.join(root, "src", "main.rs"))
    gui = "windows_subsystem" in main_rs and '"windows"' in main_rs
    builder = {"label": LABELS["rust"], "deps": [], "build": [["cargo", "build", "--release"]], "gui": gui,
               "out_dirs": ["target/release"], "out_depth": 0,
               "exe_names": [name.lower(), name.lower().replace("-", "_")], "expect_exe": True,
               "icon_note": "Rust ฝังไอคอนต้องตั้งค่า build.rs (winres/embed-resource) เอง — ยังไม่ฝังให้อัตโนมัติ"}
    return _plan_base(root, "rust", name, ver, gui, _tools("rust"), builder, ["Cargo.toml"], rep)


def _plan_go(root, info):
    rep = []
    mod = _read_text(os.path.join(root, "go.mod"))
    name = (re.search(r"^module\s+(\S+)", mod, re.M) or [None, os.path.basename(root)])[1].split("/")[-1]
    target = "."
    if not os.path.isfile(os.path.join(root, "main.go")):
        cmds = sorted(glob.glob(os.path.join(root, "cmd", "*", "main.go")))
        if cmds:
            target = "./cmd/" + os.path.basename(os.path.dirname(cmds[0]))
            if len(cmds) > 1:
                rep.append((WARN, f"พบโปรแกรมใน cmd/ หลายตัว — เลือก {target}"))
            name = os.path.basename(os.path.dirname(cmds[0]))
    gui = any(k in mod for k in ("fyne.io", "lxn/walk", "gioui.org", "webview", "wailsapp", "ebiten",
                                 "go-gl", "gotk3", "giu"))
    flags = "-s -w" + (" -H=windowsgui" if (gui and os.name == "nt") else "")
    name = _safe_name(name)
    out = "dist/" + name + (".exe" if os.name == "nt" else "")
    builder = {"label": LABELS["go"], "deps": [["go", "mod", "download"]],
               "build": [["go", "build", "-ldflags", flags, "-o", out, target]], "gui": gui,
               "out_dirs": ["dist"], "out_depth": 0, "exe_names": [name.lower()], "expect_exe": True,
               "icon_note": "Go ฝังไอคอนต้องใช้ไฟล์ .syso (rsrc/goversioninfo) เอง — ยังไม่ฝังให้อัตโนมัติ"}
    return _plan_base(root, "go", name, None, gui, _tools("go"), builder, ["go.mod"], rep)


def _plan_java(root, info):
    rep = []
    is_mvn = os.path.isfile(os.path.join(root, "pom.xml"))
    if is_mvn:
        pom = re.sub(r"<parent>.*?</parent>", "", _read_text(os.path.join(root, "pom.xml")), flags=re.S)
        name = (re.search(r"<artifactId>\s*([^<]+?)\s*</artifactId>", pom) or [None, os.path.basename(root)])[1]
        ver = (re.search(r"<version>\s*([^<]+?)\s*</version>", pom) or [None, None])[1]
        wrapper = "mvnw.cmd" if os.name == "nt" else "./mvnw"
        has_w = os.path.isfile(os.path.join(root, wrapper.lstrip("./")))
        build = [[wrapper if has_w else "mvn", "-q", "-DskipTests", "package"]]
        tools = _tools("jdk") + ([] if has_w else _tools("maven"))
        jar_dirs, manifest = ["target"], ["pom.xml"]
    else:
        gf = "build.gradle.kts" if os.path.isfile(os.path.join(root, "build.gradle.kts")) else "build.gradle"
        sett = _read_text(os.path.join(root, "settings.gradle")) + _read_text(os.path.join(root, "settings.gradle.kts"))
        name = (re.search(r"rootProject\.name\s*=\s*['\"]([^'\"]+)", sett) or [None, os.path.basename(root)])[1]
        ver = (re.search(r"^version\s*=?\s*['\"]([^'\"]+)", _read_text(os.path.join(root, gf)), re.M) or [None, None])[1]
        wrapper = "gradlew.bat" if os.name == "nt" else "./gradlew"
        has_w = os.path.isfile(os.path.join(root, wrapper.lstrip("./")))
        build = [[wrapper if has_w else "gradle", "build", "-x", "test"]]
        tools = _tools("jdk") + ([] if has_w else _tools("gradle"))
        jar_dirs, manifest = ["build/libs"], [gf]
    name = _safe_name(name)
    rep.append((OK, "ได้ไฟล์ .jar ก่อน แล้วพยายามห่อเป็น EXE ด้วย jpackage ถ้ามี (JDK 14+ และ JAR ระบุ Main-Class)"))
    builder = {"label": LABELS["java"], "deps": [], "build": build, "gui": False, "post": "java_package",
               "jar_dirs": jar_dirs, "artifact_globs": [d + "/*.jar" for d in jar_dirs],
               "out_dirs": ["dist"], "out_depth": 1, "exe_names": [name.lower()], "expect_exe": False,
               "launch_test": True}
    return _plan_base(root, "java", name, ver, False, tools, builder, manifest, rep)


def _plan_cmake(root, info):
    rep = []
    txt = _read_text(os.path.join(root, "CMakeLists.txt"))
    name = (re.search(r"project\s*\(\s*([A-Za-z0-9_\-\.]+)", txt, re.I) or [None, os.path.basename(root)])[1]
    builder = {"label": LABELS["cmake"], "deps": [],
               "build": [["cmake", "-S", ".", "-B", "build/_autobuild"],
                         ["cmake", "--build", "build/_autobuild", "--config", "Release"]],
               "gui": False, "out_dirs": ["build/_autobuild/Release", "build/_autobuild"], "out_depth": 0,
               "exe_names": [name.lower()], "expect_exe": True,
               "icon_note": "C/C++ ฝังไอคอนต้องเพิ่มไฟล์ .rc ใน CMakeLists เอง — ยังไม่ฝังให้อัตโนมัติ"}
    return _plan_base(root, "cmake", name, None, False, _tools("cmake"), builder, ["CMakeLists.txt"], rep)


def _plan_node_cli(root, info):
    rep = []
    pj = _read_json(os.path.join(root, "package.json"))
    scripts = pj.get("scripts") or {}
    name = _safe_name((pj.get("name") or os.path.basename(root)).split("/")[-1])
    b = pj.get("bin")
    entry = (b if isinstance(b, str) else (list(b.values())[0] if isinstance(b, dict) and b else None)) \
        or pj.get("main") or "index.js"
    pm = _pm(root)
    out = "dist/" + name + (".exe" if os.name == "nt" else "")
    build = ([[pm, "run", "build"]] if "build" in scripts else []) + [[
        "npx", "--yes", "@yao-pkg/pkg", entry, "--targets", f"node20-{_plat()}-x64", "--output", out]]
    builder = {"label": LABELS["node-cli"], "deps": [[pm, "install"]], "build": build, "gui": False,
               "out_dirs": ["dist"], "out_depth": 0, "exe_names": [name.lower()], "expect_exe": True,
               "icon_note": "pkg ไม่ฝังไอคอนให้อัตโนมัติ"}
    return _plan_base(root, "node-cli", name, pj.get("version"), False, _tools("node"), builder,
                      ["package.json"], rep)


def _plan_node_web(root, info):
    rep = []
    pj = _read_json(os.path.join(root, "package.json"))
    name = _safe_name((pj.get("name") or os.path.basename(root)).split("/")[-1])
    pm = _pm(root)
    builder = {"label": LABELS["node-web"], "deps": [[pm, "install"]], "build": [[pm, "run", "build"]],
               "gui": False, "out_dirs": ["dist", "build", "out", ".next"], "out_depth": 0, "exe_names": [],
               "expect_exe": False, "launch_test": False, "artifact_dirs": ["dist", "build", "out", ".next"]}
    rep.append((SKIP, "โปรเจกต์เว็บ — ผลลัพธ์เป็นโฟลเดอร์ ไม่ใช่ EXE (ข้ามขั้นทดสอบเปิดโปรแกรม)"))
    return _plan_base(root, "node-web", name, pj.get("version"), False, _tools("node"), builder,
                      ["package.json"], rep)


_PLANNERS = {"electron": _plan_electron, "tauri": _plan_tauri, "flutter": _plan_flutter,
             "dotnet": _plan_dotnet, "rust": _plan_rust, "go": _plan_go, "java": _plan_java,
             "cmake": _plan_cmake, "node-cli": _plan_node_cli, "node-web": _plan_node_web}


def auto_dispatch(root, forced=None):
    """ตรวจชนิดโปรเจกต์ → เรียกตัวสแกน/วางแผนของชนิดนั้น → (config, รายงาน)"""
    found = detect_projects(root)
    types = [t for t, _ in found]
    if forced:
        if forced not in LABELS:
            return {}, [(FAIL, f"ไม่รู้จักชนิดโปรเจกต์ '{forced}' — ใช้ได้: " + ", ".join(LABELS))]
        chosen, info = forced, dict(found).get(forced, {})
    elif not found:
        return {}, [(FAIL, "ไม่พบโปรเจกต์ที่รองรับ — รองรับ: " + ", ".join(LABELS.values())),
                    (SKIP, "ถ้าเป็นโปรเจกต์ชนิดอื่น ระบุเองได้ด้วย --type หรือคีย์ project_type")]
    else:
        chosen, info = found[0]
        strong = [t for t in types if t in STRONG]
        if len(strong) > 1 and not ASSUME_YES:
            opts = {str(i + 1): LABELS[t] for i, t in enumerate(strong[:6])}
            print()
            say("พบโปรเจกต์หลายชนิดในโฟลเดอร์เดียวกัน — เลือกชนิดที่จะ build", Y)
            ch = ask_choice("ชนิดคือ", opts)
            chosen = strong[int(ch) - 1] if ch in opts else chosen
            info = dict(found).get(chosen, {})
    head = [(OK, f"ชนิดโปรเจกต์: {LABELS[chosen]}")]
    if forced and chosen not in types:
        head.append((WARN, "บังคับชนิดนี้ แต่ไม่พบไฟล์หลักของชนิดนี้ในโฟลเดอร์ — อาจ build ไม่ผ่าน"))
    if len(types) > 1:
        others = [LABELS[t] for t in types if t != chosen]
        head.append((SKIP, "พบแบบอื่นด้วย (ไม่ได้เลือก): " + ", ".join(others) + "  — เปลี่ยนด้วย --type"))
    if chosen == "python":
        cfg, rep = auto_config(root)
    else:
        cfg, rep = _PLANNERS[chosen](root, info)
    if cfg:
        cfg["project_type"] = chosen
    return cfg, head + rep


# ── ตัวรันคำสั่ง build ทั่วไป ──────────────────────────────────
def build_env():
    env = os.environ.copy()
    extra = [d for d in EXTRA_PATH if d]
    if extra:
        env["PATH"] = os.pathsep.join(extra) + os.pathsep + env.get("PATH", "")
    return env


def _expand(cmd):
    """แทนที่ {ICON_ICO} ด้วย path ไอคอน · ถ้าไม่มีไอคอนจะตัดอาร์กิวเมนต์นั้นออก (ข้ามไอคอน)"""
    out, ico, done = [], None, False
    for a in cmd:
        if "{ICON_ICO}" in a:
            if not done:
                ico, done = resolve_icon(".ico" if os.name == "nt" else None), True
            if not ico:
                if a == "{ICON_ICO}" and out:
                    out.pop()
                continue
            a = a.replace("{ICON_ICO}", here(ico))
        out.append(a)
    return out


def _resolve_cmd(cmd, env, cwd):
    cand = os.path.join(cwd, cmd[0])
    if os.path.isfile(cand):
        return [cand] + cmd[1:]
    w = shutil.which(cmd[0], path=env.get("PATH"))
    return ([w] + cmd[1:]) if w else cmd


def _log_cmd(cmd, text):
    global _LOG_STARTED
    mode = "a" if _LOG_STARTED else "w"
    _LOG_STARTED = True
    try:
        with open(BUILD_LOG, mode, encoding="utf-8", errors="replace") as f:
            f.write("$ " + " ".join(cmd) + "\n" + text + "\n")
    except OSError:
        pass


def _run_logged(cmd, label, env, cwd):
    """รันคำสั่งพร้อมตัวนับเวลา · เก็บ log ต่อท้าย build_log.txt → (returncode, ข้อความ)"""
    full = _resolve_cmd(_expand(cmd), env, cwd)
    os.makedirs(here("logs"), exist_ok=True)
    rc, text = run_with_spinner(full, label, log_path=here("logs", "_cmd.log"), env=env, cwd=cwd)
    _log_cmd(full, text)
    return rc, text


def _explain_generic_failure(text, b):
    low = text.lower()
    print()
    if "is not recognized" in low or "command not found" in low or "winerror 2" in low \
            or "errno 2" in low and "no such file" in low:
        say("สาเหตุ: หาคำสั่งไม่เจอ — เครื่องมือ build ยังไม่ได้ติดตั้ง หรือยังไม่อยู่ใน PATH", R)
        say("ทางออก: ปิดแล้วเปิดเทอร์มินัลใหม่ (ให้ PATH ใหม่มีผล) แล้วรันสคริปต์อีกครั้ง", Y)
    elif "link.exe" in low and "not found" in low or "msvc" in low and "not found" in low:
        say("สาเหตุ: ขาด Visual Studio Build Tools (ตัวลิงก์ C++ ของ Windows)", R)
        say("ทางออก: ติดตั้ง Visual Studio Build Tools แล้วเลือก workload “Desktop development with C++”", Y)
    elif "eresolve" in low:
        say("สาเหตุ: เวอร์ชัน dependency ของ npm ขัดกัน (ERESOLVE)", R)
        say("ทางออก: ลอง  npm install --legacy-peer-deps  (ขั้น dependencies จะลองให้เองอยู่แล้ว)", Y)
    elif "eperm" in low or "access is denied" in low or "being used by another process" in low:
        say("สาเหตุที่เป็นไปได้: ไฟล์/โฟลเดอร์ถูกล็อก (โปรแกรมเปิดอยู่, แอนตี้ไวรัสสแกน, OneDrive ซิงก์)", R)
        say("ทางออก: ปิดโปรแกรมที่เปิดค้างไว้ หรือย้ายโปรเจกต์ไป path สั้นๆ เช่น C:\\build", Y)
    elif "virus" in low and "operation did not complete" in low:
        defender_report("Windows บล็อกไฟล์ที่เพิ่งสร้าง (มีไวรัสตามที่ Windows ตรวจ)")
    else:
        say("ดูรายละเอียดเต็มในไฟล์ build_log.txt", Y)
    say("บรรทัดท้ายของ log:", D)
    for r in tail(text, 8):
        print(f"      {D}{r[:110]}{X}")


# ── ขั้นตอนของ builder ทั่วไป ───────────────────────────────────
def step_check_generic():
    b = CFG["builder"]
    say(f"ชนิดโปรเจกต์: {b.get('label', CFG.get('project_type'))}")
    missing = [f for f in CFG["required_files"] if f and not os.path.isfile(here(f))]
    if missing:
        say("ไม่พบไฟล์: " + ", ".join(missing), R)
        return FAIL
    say("พบไฟล์โปรเจกต์: " + ", ".join(CFG["required_files"]), G)
    return OK


def step_deps_generic():
    b = CFG["builder"]
    cmds = CFG.get("install_commands") or b.get("deps", [])
    if not cmds:
        say("โปรเจกต์นี้ไม่มี dependencies ที่ต้องติดตั้งแยก — ข้าม", D)
        return SKIP
    env, cwd = build_env(), here(b.get("cwd", "."))
    for i, cmd in enumerate(cmds, 1):
        legacy = False
        while True:
            c = list(cmd) + (["--legacy-peer-deps"] if legacy else [])
            rc, text = _run_logged(c, f"[{i}/{len(cmds)}] {' '.join(cmd[:3])}", env, cwd)
            if rc == 0:
                say(f"✓ {' '.join(cmd[:3])}  ติดตั้งสำเร็จ", G)
                break
            if not legacy and "ERESOLVE" in text and "install" in cmd:
                legacy = True
                say("แก้อัตโนมัติ: dependency ขัดกัน (ERESOLVE) → ลองใหม่ด้วย --legacy-peer-deps", G)
                continue
            say(f"✗ {' '.join(cmd[:3])}  ไม่สำเร็จ", R)
            _explain_generic_failure(text, b)
            if ask_choice("ต้องการทำอย่างไรต่อ", {"r": "ลองใหม่", "q": "ออก"}) != "r":
                return FAIL
    return OK


def find_built_exe(b):
    """หา EXE ที่เพิ่งสร้าง + ไฟล์ติดตั้ง (setup/msi) → (exe | None, [extras])"""
    depth_max = b.get("out_depth", 0)
    names = [n.lower() for n in b.get("exe_names", [])]
    cands, extras = [], []
    for pat in b.get("out_dirs", []):
        for base in glob.glob(here(pat)):
            if not os.path.isdir(base):
                continue
            for dp, dns, fns in os.walk(base):
                rel = os.path.relpath(dp, base)
                depth = 0 if rel == "." else rel.count(os.sep) + 1
                if depth >= depth_max:
                    dns[:] = []
                for fn in fns:
                    p = os.path.join(dp, fn)
                    low = fn.lower()
                    if not _is_exe(p):
                        continue
                    (extras if ("setup" in low or "installer" in low) else cands).append(p)
    for pat in b.get("installer_dirs", []):
        for base in glob.glob(here(pat)):
            for dp, dns, fns in os.walk(base):
                rel = os.path.relpath(dp, base)
                if rel != "." and rel.count(os.sep) >= 3:
                    dns[:] = []
                for fn in fns:
                    low = fn.lower()
                    if low.endswith(".msi") or (low.endswith(".exe") and ("setup" in low or "installer" in low)):
                        extras.append(os.path.join(dp, fn))
    exe = None
    if cands:
        pool = [c for c in cands if os.path.splitext(os.path.basename(c))[0].lower() in names] or cands
        exe = max(pool, key=os.path.getmtime)
    return exe, sorted(set(extras))


_EXE_BAD = ("uninstall", "unins", "crashpad", "elevate", "vcredist", "vc_redist", "createdump")


def _is_exe(path):
    low = os.path.basename(path).lower()
    if any(x in low for x in _EXE_BAD):
        return False
    if os.name == "nt":
        return low.endswith(".exe")
    return os.path.isfile(path) and os.access(path, os.X_OK) and not low.endswith(
        (".so", ".a", ".o", ".py", ".sh", ".dll", ".dylib", ".json", ".txt", ".pdb", ".d", ".jar"))


def java_package(b, env):
    """Java: หา JAR แล้วห่อเป็น EXE ด้วย jpackage ถ้าทำได้ · คืน path ของผลลัพธ์หลัก"""
    name = CFG["app_name"]
    jars = []
    for d in b.get("jar_dirs", []):
        for p in glob.glob(here(d, "*.jar")):
            low = os.path.basename(p).lower()
            if not low.startswith("original-") and not low.endswith(("-sources.jar", "-javadoc.jar", "-plain.jar")):
                jars.append(p)
    if not jars:
        say("ไม่พบไฟล์ .jar หลัง build", Y)
        return None
    jar = max(jars, key=os.path.getsize)
    say(f"ได้ไฟล์ JAR: {os.path.relpath(jar, HERE)}  ({os.path.getsize(jar) / 1024 / 1024:.1f} MB)", G)
    try:
        with zipfile.ZipFile(jar) as z:
            mf = z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        mf = ""
    if "Main-Class" not in mf:
        say("JAR ไม่ระบุ Main-Class — ไม่ห่อเป็น EXE (เป็นไลบรารี หรือยังไม่ได้ตั้งค่า manifest)", D)
        return jar
    jp = shutil.which("jpackage", path=env.get("PATH"))
    if not jp:
        say("ไม่พบ jpackage (ต้องใช้ JDK 14+) — ได้เป็น JAR เท่านั้น รันด้วย  java -jar", D)
        return jar
    force_rmtree(here("dist", name))
    cmd = [jp, "--type", "app-image", "--name", name, "--input", os.path.dirname(jar),
           "--main-jar", os.path.basename(jar), "--dest", here("dist"), "--icon", "{ICON_ICO}"]
    rc, text = _run_logged(cmd, "jpackage ห่อเป็น EXE", env, HERE)
    if rc != 0:
        say("jpackage ไม่สำเร็จ — ใช้ไฟล์ JAR แทน", Y)
        for r in tail(text, 4):
            print(f"      {D}{r[:100]}{X}")
    return jar


def step_build_generic(dry_run=False):
    global BUILT_EXE, _LOG_STARTED
    b = CFG["builder"]
    cmds = CFG.get("build_commands") or b.get("build", [])
    env, cwd = build_env(), here(b.get("cwd", "."))
    if dry_run:
        say("คำสั่งที่จะรัน (dry-run):", D)
        for c in (CFG.get("install_commands") or b.get("deps", [])) + cmds:
            print("   " + " ".join(f'"{a}"' if " " in a else a for a in _expand(c)))
        return SKIP
    if not cmds:
        say("ไม่มีคำสั่ง build — ใส่ build_commands ใน autobuild.json", R)
        return FAIL
    t0 = time.time() - 2
    for i, cmd in enumerate(cmds, 1):
        while True:
            rc, text = _run_logged(cmd, f"[{i}/{len(cmds)}] {' '.join(cmd[:3])}", env, cwd)
            if rc == 0:
                break
            say("build ไม่สำเร็จ", R)
            _explain_generic_failure(text, b)
            if ask_choice("ต้องการทำอย่างไรต่อ", {"r": "ลองใหม่", "q": "ออก"}) != "r":
                return FAIL
    os.makedirs(here("logs"), exist_ok=True)
    try:
        shutil.copyfile(BUILD_LOG, here("logs", "build_last.log"))
    except OSError:
        pass
    main_art = None
    if b.get("post") == "java_package":
        main_art = java_package(b, env)
    exe, extras = find_built_exe(b)
    if exe:
        BUILT_EXE = exe
        say(f"สร้างสำเร็จ: {os.path.relpath(exe, HERE)}  ({os.path.getsize(exe) / 1024 / 1024:.1f} MB)", G)
        if os.path.getmtime(exe) < t0:
            say("คำเตือน: EXE นี้เป็นไฟล์เก่า (ไม่ได้ถูกสร้างใหม่รอบนี้) — ตรวจ build_log.txt", Y)
        try:
            say("SHA256: " + file_sha256(exe), D)
        except OSError:
            say("อ่านไฟล์ EXE ไม่ได้ทันทีหลัง build — อาจถูกแอนตี้ไวรัสล็อกอยู่", Y)
        for x in extras[:5]:
            say("ไฟล์ติดตั้งที่ได้: " + os.path.relpath(x, HERE), G)
        return OK
    arts = []
    for pat in b.get("artifact_globs", []):
        arts += glob.glob(here(pat))
    for d in b.get("artifact_dirs", []):
        if os.path.isdir(here(d)):
            arts.append(here(d))
    if main_art:
        arts.insert(0, main_art)
    if arts:
        say("build สำเร็จ ผลลัพธ์: " + ", ".join(os.path.relpath(a, HERE) for a in arts[:4]), G)
        return OK
    if b.get("expect_exe", True):
        defender_report("build จบแต่ไม่พบไฟล์ EXE — อาจถูกแอนตี้ไวรัสลบ/กักกัน หรือ path ผลลัพธ์ต่างจากที่คาด")
        say("ที่ค้นหา: " + ", ".join(b.get("out_dirs", [])) + "  — ถ้าผลลัพธ์อยู่ที่อื่น ใส่ out_dirs ใน autobuild.json (คีย์ builder)", Y)
        return WARN
    return WARN


def step_test_generic():
    secs = CFG["test_launch_seconds"]
    b = CFG["builder"]
    if not secs or b.get("launch_test") is False:
        say("ข้ามการทดสอบเปิดโปรแกรม", D)
        return SKIP
    exe = BUILT_EXE
    if not exe or not os.path.isfile(exe):
        say("ไม่มี EXE ให้ทดสอบ — ข้าม", D)
        return SKIP
    os.makedirs(here("logs"), exist_ok=True)
    lp = here("logs", "test_run_last.log")
    say(f"เปิดโปรแกรมทดสอบประมาณ {secs} วินาที (ถ้าเป็นหน้าต่างจะโผล่ขึ้นมาแล้วปิดเอง)")
    with open(lp, "w", encoding="utf-8", errors="replace") as f:
        try:
            p = subprocess.Popen([exe], stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT,
                                 cwd=os.path.dirname(exe), env=build_env())
        except OSError as ex:
            say("เปิดโปรแกรมไม่ได้: " + str(ex), R)
            if getattr(ex, "winerror", None) == 225 or "virus" in str(ex).lower():
                defender_report("Windows บล็อกไม่ให้เปิดไฟล์นี้ (WinError 225)")
            return WARN
        for _ in range(int(secs / 0.2)):
            time.sleep(0.2)
            if p.poll() is not None:
                break
        running = p.poll() is None
        if running:
            p.terminate()
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
    text = _read_from(lp)
    if running:
        say("โปรแกรมเปิดทำงานได้ปกติ", G)
        return OK
    if p.returncode == 0:
        say("โปรแกรมทำงานจบเองและคืนค่าปกติ (code 0)", G)
        return OK
    if "usage" in text.lower() and not analyze_log(text):
        say(f"โปรแกรมเริ่มทำงานได้และพิมพ์วิธีใช้ (code {p.returncode}) — เป็นโปรแกรม CLI ที่ต้องมีอาร์กิวเมนต์", G)
        return OK
    say(f"โปรแกรมปิดตัวด้วย code {p.returncode}:", Y)
    for r in tail(text, 6):
        print(f"      {D}{r[:110]}{X}")
    findings = analyze_log(text)
    if findings:
        show_findings(findings)
    return WARN


# ═══ ขั้นตอนที่ 1: สแกน ═════════════════════════════════════════
def step_scan(cfg_path, args):
    global CFG, CFG_PATH
    CFG_PATH = cfg_path
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    status = OK
    user = {}
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                user = json.load(f)
        except (OSError, ValueError) as ex:
            say(f"อ่าน {os.path.basename(cfg_path)} ไม่ได้: {ex}", R)
            return FAIL

    if args.no_scan:
        say("ปิดการสแกน (--no-scan) — ใช้เฉพาะ config", D)
    else:
        forced = getattr(args, "type", None) or user.get("project_type")
        auto, rep = auto_dispatch(HERE, forced)
        merge_cfg(cfg, auto)
        for st, msg in rep:
            print(f"  {ICON[st]} {msg}")
            if st == FAIL:
                status = FAIL
            elif st == WARN and status == OK:
                status = WARN

    if user:
        known = set(DEFAULT_CONFIG)
        keys = [k for k in user if not k.startswith("_") and k in known]
        unknown = [k for k in user if not k.startswith("_") and k not in known]
        merge_cfg(cfg, {k: user[k] for k in keys})
        if keys:
            say(f"ใช้ค่าจาก {os.path.basename(cfg_path)} ทับผลสแกน: " + ", ".join(keys), Y)
        if unknown:
            say("ข้ามคีย์ที่ไม่รู้จัก: " + ", ".join(unknown), D)
    if not cfg.get("project_type"):
        cfg["project_type"] = "python"
    CFG = cfg

    if args.init:
        out = cfg_path if not os.path.exists(cfg_path) else cfg_path.replace(".json", ".generated.json")
        data = dict(cfg)
        data["_comment"] = "สร้างจากการสแกนอัตโนมัติ · แก้ได้ · ลบคีย์ที่ไม่ต้องการแก้ออกเพื่อให้สแกนใหม่ทุกครั้ง"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        say(f"บันทึกผลสแกนแล้ว: {os.path.basename(out)}", G)
    return status


# ═══ ขั้นตอนที่ 1 ═══════════════════════════════════════════
def step_check():
    v = sys.version_info
    say(f"Python {v.major}.{v.minor}.{v.micro}  ({sys.executable})")
    need = tuple(CFG["min_python"])
    if v < need:
        say(f"ต้องใช้ Python {'.'.join(map(str, need))} ขึ้นไป — กรุณาอัปเดต Python", R)
        return FAIL
    files = set(CFG["required_files"]) | {CFG["entry_script"]}
    missing = [f for f in sorted(files) if f and not os.path.isfile(here(f))]
    if missing:
        say("ไม่พบไฟล์: " + ", ".join(missing) + "  (ต้องวางไว้โฟลเดอร์เดียวกับสคริปต์นี้)", R)
        return FAIL
    say("พบไฟล์โปรเจกต์ครบ: " + ", ".join(sorted(files)), G)
    return OK


# ═══ ขั้นตอนที่ 2 ═══════════════════════════════════════════
def _pip_install(args, timeout=600):
    return run_quiet([sys.executable, "-m", "pip", "install", *args,
                      "--disable-pip-version-check"], timeout=timeout)


def step_pip():
    result = OK

    req = CFG.get("requirements_file")
    if req and os.path.isfile(here(req)):
        print(f"  {B}…{X} ติดตั้งจาก {req}", end="", flush=True)
        rc, out = _pip_install(["-r", here(req)], timeout=1800)
        print("\r" + " " * 70 + "\r", end="")
        if rc == 0:
            print(f"  {ICON[OK]} {req}  {G}ติดตั้งสำเร็จ{X}")
        else:
            print(f"  {ICON[WARN]} {req}  {Y}ติดตั้งไม่ครบ — จะลองทีละตัวต่อ{X}")
            for r in tail(out, 4):
                print(f"      {D}{r[:100]}{X}")
            result = WARN

    pkgs = CFG["python_packages"]
    if not pkgs and not req:
        say("config ไม่ได้ระบุไลบรารี — ข้าม", D)
        return SKIP

    for p in pkgs:
        mod, pipname = p["module"], p["pip"]
        required, desc = p.get("required", False), p.get("desc", "")
        label = f"{pipname:<14} {D}{desc}{X}"
        if has_module(mod):
            print(f"  {ICON[OK]} {label}  {D}มีอยู่แล้ว{X}")
            continue
        while True:
            print(f"  {B}…{X} {label}  กำลังติดตั้ง", end="", flush=True)
            rc, out = _pip_install([pipname])
            print("\r" + " " * 70 + "\r", end="")
            if rc == 0:
                print(f"  {ICON[OK]} {label}  {G}ติดตั้งสำเร็จ{X}")
                break
            mark = ICON[FAIL] if required else ICON[WARN]
            print(f"  {mark} {label}  {R if required else Y}ติดตั้งไม่สำเร็จ{X}")
            for r in tail(out, 4):
                print(f"      {D}{r[:100]}{X}")
            if required:
                c = ask_choice("จำเป็นต้องมีตัวนี้", {"r": "ลองใหม่", "q": "ออก"})
                if c == "r":
                    continue
                return FAIL
            result = WARN
            say(f"ข้าม {pipname} — โปรแกรมยังใช้ได้ แต่ฟีเจอร์ “{desc}” จะไม่ทำงาน", Y)
            break
    return result


# ═══ ขั้นตอนที่ 3 ═══════════════════════════════════════════
def find_tool(tool):
    """ค้นหาเครื่องมือตาม config: commands (PATH) → paths (ไฟล์ตรง ๆ) → globs (รูปแบบ)"""
    for c in tool.get("commands", []):
        w = shutil.which(c)
        if w:
            return w
    for p in tool.get("paths", []):
        p = os.path.expandvars(p)
        if os.path.isfile(p):
            return p
    for g in tool.get("globs", []):
        hits = sorted(glob.glob(os.path.expandvars(g)))
        if hits:
            return hits[-1]
    return None


def _note_tool_path(path):
    d = os.path.dirname(path) if path else ""
    if d and d not in EXTRA_PATH:
        EXTRA_PATH.append(d)


def step_tools():
    tools = CFG["external_tools"]
    if not tools:
        say("config ไม่ได้ระบุเครื่องมือเสริม — ข้าม", D)
        return SKIP
    have_winget = shutil.which("winget") is not None
    result = OK
    any_missing = False
    missing_required = []
    for t in tools:
        name, desc, wid = t["name"], t.get("desc", ""), t.get("winget_id")
        req = t.get("required", False)
        label = f"{name:<12} {D}{desc}{X}"
        found = find_tool(t)
        if found:
            _note_tool_path(found)
            print(f"  {ICON[OK]} {label}  {D}มีอยู่แล้ว{X}")
            continue
        any_missing = True
        print(f"  {ICON[FAIL if req else WARN]} {label}  {Y}ยังไม่ได้ติดตั้ง{X}")
        if t.get("manual"):
            say("    " + t["manual"], Y)
        if not wid or not have_winget:
            say("    ไม่มี winget/ไม่ระบุ winget_id — ติดตั้งเองภายหลังได้" +
                ("" if req else " (ข้ามได้ ไม่กระทบการ build)"), D)
            result = WARN
            if req:
                missing_required.append(name)
            continue
        if not ask_yes(f"ติดตั้ง {name} ตอนนี้ไหม?", default=True):
            say(f"    ข้าม {name}", D)
            result = WARN
            if req:
                missing_required.append(name)
            continue
        print(f"  {B}…{X} กำลังติดตั้ง {name} (อาจมีหน้าต่างขอสิทธิ์ผู้ดูแล)", end="", flush=True)
        rc, out = run_quiet(["winget", "install", "--id", wid, "-e",
                             "--accept-package-agreements", "--accept-source-agreements"],
                            timeout=1800)
        print("\r" + " " * 78 + "\r", end="")
        found = find_tool(t)
        if rc == 0 or found:
            if found:
                _note_tool_path(found)
                print(f"  {ICON[OK]} {name}  {G}ติดตั้งสำเร็จ{X}")
            else:
                print(f"  {ICON[WARN]} {name}  {Y}ติดตั้งแล้วแต่ยังหาไม่เจอ — ปิดแล้วเปิดเทอร์มินัลใหม่ แล้วรันสคริปต์อีกครั้ง{X}")
                if req:
                    missing_required.append(name)
                result = WARN
            if t.get("after_install"):
                say("    " + t["after_install"], D)
        else:
            print(f"  {ICON[FAIL]} {name}  {R}ติดตั้งไม่สำเร็จ{X}")
            for r in tail(out, 3):
                print(f"      {D}{r[:100]}{X}")
            result = WARN
            if req:
                missing_required.append(name)
    if missing_required:
        say("ขาดเครื่องมือที่จำเป็นต่อการ build: " + ", ".join(missing_required), R)
        return FAIL
    if any_missing and not _is_generic():
        say("หมายเหตุ: เครื่องมือเสริมเหล่านี้ไม่ได้รวมอยู่ใน EXE — เครื่องผู้ใช้ต้องมีเองถ้าต้องการฟีเจอร์นั้น", D)
    return result


# ═══ ขั้นตอนที่ 4 ═══════════════════════════════════════════
# ═══ Windows Defender: ตรวจการกักกัน / exclusion / SHA256 ═══════
def _ps(command, timeout=60):
    return run_quiet(["powershell", "-NoProfile", "-NonInteractive", "-Command", command], timeout=timeout)


def is_admin():
    if os.name != "nt":
        return False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_under(path, folders):
    p = os.path.normcase(os.path.abspath(path))
    for f in folders:
        f = os.path.normcase(os.path.abspath(os.path.expandvars(f.strip())))
        if p == f or p.startswith(f.rstrip("\\/") + os.sep):
            return True
    return False


def defender_exclusions():
    """คืน (รายการโฟลเดอร์ที่ยกเว้น | None ถ้าอ่านไม่ได้, เหตุผล)"""
    rc, out = _ps("(Get-MpPreference).ExclusionPath -join [char]10")
    if rc != 0 or "not recognized" in out or "Get-MpPreference" in out and "Exception" in out:
        return None, "ไม่พบ Windows Defender (อาจใช้แอนตี้ไวรัสตัวอื่น)"
    rows = [r.strip() for r in out.splitlines() if r.strip()]
    if any(r.startswith("N/A") for r in rows):
        return None, "ต้องรันแบบ Administrator จึงจะอ่านรายการยกเว้นได้"
    return rows, ""


def defender_recent():
    """ประวัติที่ Defender ตรวจเจอ/กักกันล่าสุด → [{time, name, res}]"""
    cmd = ("$d = Get-MpThreatDetection | Sort-Object InitialDetectionTime -Descending | Select-Object -First 10; "
           "$r = foreach($x in $d){ $t = Get-MpThreat -ThreatID $x.ThreatID -ErrorAction SilentlyContinue; "
           "[pscustomobject]@{Time=[string]$x.InitialDetectionTime; Name=$t.ThreatName; Res=($x.Resources -join ';')} }; "
           "@($r) | ConvertTo-Json -Compress")
    rc, out = _ps(cmd, timeout=90)
    if rc != 0:
        return []
    try:
        data = json.loads(out.strip() or "[]")
    except ValueError:
        return []
    if isinstance(data, dict):
        data = [data]
    return [{"time": d.get("Time", ""), "name": d.get("Name") or "?", "res": d.get("Res", "")}
            for d in data if isinstance(d, dict)]


def defender_report(reason):
    """EXE หาย/เปิดไม่ได้ → ดูว่า Defender กักกันหรือไม่ แล้วบอกวิธีแก้"""
    if os.name != "nt" or not CFG.get("defender", {}).get("check", True):
        return False
    say(reason, Y)
    mine = []
    key = os.path.normcase(HERE)
    for d in defender_recent():
        res = os.path.normcase(d["res"])
        if key in res or CFG.get("app_name", "").lower() in res:
            mine.append(d)
    if not mine:
        say("ไม่พบประวัติ Defender ที่เกี่ยวกับไฟล์ของโปรเจกต์นี้ — อาจเป็นสาเหตุอื่น (ดู build_log.txt)", D)
        return False
    say("Windows Defender ตรวจเจอ/กักกันไฟล์ของโปรเจกต์นี้:", R)
    for d in mine[:4]:
        say(f"  • {d['name']}  ({d['time']})", R)
        say(f"    {d['res'][:150]}", D)
    say("วิธีแก้ (ส่วนใหญ่เป็น false positive ของ EXE จาก PyInstaller):", Y)
    say("  1) Windows Security > Virus & threat protection > Protection history > เลือกรายการ > Actions > Allow on device", Y)
    say("  2) รันสคริปต์นี้ใหม่ — ขั้นตอน Defender จะถามเพิ่ม exclusion เฉพาะโฟลเดอร์โปรเจกต์ให้", Y)
    if CFG.get("onefile"):
        say("  3) ลอง build แบบ onedir: ใส่ {\"onefile\": false} ใน autobuild.json (โดนจับน้อยกว่ามาก)", Y)
    say("  4) ส่งไฟล์ให้ Microsoft ตรวจ: https://www.microsoft.com/wdsi/filesubmission", Y)
    return True


def step_defender():
    cfg = CFG.get("defender", {})
    if os.name != "nt":
        say("ไม่ใช่ Windows — ข้าม", D)
        return SKIP
    if not cfg.get("check", True):
        say("config ปิดการตรวจ Defender — ข้าม", D)
        return SKIP
    folders, why = defender_exclusions()
    if folders is not None and _is_under(HERE, folders):
        say("โฟลเดอร์โปรเจกต์อยู่ในรายการยกเว้นของ Defender แล้ว", G)
        return OK
    if folders is None and "ไม่พบ" in why:
        say(why + " — ข้าม", D)
        return SKIP
    say("Defender มักกักกัน EXE ที่ PyInstaller สร้างทันทีที่ build เสร็จ (false positive)", Y)
    if why:
        say(why, D)
    if not cfg.get("offer_exclusion", True):
        return OK
    cmd_txt = f'Add-MpPreference -ExclusionPath "{HERE}"'
    if not is_admin():
        say("เพิ่ม exclusion เฉพาะโฟลเดอร์นี้ได้ โดยเปิด PowerShell แบบ Administrator แล้วรัน:", D)
        say("  " + cmd_txt, D)
        say("(หรือ Windows Security > Manage settings > Exclusions > Add folder) — จะข้ามไปก่อนก็ได้", D)
        return WARN
    if ASSUME_YES:
        say("โหมด --yes ไม่เพิ่ม exclusion ให้เอง (ต้องยืนยันด้วยตัวเอง)", D)
        return WARN
    say("การยกเว้นจะมีผลกับโฟลเดอร์นี้เท่านั้น: " + HERE, D)
    if not ask_yes("เพิ่มโฟลเดอร์นี้เข้ารายการยกเว้นของ Windows Defender ไหม?", default=False):
        say("ข้าม", D)
        return WARN
    rc, out = _ps(f"Add-MpPreference -ExclusionPath '{HERE}'")
    folders, _ = defender_exclusions()
    if rc == 0 and folders is not None and _is_under(HERE, folders):
        say("เพิ่มรายการยกเว้นแล้ว", G)
        return OK
    say("เพิ่มไม่สำเร็จ (อาจมี Tamper Protection หรือนโยบายองค์กรบล็อก)", R)
    for r in tail(out, 3):
        print(f"      {D}{r[:100]}{X}")
    return WARN


def _explain_build_failure(text):
    low = text.lower()
    name = CFG["app_name"]
    hint = (CFG.get("help_hints") or {}).get("run_without_build")
    print()
    if "device guard" in low or "blocked" in low or "application control" in low or "4551" in low:
        say("สาเหตุ: นโยบาย Device Guard / Application Control ของเครื่องบล็อกไฟล์ที่ไม่ได้ลงนาม", R)
        say("ทางออก: ให้ผู้ดูแลระบบ (IT) อนุญาต PyInstaller หรือโฟลเดอร์นี้", Y)
        if hint:
            say(f"หรือใช้ {hint} เปิดโปรแกรมผ่าน Python โดยไม่ต้อง build", Y)
    elif "permission" in low or "access is denied" in low or "winerror 5" in low:
        say(f"สาเหตุที่เป็นไปได้: ไฟล์/โฟลเดอร์ถูกล็อกหรือไม่มีสิทธิ์เขียน (เช่น {name}.exe เปิดอยู่,", R)
        say("แอนตี้ไวรัสสแกนอยู่, หรือโฟลเดอร์ถูกซิงก์โดย OneDrive)", R)
        say(f"ทางออก: ปิดโปรแกรม {name} · ปิด VS Code หน้าต่างที่เปิดโฟลเดอร์ dist/build ·", Y)
        say("หรือย้ายโปรเจกต์ไปไว้ที่ path สั้น ๆ เช่น C:\\build แล้วรันใหม่", Y)
    elif "no module named" in low:
        say("สาเหตุ: ไลบรารีบางตัวไม่ได้ติดตั้ง — กลับไปทำขั้นตอนที่ 2 ใหม่", R)
    else:
        say("ดูรายละเอียดเต็มในไฟล์ build_log.txt", Y)
    say("บรรทัดท้ายของ log:", D)
    for r in tail(text, 8):
        print(f"      {D}{r[:110]}{X}")


def build_command(workdir):
    """ประกอบคำสั่ง PyInstaller จาก config"""
    sep = os.pathsep           # ';' บน Windows, ':' บน Linux/macOS
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--workpath", workdir,
           "--onefile" if CFG["onefile"] else "--onedir",
           f"--name={CFG['app_name']}"]
    if CFG["windowed"]:
        cmd.append("--windowed")
    ic = resolve_icon(".ico" if os.name == "nt" else None)
    if ic:
        cmd.append(f"--icon={ic}")

    for item in CFG["add_data"] + CFG["extra_add_data"]:
        cmd += ["--add-data", item.replace(";", sep)]
    for item in CFG["add_binary"]:
        cmd += ["--add-binary", item.replace(";", sep)]
    for m in CFG["hidden_imports"] + CFG["extra_hidden_imports"]:
        cmd += ["--hidden-import", m]
    for m in CFG["collect_all"] + CFG["extra_collect_all"]:
        cmd += ["--collect-all", m]
    if CFG.get("runtime_log"):
        hook = os.path.join(workdir, "autobuild_runtime_hook.py")
        with open(hook, "w", encoding="utf-8") as f:
            f.write(RUNTIME_HOOK.replace("__APP__", CFG["app_name"]))
        cmd += ["--runtime-hook", hook]

    # กลุ่มไฟล์ที่แนบเฉพาะตัวแรกที่เจอ (เช่น 7za.exe หรือ 7zr.exe)
    for group in CFG["add_binary_first_found"]:
        found = next((n for n in group if os.path.isfile(here(n))), None)
        if found:
            cmd += ["--add-binary", f"{found}{sep}."]
            say(f"พบ {found} — จะแนบเข้า EXE", G)
        else:
            say(f"ไม่พบ {' / '.join(group)} — ไม่แนบเข้า EXE", D)

    cmd += CFG["extra_pyinstaller_args"]
    cmd.append(CFG["entry_script"])
    return cmd


def step_build(dry_run=False):
    name = CFG["app_name"]
    exe = exe_path()

    old_build = here("build")
    if os.path.isdir(old_build) and not dry_run:
        if force_rmtree(old_build):
            say("ล้างโฟลเดอร์ build เดิมแล้ว", D)
        else:
            say("ล้างโฟลเดอร์ build เดิมไม่ได้ (ถูกล็อก/ไม่มีสิทธิ์) — ใช้โฟลเดอร์ชั่วคราวแทน", Y)

    if dry_run:
        workdir = tempfile.mkdtemp(prefix=f"{name.lower()}_build_")
        cmd = build_command(workdir)
        say("คำสั่งที่จะรัน (dry-run):", D)
        print("   " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
        force_rmtree(workdir)
        return SKIP

    if os.path.isfile(exe):
        try:
            os.remove(exe)                  # ตรวจว่าไฟล์เก่าไม่ได้ถูกล็อกอยู่
        except OSError:
            say(f"ลบ {os.path.relpath(exe, HERE)} เดิมไม่ได้ — ปิดโปรแกรม {name} ก่อนแล้วลองใหม่", R)
            return FAIL

    attempts = 0
    while True:
        workdir = tempfile.mkdtemp(prefix=f"{name.lower()}_build_")
        cmd = build_command(workdir)
        rc, text = run_with_spinner(cmd, "กำลัง build (ใช้เวลาราว 1–3 นาที)")
        os.makedirs(here("logs"), exist_ok=True)
        try:
            shutil.copyfile(BUILD_LOG, here("logs", "build_last.log"))
        except OSError:
            pass
        built = os.path.isfile(exe) if CFG["onefile"] else os.path.isdir(here("dist", name))
        if rc == 0 and not built:
            defender_report("build จบแต่ไม่พบไฟล์ EXE — อาจถูกแอนตี้ไวรัสลบ/กักกัน")
        if rc == 0 and built:
            missing = collect_warn(workdir, name)
            force_rmtree(workdir)
            if CFG["onefile"]:
                mb = os.path.getsize(exe) / 1024 / 1024
                say(f"สร้างสำเร็จ: {os.path.relpath(exe, HERE)}  ({mb:.1f} MB)", G)
            else:
                say(f"สร้างสำเร็จ: dist{os.sep}{name}{os.sep}", G)
            if CFG["onefile"]:
                try:
                    say("SHA256: " + file_sha256(exe), D)
                    say("(ใช้ยืนยันไฟล์เวลาส่งให้ Microsoft หรือแจ้ง IT ขออนุญาต)", D)
                except OSError:
                    say("อ่านไฟล์ EXE ไม่ได้ทันทีหลัง build — อาจถูกแอนตี้ไวรัสล็อกอยู่", Y)
            if missing:
                say("คำเตือน: PyInstaller หาโมดูลเหล่านี้ไม่เจอ (อาจทำให้ EXE พัง): " + ", ".join(missing[:8]), Y)
                say("  ถ้า EXE ทำงานผิดปกติ สคริปต์จะอ่าน log ตอนทดสอบแล้วแก้ให้เอง", D)
            return OK
        force_rmtree(workdir)
        say("build ไม่สำเร็จ", R)
        _explain_build_failure(text)
        fixes = apply_fixes(analyze_log(text)) if attempts < CFG["max_auto_retries"] else []
        if fixes:
            attempts += 1
            for fx in fixes:
                say("แก้อัตโนมัติ: " + fx, G)
            say(f"ลอง build ใหม่ (รอบที่ {attempts})", D)
            continue
        c = ask_choice("ต้องการทำอย่างไรต่อ", {"r": "ลองใหม่", "q": "ออก"})
        if c != "r":
            return FAIL


# ═══ ขั้นตอนที่ 5 ═══════════════════════════════════════════
def _test_once():
    """เปิด EXE ชั่วคราวแล้วดึง log ที่โปรแกรมเขียนออกมา → (สถานะ, findings)"""
    secs = CFG["test_launch_seconds"]
    exe = exe_path() if CFG["onefile"] else os.path.join(
        here("dist", CFG["app_name"]), os.path.basename(exe_path()))
    if not os.path.isfile(exe):
        say("ไม่พบ EXE — ข้าม", D)
        return SKIP, []
    lp = runtime_log_path()
    offset = os.path.getsize(lp) if os.path.isfile(lp) else 0
    say(f"เปิดโปรแกรมทดสอบประมาณ {secs} วินาที (หน้าต่างจะโผล่ขึ้นมาแล้วปิดเอง)")
    try:
        p = subprocess.Popen([exe])
    except OSError as ex:
        say("เปิดโปรแกรมไม่ได้: " + str(ex), R)
        if getattr(ex, "winerror", None) == 225 or "virus" in str(ex).lower():
            defender_report("Windows บล็อกไม่ให้เปิดไฟล์นี้ (WinError 225)")
        say("ถ้าเป็นข้อความเรื่อง policy/blocked = Device Guard บล็อก EXE ที่ไม่ได้ลงนาม → ให้ IT อนุญาต", Y)
        return WARN, []
    for _ in range(int(secs / 0.2)):
        time.sleep(0.2)
        if p.poll() is not None:
            break
    running = p.poll() is None
    if running:
        p.terminate()
        try:
            p.wait(timeout=5)
        except Exception:
            p.kill()
    time.sleep(0.3)

    text = _read_from(lp, offset) if CFG.get("runtime_log") else ""
    findings = analyze_log(text) if text else []
    if text:
        os.makedirs(here("logs"), exist_ok=True)
        with open(here("logs", "test_run_last.log"), "w", encoding="utf-8") as f:
            f.write(text)
        say(f"อ่าน log ของโปรแกรมได้ {len(text.splitlines())} บรรทัด  ({lp})", D)
    elif CFG.get("runtime_log"):
        say("ไม่พบ log ของโปรแกรม (ยังไม่ได้เขียน) — โปรแกรมอาจพังก่อนเริ่มทำงาน", Y)

    if running and not findings:
        say("โปรแกรมเปิดทำงานได้ปกติ", G)
        return OK, []
    if running:
        say("โปรแกรมเปิดอยู่ แต่ log มีข้อผิดพลาด:", Y)
    else:
        say(f"โปรแกรมปิดตัวเองทันที (code {p.returncode}) — สาเหตุจาก log:", Y)
    if not findings and text:
        for r in tail(text, 6):
            print(f"      {D}{r[:110]}{X}")
    return WARN, findings


def step_test():
    if not CFG["test_launch_seconds"]:
        say("config ปิดการทดสอบ — ข้าม", D)
        return SKIP
    tries = 0
    while True:
        st, findings = _test_once()
        if st == SKIP:
            return SKIP
        if findings:
            show_findings(findings)
        if st == OK:
            return OK
        fixes = apply_fixes(findings) if tries < CFG["max_auto_retries"] else []
        if fixes:
            for fx in fixes:
                say("แก้อัตโนมัติ: " + fx, G)
            if ask_yes("แก้ค่าให้แล้ว — build ใหม่แล้วทดสอบซ้ำเลยไหม?", default=True):
                tries += 1
                if step_build() == FAIL:
                    return FAIL
                continue
        say("log เต็ม: " + runtime_log_path(), D)
        say("ส่งไฟล์ autobuild_report.txt (สร้างให้ท้ายการรัน) มาให้ดูได้เลย", D)
        return WARN


# ═══ ขั้นตอนที่ 6 ═══════════════════════════════════════════
def _find_iscc():
    w = shutil.which("ISCC") or shutil.which("iscc")
    if w:
        return w
    for p in (r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
              r"C:\Program Files\Inno Setup 6\ISCC.exe",
              os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe")):
        if os.path.isfile(p):
            return p
    return None


def step_installer():
    inst = CFG["installer"]
    if not inst.get("enabled"):
        say("config ไม่ได้เปิดตัวสร้างตัวติดตั้ง — ข้าม", D)
        return SKIP
    if not os.path.isfile(exe_path()):
        say("ไม่มี EXE — ข้าม", D)
        return SKIP
    iss = here(inst["iss_file"])
    if not os.path.isfile(iss):
        say(f"ไม่พบ {inst['iss_file']} — ข้ามการสร้างตัวติดตั้ง", D)
        return SKIP
    if not ask_yes("สร้างตัวติดตั้ง Setup.exe (ใช้ Inno Setup) ไหม?", default=True):
        say("ข้าม", D)
        return SKIP
    iscc = _find_iscc()
    if not iscc:
        say("ยังไม่ได้ติดตั้ง Inno Setup", Y)
        if shutil.which("winget") and ask_yes("ติดตั้ง Inno Setup ผ่าน winget ตอนนี้ไหม?", default=True):
            print(f"  {B}…{X} กำลังติดตั้ง Inno Setup", end="", flush=True)
            run_quiet(["winget", "install", "--id", "JRSoftware.InnoSetup", "-e",
                       "--accept-package-agreements", "--accept-source-agreements"],
                      timeout=1800)
            print("\r" + " " * 60 + "\r", end="")
            iscc = _find_iscc()
        if not iscc:
            say("ไม่พบ Inno Setup — ติดตั้งแล้วรันสคริปต์นี้ใหม่ หรือคอมไพล์ .iss ด้วยตัวเอง", Y)
            return WARN
    rc, text = run_with_spinner([iscc, iss], "กำลังสร้างตัวติดตั้ง",
                                log_path=here("installer_log.txt"))
    out = installer_outputs()
    if rc == 0 and out:
        newest = max(out, key=os.path.getmtime)
        say(f"สร้างสำเร็จ: {inst['output_dir']}{os.sep}{os.path.basename(newest)}", G)
        return OK
    say("สร้างตัวติดตั้งไม่สำเร็จ", R)
    for r in tail(text, 6):
        print(f"      {D}{r[:110]}{X}")
    return WARN


# ═══ รายงานรวม + โหมด --logs ═══════════════════════════════════
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class _Transcript:
    """จับทุกอย่างที่พิมพ์ออกหน้าจอ เพื่อเอาไปใส่รายงาน"""

    def __init__(self, orig):
        self.orig, self.buf = orig, []

    def write(self, s):
        self.buf.append(s)
        return self.orig.write(s)

    def flush(self):
        self.orig.flush()

    def __getattr__(self, a):
        return getattr(self.orig, a)

    def text(self):
        raw = ANSI_RE.sub("", "".join(self.buf))
        lines = [ln.split("\r")[-1].rstrip() for ln in raw.split("\n")]
        out, blank = [], 0
        for ln in lines:
            blank = blank + 1 if not ln.strip() else 0
            if blank <= 1:
                out.append(ln)
        return "\n".join(out)


def _tail_file(path, n=80):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return "\n".join(f.read().splitlines()[-n:]) or "(ว่าง)"
    except OSError:
        return "(ไม่มีไฟล์)"


def write_report(transcript, results):
    import platform
    parts = [f"AutoBuild report — {time.strftime('%Y-%m-%d %H:%M:%S')}",
             f"OS: {platform.platform()} | Python {sys.version.split()[0]} | {sys.executable}",
             "ผลแต่ละขั้น: " + ", ".join(f"{t} = {st}" for t, st in results)]
    vers = []
    try:
        from importlib.metadata import version
        for p in CFG.get("python_packages", []):
            try:
                vers.append(f"{p['pip']}=={version(p['pip'])}")
            except Exception:
                vers.append(f"{p['pip']} (ไม่ได้ติดตั้ง)")
    except Exception:
        pass
    sections = [
        ("ไลบรารีที่ใช้ (เวอร์ชันในเครื่องนี้)", ", ".join(vers) or "-"),
        ("ค่า config ที่ใช้จริง", json.dumps(CFG, ensure_ascii=False, indent=2, default=str)),
        ("ข้อความบนหน้าจอตลอดการรัน", transcript),
        ("build_log (ท้าย 80 บรรทัด)", _tail_file(here("logs", "build_last.log"), 80)),
        ("PyInstaller warn (โมดูลที่หาไม่เจอ)", "\n".join(
            [ln for ln in _tail_file(here("logs", "build_warn_last.txt"), 4000).splitlines()
             if ln.startswith("missing module")][:40]) or "-"),
        ("log ตอนทดสอบเปิด EXE", _tail_file(here("logs", "test_run_last.log"), 80)),
        ("log ของโปรแกรม (app.log ท้าย 120 บรรทัด)", _tail_file(runtime_log_path(), 120)),
    ]
    for title, body in sections:
        parts.append("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70 + f"\n{body}")
    path = here("autobuild_report.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts) + "\n")
    except OSError:
        return None
    return path


def step_logs():
    lp = runtime_log_path()
    say("log ของโปรแกรม (ที่ EXE เขียนตอนทำงาน):")
    say(lp, D)
    if not os.path.isfile(lp):
        say("ยังไม่มี log — เปิด EXE ที่ build ด้วยสคริปต์นี้อย่างน้อย 1 ครั้งก่อน", Y)
        return WARN
    session = _last_session(_read_from(lp))
    n = len(session.splitlines())
    say(f"การเปิดโปรแกรมครั้งล่าสุด: {n} บรรทัด", D)
    findings = analyze_log(session)
    if not findings:
        say("ไม่พบข้อผิดพลาดที่รู้จักใน log ครั้งล่าสุด", G)
        for r in tail(session, 5):
            print(f"      {D}{r[:110]}{X}")
        return OK
    show_findings(findings)
    fixes = apply_fixes(findings)
    for fx in fixes:
        say("แก้อัตโนมัติ: " + fx, G)
    if fixes:
        say("รัน  python setup_build.py  เพื่อ build ใหม่ด้วยค่าที่แก้แล้ว", Y)
    return WARN


# ═══ ตัวรันหลัก ═════════════════════════════════════════════
def main():
    global ASSUME_YES, HERE, BUILD_LOG

    ap = argparse.ArgumentParser(description="สแกนโปรเจกต์ Python แล้ว build เป็น EXE อัตโนมัติ")
    ap.add_argument("--project", help="โฟลเดอร์โปรเจกต์ (ค่าเริ่มต้น: โฟลเดอร์ของสคริปต์)")
    ap.add_argument("--config", help="ไฟล์ config (ค่าเริ่มต้น: autobuild.json ในโปรเจกต์)")
    ap.add_argument("--scan-only", action="store_true", help="สแกนแล้วแสดงผลอย่างเดียว")
    ap.add_argument("--init", action="store_true", help="บันทึกผลสแกนเป็น autobuild.json")
    ap.add_argument("--dry-run", action="store_true", help="แสดงคำสั่ง PyInstaller โดยไม่ build")
    ap.add_argument("--yes", action="store_true", help="ตอบรับค่าเริ่มต้นทุกคำถาม")
    ap.add_argument("--no-scan", action="store_true", help="ปิดการสแกน ใช้เฉพาะ config")
    ap.add_argument("--type", choices=sorted(LABELS), help="บังคับชนิดโปรเจกต์ (ค่าเริ่มต้น: ตรวจเอง)")
    ap.add_argument("--logs", action="store_true", help="ดึง/วิเคราะห์ log ของโปรแกรมที่ build แล้ว")
    args = ap.parse_args()
    ASSUME_YES = args.yes
    tr = _Transcript(sys.stdout)
    sys.stdout = tr

    if args.project:
        HERE = os.path.abspath(args.project)
        if not os.path.isdir(HERE):
            print(f"ไม่พบโฟลเดอร์: {HERE}")
            sys.exit(1)
    os.chdir(HERE)
    BUILD_LOG = here("build_log.txt")
    cfg_path = os.path.abspath(args.config) if args.config else here("autobuild.json")
    if args.config and not os.path.isfile(cfg_path):
        print(f"ไม่พบไฟล์ config: {cfg_path}")
        sys.exit(1)

    def T(py, other):
        return lambda: other() if (_is_generic() and callable(other)) else (other if _is_generic() else py)

    steps = [
        ("สแกนโปรเจกต์อัตโนมัติ",           lambda: step_scan(cfg_path, args)),
        (T("ตรวจ Python และไฟล์โปรเจกต์", "ตรวจไฟล์โปรเจกต์"),
         lambda: step_check_generic() if _is_generic() else step_check()),
        (T("ติดตั้งไลบรารี Python (ทีละตัว)", "ตรวจ/ติดตั้งเครื่องมือ build (toolchain)"),
         lambda: step_tools() if _is_generic() else step_pip()),
        (T("ติดตั้งเครื่องมือเสริม", "ติดตั้ง dependencies ของโปรเจกต์"),
         lambda: step_deps_generic() if _is_generic() else step_tools()),
        ("Windows Defender (กัน EXE ถูกกักกัน)", step_defender),
        (T("Build ด้วย PyInstaller", lambda: "Build: " + CFG.get("builder", {}).get("label", "")),
         lambda: step_build_generic(args.dry_run) if _is_generic() else step_build(args.dry_run)),
        ("ทดสอบเปิดโปรแกรม",                 lambda: step_test_generic() if _is_generic() else step_test()),
        ("สร้างตัวติดตั้ง Setup.exe",         step_installer),
    ]
    if args.logs:
        steps = [steps[0], ("ดึงและวิเคราะห์ log ของโปรแกรม", step_logs)]
    elif args.scan_only or args.init:
        steps = steps[:1]
    elif args.dry_run:
        steps = [steps[0], steps[1], steps[5]]

    print()
    print(f"{M}  Auto Build{X} — สแกนโปรเจกต์และ build อัตโนมัติ\n")
    say("โปรเจกต์: " + HERE, D)
    say("ระบบจะทำทีละขั้นตอน ถ้าขั้นไหนต้องตัดสินใจจะถามก่อนเสมอ", D)

    results, titles_done = [], []
    total = len(steps)
    for i, (title, fn) in enumerate(steps, 1):
        title = title() if callable(title) else title
        header(i, total, title)
        titles_done.append(title)
        try:
            st = fn()
        except KeyboardInterrupt:
            print()
            say("ยกเลิกโดยผู้ใช้", Y)
            st = FAIL
        except Exception as ex:                      # กันสคริปต์ล้มกลางคัน
            say(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {ex}", R)
            st = FAIL
        results.append((title, st))
        if st == FAIL:
            break

    print()
    print(f"{M}  สรุปผล{X}\n")

    for title, st in results:
        print(f"  {ICON[st]}  {title}")
    for title, _ in steps[len(results):]:
        title = title() if callable(title) else title
        print(f"  {ICON[SKIP]}  {D}{title} (ไม่ได้ทำ){X}")

    print()
    if CFG.get("app_name") and os.path.isfile(exe_path()):
        say("EXE: " + exe_path(), G)
    out = installer_outputs() if CFG.get("installer", {}).get("enabled") else []
    if out:
        say("ตัวติดตั้ง: " + max(out, key=os.path.getmtime), G)
    failed = any(st == FAIL for _, st in results)
    if not (args.scan_only or args.init or args.dry_run):
        rp = write_report(tr.text(), results)
        if rp:
            say("รายงานทั้งหมด: " + rp, G)
            say("(ถ้ามีปัญหา ส่งไฟล์นี้ไฟล์เดียวมาให้ดูได้เลย)", D)
    print()
    if not ASSUME_YES and not (args.scan_only or args.init or args.dry_run):
        try:
            input("  กด Enter เพื่อปิด…")
        except EOFError:
            pass
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()