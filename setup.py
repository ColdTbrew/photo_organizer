from setuptools import setup

APP = ['photo_organizer.py']  # 메인 Streamlit 스크립트 파일 이름
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['streamlit', 'plotly', 'exifread'],
    'excludes': ['PyInstaller', 'django'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)