from setuptools import setup

setup(name='MongoTest',
    version='0.1.0',
    author = "idbentley",
    author_email = 'ian.bentley@gmail.com',
    url = "https://github.com/idbentley/mongo_test",
    packages=['mongo_test'],
    description = """A Python library to ease testing applications that rely on
    MongoDB as a datastore""",
    long_description = open('README.rst').read(),
    license = "LICENSE.txt",
    keywords = "python MongoDB fixture test ",
    install_requires=[
        "PyYaml",
        "pymongo"
    ],
)
