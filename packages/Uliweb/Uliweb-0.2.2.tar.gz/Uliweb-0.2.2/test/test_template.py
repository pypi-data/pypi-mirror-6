from uliweb.core.template import *

def test_1():
    """
    >>> print template("Hello, {{=name}}", {'name':'uliweb'})
    Hello, uliweb
    >>> print template("Hello, {{ =name}}", {'name':'uliweb'})
    Hello, uliweb
    >>> print template("Hello, {{ = name}}", {'name':'uliweb'})
    Hello, uliweb
    >>> print template("Hello, {{=name}}", {'name':'<h1>Uliweb</h1>'})
    Hello, &lt;h1&gt;Uliweb&lt;/h1&gt;
    >>> print template("Hello, {{<<name}}", {'name':'<h1>Uliweb</h1>'})
    Hello, <h1>Uliweb</h1>
    >>> print template('''{{import datetime}}{{=datetime.date( # this breaks
    ...   2009,1,8)}}''')
    2009-01-08
    """

def test_comment():
    """
    >>> text = "{{## comment {{= var}} ##}}{{=name}}"
    >>> print template(text, {'name':'hello'})
    hello
    """
    
