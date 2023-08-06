from distutils.core import setup

setup(
      name = 'SimpleORM'
    , py_modules = ['simpleorm']
    , scripts = ['simpleorm.py']
    , version = '0.1.0'
    , license = 'LGPL'
    , platforms = ['MacOS', 'POSIX']
    , description = 'Simple SQLite3 Object Relational Mapper for Python.'
    , author = 'hideshi'
    , author_email = 'hideshi.ogoshi@gmail.com'
    , url = 'https://github.com/hideshi/SimpleORM'
    , keywords = ['SQLite3', 'ORM', 'Framework']
    , classifiers = [
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)'
        , 'Operating System :: MacOS :: MacOS X'
        , 'Operating System :: POSIX :: Linux'
        , 'Programming Language :: Python'
        , 'Development Status :: 4 - Beta'
        , 'Environment :: Web Environment'
        , 'Environment :: Console'
        , 'Intended Audience :: Developers'
        , 'Topic :: Software Development :: Libraries :: Application Frameworks'
        , 'Topic :: Database'
        ]
    , long_description = """\
Simple SQLite3 Object Relational Mapper for Python.

Requirements
------------
* Python 3.3 or later

Features
--------
* Under construction

Setup
-----
::

   $ pip install SimpleORM

History
-------
0.1.0 (2014-03-13)
~~~~~~~~~~~~~~~~~~
* first release

Example
-------

.. code-block:: python

    from simpleorm import BaseDao
    from classes import Employee
    from collections import OrderedDict

    class SelectEmployeeAll(BaseDao):
        sql = '''
    SELECT A.ID
          ,A.NAME
          ,B.NAME AS BOSS_NAME
      FROM EMPLOYEE A
      LEFT OUTER JOIN EMPLOYEE B
        ON B.ID = A.BOSS
    '''

    if __name__ == '__main__':
        param = OrderedDict()
        result = SelectEmployeeAll(dbfile = 'test.db', return_type = Employee).execute(param)
        for elem in result:
            print(elem.id, elem.name, elem.boss_name)

.. code-block:: python

    class Employee:
        id = None
        name = None
        boss_name = None

"""
)
