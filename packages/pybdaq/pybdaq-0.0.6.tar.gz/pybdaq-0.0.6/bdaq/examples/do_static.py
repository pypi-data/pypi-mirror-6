import bdaq


def main():
    # open the device
    instant_do = bdaq.InstantDoCtrl()

    instant_do.selected_device = bdaq.DeviceInformation(number=0)

    # write DO ports
    instant_do.write([True, True, True, True, False, False, False, False])

    print "DO output completed!"

if __name__ == "__main__":
    main()
