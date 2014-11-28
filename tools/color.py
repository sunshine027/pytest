#!/usr/bin/env python

    
def inblack(s):
    return highlight('') + "%s[30;2m%s%s[0m"%(chr(27), s, chr(27)) 
    
def inred(s):
    return highlight('') + "%s[31;2m%s%s[0m"%(chr(27), s, chr(27))

def ingreen(s):
    return highlight('') + "%s[32;2m%s%s[0m"%(chr(27), s, chr(27)) 
    
def inyellow(s):
    return highlight('') + "%s[33;2m%s%s[0m"%(chr(27), s, chr(27)) 
    
def inblue(s):
    return highlight('') + "%s[34;2m%s%s[0m"%(chr(27), s, chr(27)) 
    
def inpurple(s):
    return highlight('') + "%s[35;2m%s%s[0m"%(chr(27), s, chr(27)) 
    
def inwhite(s):
    return highlight('') + "%s[37;2m%s%s[0m"%(chr(27), s, chr(27))
    
def highlight(s):
    return "%s[30;2m%s%s[1m"%(chr(27), s, chr(27))
    