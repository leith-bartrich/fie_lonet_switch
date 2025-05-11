import sys

if sys.platform == "darwin":
    from fie_lonet_switch.tray_mac import main
else:
    from fie_lonet_switch.tray import main

if __name__ == "__main__":
    main()
