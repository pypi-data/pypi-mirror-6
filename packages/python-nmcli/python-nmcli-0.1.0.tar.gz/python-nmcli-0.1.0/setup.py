from distutils.core import setup

setup(name='python-nmcli',
      version='0.1.0',
      description='Python wrapper around nmcli',
      author='Zach Goldberg',
      author_email='zach@zachgoldberg.com',
      url='https://github.com/ZachGoldberg/python-nmcli',
      packages=[
        'nmcli',
        ],
      classifiers=['Development Status :: 3 - Alpha'],
      long_description="""
Just a simple wrapper around nmcli.

>>> import nmcli
>>> dir(nmcli)
['__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__', 'con', 'dev', 'nm', 'nmcli', 'shell']
>>> nmcli.nm.status()
[{'WIFI': 'enabled', 'STATE': 'connected', 'WWAN': 'enabled', 'WWAN-HARDWARE': 'enabled', 'RUNNING': 'running', 'WIFI-HARDWARE': 'enabled'}]
>>> nmcli.nm.enable(True)
[]
>>> nmcli.con.list()
[{'TIMESTAMP-REAL': 'never', 'TYPE': 'vpn', 'NAME': 'starbuckswifi', 'UUID': 'a8a95280-f938-46b9-a58a-d71d71c6d37e'}, {'TIMESTAMP-REAL': 'never', 'TYPE': 'vpn', 'NAME': 'marriot', 'UUID': '56e66de7-7902-42b4-bf6d-2a4a36d051d1'....
>>> nmcli.con.list(id="marriot")
[{'dhcp-send-hostname': 'yes....


"""
     )
