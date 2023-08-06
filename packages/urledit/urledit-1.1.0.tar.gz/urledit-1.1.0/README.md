urledit
=======
Url parsing and editing as an object or in a functional style.

    >>> from urledit import urledit
    >>> url = 'forum/showthread.php?s=12345&p=728386#post728386'

Functional style
----------------
    >>> urledit(url)(scheme='http')(netloc='host.com')(fragment=''
    ... ).param(s=None).param(a=1).param(b=['x', 'y', 'z']).join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'

or

    >>> urledit(url, scheme='http', netloc='host.com', fragment=''
    ... ).param(('s', None), ('a', 1), b=['x', 'y', 'z']).join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'

Object style
------------
    >>> u = urledit(url)
    >>> u.scheme, u.netloc, u.path, u.qs, u.fragment
    ('', '', 'forum/showthread.php', 's=12345&p=728386', 'post728386')

    >>> u.scheme, u.netloc, u.fragment = 'http', 'host.com', ''
    >>> u.join()
    'http://host.com/forum/showthread.php?s=12345&p=728386'

Working with query string:

    >>> u.query == {'p': '728386', 's': '12345'}
    True

    >>> del u.query['s']
    >>> u.join()
    'http://host.com/forum/showthread.php?p=728386'

    >>> u.query['a'] = 1
    >>> u.query['b'] = ['x', 'y', 'z']
    >>> u.join()
    'http://host.com/forum/showthread.php?p=728386&a=1&b=x&b=y&b=z'