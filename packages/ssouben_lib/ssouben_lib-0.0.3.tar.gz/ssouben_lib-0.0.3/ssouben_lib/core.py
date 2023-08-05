#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
    Implementation de hello world
 
    Usage:
 
    >>> from ssouben_lib import proclamer
    >>> proclamer()
"""

from datetime import datetime
 

__all__ = ['proclamer']

def proclamer():
    
    """
        Fonction privet
    """
    print "[%s] Privet, kak dela ?" % datetime.now()
 
 
if __name__ == "__main__":
    proclamer()