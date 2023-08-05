from setuptools import setup
import svdog

setup(
    name="svdog",
    version=svdog.__version__,
    zip_safe=False,
    platforms='any',
    packages=['svdog'],
    install_requires=['flylog'],
    scripts=['svdog/bin/run_svdog.py'],
    url="https://github.com/dantezhu/svdog",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="supervisor's dog, should deploy with flylog",
)
