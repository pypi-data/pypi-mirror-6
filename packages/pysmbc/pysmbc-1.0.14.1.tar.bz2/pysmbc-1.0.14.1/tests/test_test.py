#!/usr/bin/env python

def setUp():
    print "setUp"
    pass

def tearDown():
    print "tearDown"
    pass

def test_003():
    print "003"
    pass

def test_002():
    print "002"
    pass

def test_001():
    print "001"
    pass

def test_compare():
    assert 1==0

if __name__ == '__main__':
    print "main"
    import nose
#    result = nose.run()
    result = nose.main(["./"])
