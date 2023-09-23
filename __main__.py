from app import ArgsParser as App


if __name__ == '__main__':
    try:
        App()
    except KeyboardInterrupt:
        print("\nStopped by keyboard")
