from setuptools import setup
import flylog

setup(
    name="flylog",
    version=flylog.__version__,
    zip_safe=False,
    platforms='any',
    packages=['flylog'],
    scripts=['flylog/bin/run_flylog_agent.py'],
    url="https://github.com/dantezhu/flylog",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="make log fly to mail or other",
)
