from setuptools import setup, find_packages

setup(
    name="ZhihuSpider",
    version="0.5",
    packages=find_packages(),
    url='https://github.com/aerfensi/zhihu-spider',
    scripts=['zhspider.py'],
    install_requires=[
        'requests',
        'bs4',
        'lxml',
        'pillow',
        'html2text'
    ],
    author="Kinuxer",
    author_email="kinuxer@outlook.com",
    description="download answers and images from zhihu",
)
