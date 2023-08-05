from distutils.core import setup

setup(name='scr_dim',
    version='0.4.0',
    description='Make your screen darker when it is too bright',
    author='N.Sukegawa',
    author_email='nsukeg@gmail.com',
    url='https://github.com/nsuke/scr_dim',
    packages=['scr_dim', 'scr_dim.tests'],
    scripts=['scr-dim'],
    license='MIT',
    )
