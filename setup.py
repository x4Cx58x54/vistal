import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'vistal',
    version = '0.0.1',
    author = 'x4Cx58x54',
    description = 'A visualization tool for temporal action localization',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    keywords = [
        'visualization',
        'temporal action localization',
        'action segmentation',
        'computer vision',
        'video understanding',
    ],
    url = 'https://github.com/x4Cx58x54/vistal',
    project_urls = {
        'Homepage': 'https://github.com/x4Cx58x54/vistal',
        'Bug Tracker': 'https://github.com/x4Cx58x54/vistal/issues',
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Video',
    ],
    packages = setuptools.find_packages(),
    python_requires = '>=3.6',
    install_requires = [
        'distinctipy>=1.2.2',
    ],
)
