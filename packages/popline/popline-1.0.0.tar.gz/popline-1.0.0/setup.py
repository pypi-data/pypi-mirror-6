from setuptools import setup

setup(
    name="popline",
    version="1.0.0",
    author="Rory McCann",
    author_email="rory@technomancy.org",
    py_modules=['popline'],
    platforms=['any',],
    requires=[],
    license="GPLv3+",
    entry_points={
        'console_scripts': [
            'popline = popline:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: Console',
    ],
)
