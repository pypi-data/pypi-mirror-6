import os
import glob
import fnmatch
from sacrud import version
from setuptools import setup


def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

badnames = [".pyc", ".py", "~", "no_"]


def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if not any(bad in filename for bad in badnames):
                    if fnmatch.fnmatch(filename, wc_name)\
                            and not os.path.isdir(filename):
                        names.append(filename)
        if names:
            lst.append((dirname, names))

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list
files = find_data_files('sacrud/', '*.*')
print 'files', files

setup(
    name='sacrud',
    version=version.__version__,
    url='http://github.com/uralbash/sacrud/',
    author='Svintsov Dmitry',
    author_email='root@uralbash.ru',

    packages=['sacrud', 'sacrud.pyramid_ext', 'sacrud.common'],
    data_files=files,
    include_package_data=True,
    zip_safe=False,
    test_suite="sacrud.tests",
    license="GPL",
    package_dir={'sacrud': 'sacrud'},
    package_data={
        'sacrud': ['static/style/*.css',
                   'static/js/*.js',
                   'static/js/jquery/*.js',
                   'static/images/*',
                   'templates/*.jinja2', 'templates/forms/*.jinja2',
                   'templates/forms/actions/*.jinja2',
                   'templates/types/*.jinja2',
                   'tests/*.py', ],
        'sacrud.pyramid_ext': ['tests/*.py']
    },
    description='SQLAlchemy CRUD.',
    long_description=open('README.txt').read(),
    install_requires=[
        "sqlalchemy",
        "transaction",
        'zope.sqlalchemy',
        'webhelpers',
        'webtest',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Framework :: Pyramid ",
        "Framework :: Flask",
        "Topic :: Internet",
        "Topic :: Database",
        "License :: Repoze Public License",
    ],
)
