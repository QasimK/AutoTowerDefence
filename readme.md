# Auto Tower Defence

A program to automatically play the tower defence game [FrozenDefence2](http://pivotfinland.com/frozendefence2/). Although the game is no longer fully-functional.

**The program has not been updated for the current iteration of the game (Last checked, September 2014).**

## Notes

- Detecting the game is *currently* highly-dependent on the OS, browser, page zoom level, system DPI, and perhaps other factors.
    - You may need to disable DPI scaling for python.exe.
    - You may need to adjust the detection of game elements in the code manually.
- Developed on Windows 8 with Google Chrome at 100% DPI and zoom level.

## Dependencies

- Python 3 (Developed with 32-bit)
- [Pywin32](http://sourceforge.net/projects/pywin32/)
- [Pillow](https://python-pillow.github.io/). (`pip install pillow`)
