from distutils.core import setup

import version


setup(name='task_scheduler',
      version=version.getVersion(),
      description='Schedule tasks based on requested relative partial '
      'ordering.',
      keywords='schedule task constraint',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/cfobel/task_scheduler.git',
      license='GPL',
      packages=['task_scheduler'])
