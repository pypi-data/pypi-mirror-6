import getpass
import sys

def report_install(m):
    import json
    import platform
    data = {'hostname': platform.node(),
            'platform': platform.platform(),
            'processor': platform.processor(),
            'language': 'python',
            'language_extras': json.dumps({
                'version': platform.python_version(),
                'implementation': platform.python_implementation(),
                'architecture': platform.machine(),
                'pyexe_build': platform.architecture()[0],
                }),
            }
    m._ask(m._ASK_POST,
           '/report/install/',
           data=data)

def main():
    
    print 'Welcome to Multyvac.\n'
    print ('If you input your Multyvac username and password, an api key will '
           'be automatically fetched for this machine.') 
    
    username = raw_input('Username: ')
    password = getpass.getpass('Password: ')
    
    from .multyvac import Multyvac, RequestError
    m = Multyvac()
    try:
        api_keys = m.api_key.list(username=username, password=password)
    except RequestError as e:
        print >> sys.stderr, ('Bad username and password. '
                              'Please run setup again.')
        sys.exit(1)
    except Exception as e:
        print >> sys.stderr, 'Unknown error: ', e
        sys.exit(1)
    
    for api_key in api_keys:
        if api_key.active:
            print 'Your machine will use api key %s' % api_key.id
            m.config.set_key(api_key.id,
                             api_key.secret_key)
            m.config.save_to_disk()
            print 'Success'
            try: report_install(m)
            except: pass
            sys.exit(0)
    else:
        print >> sys.stderr, 'Your account has no active api keys.'
        sys.exit(1)

    

if __name__ == '__main__':
    main()
