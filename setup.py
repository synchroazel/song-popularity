from distutils.core import setup

setup(name='Handlers',
      version='1.0',
      description='Handler classes for technologies used in the project.',
      author='Antonio Padalino & Milena Atanasova',
      author_email='antoniopio.padalino@studenti.unitn.it',
      url='https://github.com/synchroazel/song-popularity',
      packages=['handlers', 'handlers.music', 'handlers.mysql', 'handlers.mqtt']
      )

