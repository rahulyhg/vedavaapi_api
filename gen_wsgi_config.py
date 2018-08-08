import os, os.path, sys, getpass


class Config(object):
    wsgi_confdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wsgi/')
    wsgi_apache_config_file = os.path.join(wsgi_confdir, 'wsgi_apache_vedavaapi.conf')
    wsgi_apache_config_template_file = os.path.join(wsgi_confdir, 'wsgi_apache_template.conf')



'''
generate apache config from template.
equivalent to getconf.py
'''
user = getpass.getuser()
pwd = os.getcwd()

if not os.path.exists(Config.wsgi_confdir):
    os.makedirs(Config.wsgi_confdir)
with open(Config.wsgi_apache_config_template_file) as f:
    content = f.read()
    content = content.replace('$USER', user).replace('$GROUP', user).replace('$SRCDIR', pwd).replace('$MOD', 'vedavaapi')
    targetfile = Config.wsgi_apache_config_file
    try:
        with open(targetfile, "w") as newf:
            newf.write(content)
    except Exception as e:
        print ("Could not write " + targetfile + ": ", e)
        sys.exit(1)

'''

'''


