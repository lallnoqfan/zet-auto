from sys import argv


if __name__ == '__main__':

    if len(argv) > 1:
        from app import ArgsParser as App
    else:
        from app import InquirerApp as App

    try:
        App.run()
    except KeyboardInterrupt:
        print("\nStopped by keyboard")
