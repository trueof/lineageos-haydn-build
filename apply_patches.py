#!/usr/bin/env python3
"""Apply kABI patches for DroidSpaces on GKI 5.4 kernel"""

import os

def patch_sched_h():
    filepath = 'include/linux/sched.h'
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Patch 1: Comment out sysvsem/sysvshm in their original position
    content = content.replace(
        '\tstruct sysv_sem\t\t\tsysvsem;',
        '\t// struct sysv_sem\t\t\tsysvsem;'
    )
    content = content.replace(
        '\tstruct sysv_shm\t\t\tsysvshm;',
        '\t// struct sysv_shm\t\t\tsysvshm;'
    )
    
    # Patch 2: Replace KABI reserves 6/7/8 with conditional SYSVIPC version
    old = '\tANDROID_KABI_RESERVE(6);\n\tANDROID_KABI_RESERVE(7);\n\tANDROID_KABI_RESERVE(8);'
    new = """#ifdef CONFIG_SYSVIPC
\tANDROID_KABI_USE(6, struct sysv_sem sysvsem);
\t_ANDROID_KABI_REPLACE(ANDROID_KABI_RESERVE(7); ANDROID_KABI_RESERVE(8), struct sysv_shm sysvshm);
#else
\tANDROID_KABI_RESERVE(6);
\tANDROID_KABI_RESERVE(7);
\tANDROID_KABI_RESERVE(8);
#endif"""
    content = content.replace(old, new)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

def patch_user_h():
    filepath = 'include/linux/sched/user.h'
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Patch 1: Comment out mq_bytes in its original position
    content = content.replace(
        '\tunsigned long mq_bytes;',
        '\t//unsigned long mq_bytes;'
    )
    
    # Patch 2: Replace KABI reserves 1/2 with conditional POSIX_MQUEUE version
    old = '\tANDROID_KABI_RESERVE(1);\n\tANDROID_KABI_RESERVE(2);\n};'
    new = """#if defined(CONFIG_POSIX_MQUEUE)
\tANDROID_KABI_USE(1, unsigned long mq_bytes);
\tANDROID_KABI_RESERVE(2);
\tANDROID_OEM_DATA_ARRAY(1, 2);
#else
\tANDROID_KABI_RESERVE(1);
\tANDROID_KABI_RESERVE(2);
\tANDROID_OEM_DATA_ARRAY(1, 2);
#endif
};"""
    content = content.replace(old, new)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

if __name__ == '__main__':
    os.chdir('kernel')
    patch_sched_h()
    patch_user_h()
    print("kABI patches applied successfully!")
