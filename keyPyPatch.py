import sys, winreg, ctypes, random, os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class HttpDebuggerCore:
    REG_PATH = r"Software\MadeForNet\HTTPDebuggerPro"

    @staticmethod
    def write_to_registry(key_name, license_key):
        try:
            # Replicates winreg logic
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, HttpDebuggerCore.REG_PATH, 0, winreg.KEY_SET_VALUE)
            with key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, str(license_key))
        except Exception as e:
            raise Exception(f"Registry Error: {e}")

    @staticmethod
    def get_httpdebugger_version():
        try:
            # Logic to find and format the version string from Registry
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, HttpDebuggerCore.REG_PATH, 0, winreg.KEY_READ)
            with key:
                version_full, _ = winreg.QueryValueEx(key, "AppVer")
                version_str = version_full.split()[-1].replace(".", "")
                return int(version_str)
        except Exception:
            return 0

    @staticmethod
    def get_volume_serial_number():
        # Replicates winsafe::GetVolumeInformation logic
        serial_number = ctypes.c_uint32(0)
        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p("C:\\"), None, 0, 
            ctypes.byref(serial_number), None, None, None, 0
        )
        return serial_number.value

    @staticmethod
    def create_registry_key_name(version):
        # Replicates specific bitwise math for SN generation
        serial_number = HttpDebuggerCore.get_volume_serial_number()
        not_serial = (~serial_number) & 0xFFFFFFFF
        calc = version ^ ((not_serial >> 1) + 736) ^ 0x590D4
        return f"SN{(calc & 0xFFFFFFFF)}"

    @staticmethod
    def create_license_key():
        r1 = random.getrandbits(8)
        r2 = random.getrandbits(8)
        r3 = random.getrandbits(8)
        parts = [f"{r1:02X}", f"{(r2 ^ 0x7C):02X}", f"{(~r1 & 0xFF):02X}", "7C", f"{r2:02X}", f"{r3:02X}", f"{(r3 ^ 7):02X}", f"{(r1 ^ (~r3 & 0xFF)):02X}"]
        return "".join(parts)

class HttpDebuggerKeygen(QWidget):
    def __init__(self):
        super().__init__()
        self.version = HttpDebuggerCore.get_httpdebugger_version()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Http Debugger Pro 9.x Patcher")
        self.setFixedSize(370, 180)

        # SHOW THE ICON IN APP
        icon_path = resource_path("src/ss.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Fix for Windows Taskbar and prevents showing the default Python icon
        my_appid = 'mycompany.myproduct.subproduct.version' # test string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_appid)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        mono_font = QFont("Consolas", 10)

        # Version Display
        layout.addWidget(QLabel("Installed Version", alignment=Qt.AlignmentFlag.AlignCenter))
        self.lbl_version = QLabel(str(self.version))
        self.lbl_version.setFont(mono_font)
        self.lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_version)

        # License Key Display
        layout.addWidget(QLabel("License Key", alignment=Qt.AlignmentFlag.AlignCenter))
        self.lbl_license = QLabel("*******")
        self.lbl_license.setFont(mono_font)
        self.lbl_license.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_license.setStyleSheet("border: 1px solid #ccc; padding: 5px; background: #f9f9f9;")
        layout.addWidget(self.lbl_license)

        # Make Button (Resized smaller)
        self.btn_make = QPushButton("Patch")
        self.btn_make.setFixedWidth(80) # Fixed small width
        self.btn_make.clicked.connect(self.on_make_clicked)
        
        # Center the button manually in the layout
        layout.addWidget(self.btn_make, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def on_make_clicked(self):
        try:
            reg_key_name = HttpDebuggerCore.create_registry_key_name(self.version)
            lic_key = HttpDebuggerCore.create_license_key()
            HttpDebuggerCore.write_to_registry(reg_key_name, lic_key) # > save to Windows Registry
            self.lbl_license.setText(lic_key)
            QMessageBox.information(self, "Success", "Registry patch success!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HttpDebuggerKeygen()
    window.show()
    sys.exit(app.exec())