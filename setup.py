import PyInstaller.__main__ as pyinstaller_main


def get_version():
    with open("version.txt", "r") as f:
        version = f.read().strip()
    return version


version = get_version()

args = [
    './src/main.py',
    '-F',
    '-i=favicon.ico',
    f'--name=LaravelQueueManager-{version}',
    '--console',
]

# 调用 pyinstaller 进行打包
pyinstaller_main.run(args)
