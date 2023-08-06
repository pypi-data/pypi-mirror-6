"""
Flask-Imgur
-----------


This is simple flask extension allowing uploading
images straight to Imgur image hosting service.


"""


from setuptools import setup

setup(
    name="Flask-Imgur",
    packages=["flask_imgur"],
    version="0.1",
    description="Upload images straight to Imgur in your Flask app",
    url="https://github.com/exaroth/flask-imgur",
    license="BSD",
    author="Konrad Wasowicz",
    author_email="exaroth@gmail.com",
    long_description=__doc__,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=["Flask", "six"],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
