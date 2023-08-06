from setuptools import setup


setup(
    name='${package_name}',
    version='0.1.dev0',
    description='Tangled ${package} integration (core)',
    long_description=open('README.rst').read(),
    author='${author}',
    author_email='${author}@example.com',
    url='http://example.com/',
    packages=[
        '${package_name}',
        '${package_name}.tests',
    ],
    install_requires=[
        'tangled>=${version_tangled}',
    ],
    extras_require={
        'dev': [
            'tangled[dev]',
        ],
    },
    entry_points="""
    [tangled.scripts]
    ${package} = ${package_name}.command:Command

    """,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
