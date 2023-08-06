from setuptools import setup, find_packages

setup(
      name = 'archicv',
      version = '0.0.1.1',
      keywords = ('archicv', 'ArchiCV', 'archi', 'archiCV'),
      url = 'https://github.com/zhangxiansheng/-archi',
      description = 'OpenCV on Landscape Architecture',
      license = 'MIT License',
      install_requires = ['opencv>=2.0', 'numpy>=1.0'],
      
      author = 'Zhang Yiwei',
      author_email = 'Karl1991223@126.com',
      
      packages = find_packages(),
      platforms = 'any',
      )