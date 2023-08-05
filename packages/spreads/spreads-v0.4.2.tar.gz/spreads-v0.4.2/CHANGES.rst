0.4.2 (2014/01/05)
    - Fix packaging issues
    - Small bugfix for older Tesseract versions

0.4.1 (2013/12/25)
    - Fix 'spread' tool
    - Include missing 'vendor' package in distribution

0.4 (2013/12/25)
    - Use `chdkptp` utility for controlling cameras with CHDK firmware
    - Fix instability when shooting with CHDK cameras
    - Shoot images in RAW/DNG file format *(experimental)*
    - Remove `download` step, images will be directly streamed to the project
      directory
    - Remove `combine` plugin, images will be combined in `capture` step
    - Device driver and plugins, as well as their order of execution can be set
      interactively via the `configure` subcommand, which has to be run before
      the first usage.
    - Lots of internal API changes

0.3.3 (2013/08/28)
    - Fix typo in device manager that prevent drivers from being loaded

0.3.2 (2013/08/24)
    - fixes a problem with the devices drivers

0.3.1 (2013/08/23)
    - fixes a problem that prevented spreads to be installed

0.3 (2013/08/23)
    - Plugins can add completely new subcommands.
    - GUI plugin that provides a graphical workflow wizard.
    - Tesseract plugin that can perform OCR on captured images.
    - pdfbeads plugin can include recognized text in a hidden layer if OCR has
      been performed beforehand.
    - Use EXIF tags to persist orientation information instead of JPEG
      comments.
    - Better logging with colorized output
    - Simplified multithreading/multiprocessing code
    - CHDK driver is a lot more stable now

0.2 (2013/06/30)
    - New plugin system based on Doug Hellmann's `stevedore` package,
      allows packages to extend spreads without being included in the core
      distribution
    - The driver for CHDK cameras no longer relies on gphoto2 and ptpcam,
      but relies on Abel Deuring's `pyptpchdk` package to communicate with
      the cameras.
    - `Wand` is now used to deal with image data instead of `Pillow`
    - New 'colorcorrection' plugin allows users to automatically correct
      white balance.
    - Improved tutorial

0.1 (2013/06/23)
    Initial release
