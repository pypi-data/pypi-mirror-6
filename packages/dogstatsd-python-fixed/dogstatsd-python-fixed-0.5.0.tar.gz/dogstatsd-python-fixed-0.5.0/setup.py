from setuptools import setup, find_packages
import sys


setup(
    name = "dogstatsd-python-fixed",
    version = "0.5.0",
    author = "Datadog, Inc. (packages@datadoghq.com), Steve Leonard",
    author_email = "sleonard76@gmail.com",
    description = "Python bindings to Datadog's API and a user-facing command line tool.",
    py_modules=['dogstatsd'],
    license = "BSD",
    keywords = "datadog data statsd dogstatsd metrics",
    url = "http://www.datadoghq.com",
)
