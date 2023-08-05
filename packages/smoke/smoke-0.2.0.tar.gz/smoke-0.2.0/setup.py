from setuptools import setup

setup(
    name='smoke',
    py_modules=['smoke'],
    version='0.2.0',
    author='David Keijser',
    author_email='keijser@gmail.com',
    description='concise publish/subscribe utility',
    license='MIT',
    keywords='publish subscribe pubsub signal',
    extras_require={'tests': ['PyHamcrest']}
)
