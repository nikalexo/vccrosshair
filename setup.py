from setuptools import setup
setup(
    name = 'vccrosshair',
    version = '0.1.0',
    packages = ['vccrosshair'],
    entry_points = {
        'console_scripts': [
            'vccrosshair = vccrosshair.__main__:main'
        ]
    })
