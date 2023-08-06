from setuptools import setup

setup(
    name="flylog",
    version='0.1.18',
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
