from sys import argv
from os.path import exists
from terminal import MyTerminal


def main():
    if len(argv) >= 5:
        user_name = argv[1]
        fs_path = argv[2]
        log_file = argv[3]
        start_script = argv[4]
    else:
        print('Введены не все ключи для корректного запуска')
        return

    if not exists(fs_path):
        print("Файловая система с таким названием отсутствует")
        return

    terminal = MyTerminal(user_name, fs_path, log_file, start_script)
    terminal.exec_start_script()
    terminal.start_polling()


if __name__ == '__main__':
    main()
