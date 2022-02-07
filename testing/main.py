import os

def main():
    print(os.popen('df -h').read())

if __name__ == "__main__":
    main()

