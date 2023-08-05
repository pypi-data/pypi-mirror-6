from setuptools import setup, find_packages

setup(
        author='Ana Nelson',
        author_email='ana@ananelson.com',
        classifiers=[
            "License :: OSI Approved :: MIT License"
            ],
        description='Templates used in Dexy User Guide',
        entry_points = {
            },
        include_package_data = True,
        install_requires = [
            ],
        name='dexy_user_guide_templates',
        packages=find_packages(),
        url="http://dexy.it",
        version="0.0.3a"
        )
