import getpass
import sys

def main():
    
    print 'Welcome to Multyvac.\n'
    print ('If you input your username and password, an api key will be '
           'automatically fetched from Multyvac for this machine.') 
    
    username = raw_input('Username: ')
    password = getpass.getpass('Password: ')
    
    from .multyvac import Multyvac, MultyvacRequestError
    m = Multyvac()
    try:
        api_keys = m.api_key.list(username=username, password=password)
    except MultyvacRequestError as e:
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
            sys.exit(0)
    else:
        print >> sys.stderr, 'Your account has no active api keys.'
        sys.exit(1)

if __name__ == '__main__':
    main()
