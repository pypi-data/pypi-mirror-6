try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
      name = 'PracticeWordament',
      version = '1.0',
      author = 'Sandeep Dasika',
      author_email = 'dasika.sandy@gmail.com',
      packages = ['practicewordament', 'practicewordament.utils',],
      url = 'http://pypi.python.org/gravetii/PracticeWordament',
      license = open('LICENSE.txt').read(),
      description = 'A mimic of the popular word game Wordament',
      long_description = open('README.md').read(),
	  install_requires = ["PyTrie>=0.2",],
	  data_files = [('practicewordament/utils/images/alphabet', ['practicewordament/utils/images/alphabet/a.png', 'practicewordament/utils/images/alphabet/b.png', 'practicewordament/utils/images/alphabet/c.png', 'practicewordament/utils/images/alphabet/d.png', 'practicewordament/utils/images/alphabet/e.png', 'practicewordament/utils/images/alphabet/f.png', 'practicewordament/utils/images/alphabet/g.png', 'practicewordament/utils/images/alphabet/h.png', 'practicewordament/utils/images/alphabet/i.png', 'practicewordament/utils/images/alphabet/j.png', 'practicewordament/utils/images/alphabet/k.png', 'practicewordament/utils/images/alphabet/l.png', 'practicewordament/utils/images/alphabet/m.png', 'practicewordament/utils/images/alphabet/n.png', 'practicewordament/utils/images/alphabet/o.png', 'practicewordament/utils/images/alphabet/p.png', 'practicewordament/utils/images/alphabet/q.png', 'practicewordament/utils/images/alphabet/r.png', 'practicewordament/utils/images/alphabet/s.png', 'practicewordament/utils/images/alphabet/t.png', 'practicewordament/utils/images/alphabet/u.png', 'practicewordament/utils/images/alphabet/v.png', 'practicewordament/utils/images/alphabet/w.png', 'practicewordament/utils/images/alphabet/x.png', 'practicewordament/utils/images/alphabet/y.png', 'practicewordament/utils/images/alphabet/z.png', ]),
			('practicewordament/utils/images/skins', ['practicewordament/utils/images/skins/1.jpg', 'practicewordament/utils/images/skins/2.jpg', 'practicewordament/utils/images/skins/3.jpg']),
			('practicewordament/utils', ['practicewordament/utils/words.dump']),
			('practicewordament/utils/sounds', ['practicewordament/utils/sounds/alarm.wav']),],
      )
