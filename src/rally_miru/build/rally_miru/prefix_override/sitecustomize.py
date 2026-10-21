import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/media/fathirwin/New Volume/Kuliah/TC/Ichiro Intern/KPP2/tugas2-ichiro/src/rally_miru/install/rally_miru'
