from setuptools import setup

setup(
    name="svdog",
    version='0.1.10',
    zip_safe=False,
    platforms='any',
    packages=['svdog'],
    install_requires=['supervisor', 'flylog'],
    scripts=['svdog/bin/run_svdog.py'],
    url="https://github.com/dantezhu/svdog",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="supervisor's dog, should deploy with flylog",
)
