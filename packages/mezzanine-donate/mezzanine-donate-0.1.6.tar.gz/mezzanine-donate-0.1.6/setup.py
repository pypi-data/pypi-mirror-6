from setuptools import setup, find_packages

setup(
    name="mezzanine-donate",
    version='0.1.6',
    author="Krzysztof Klimonda",
    author_email="krzysztof@vannoppen.co",
    description="Donate plugin for mezzanine using stripe "
                "for processing donations",
    license="BSD",
    zip_safe=False,
    package_dir={'': 'src'},
    package_data={
        'mezzanine_donate': [
            'templates/admin/mezzanine_donate/*',
            'templates/forms/*',
            'templates/pages/*'
        ]
    },
    packages=find_packages("src"),
    install_requires=["Mezzanine >= 1.4.6", "South", "stripe >= 1.9.8",
                      "django-localflavor"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
    ]
)
