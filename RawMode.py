import os
if os.name == "posix":
    import sys
    import tty
    import termios

    def posix_getch():
        return sys.stdin.read(1)
    old_settings = termios.tcgetattr(sys.stdin)

    def posix_enable():
        tty.setcbreak(sys.stdin.fileno())

    def posix_restore():
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
elif os.name == "nt":
    import msvcrt
    def nt_getch():
        while True:
            if msvcrt.kbhit():
                return msvcrt.getwch()
