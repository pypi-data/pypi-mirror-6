from setuptools import setup
    
setup(
    name = "bakemate",
    py_modules = ["bakemate"],
    #scripts = [""],
    zip_safe=False,
    version = "0.5",
    license = "LGPL",
    install_requires=["requests"],
    description = "a baker helper",
    author = "karasuyamatengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/py-bakemate",
    keywords = ["baker"],
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        ],
    long_description = """see https://github.com/tengu/py-bakemate"""
    )
