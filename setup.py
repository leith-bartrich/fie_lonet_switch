from setuptools import setup

APP = ['fie_lonet_switch/tray_entry.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,  # Set to a .icns file path if you have a custom icon
    'packages': ['fie_lonet_switch'],
    'plist': {
        'CFBundleName': 'FIE Lonet Switch',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'CFBundleIdentifier': 'com.yourdomain.fielonetswitch',
        'LSBackgroundOnly': True,  # Hide dock icon and terminal window
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
