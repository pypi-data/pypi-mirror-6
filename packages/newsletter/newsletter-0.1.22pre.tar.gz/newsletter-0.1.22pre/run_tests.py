#!/usr/bin/env python
##    newsletter - Python Newsletter Library
##    Copyright (C) 2009, 2010 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com
import sys, os, re, unittest
import newsletter.tests

main_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]

# Make sure we're in the correct directory
os.chdir( main_dir )

# Add the modules directory to the python path    

newsletter.tests.verbose = "--verbose" in sys.argv or "-v" in sys.argv
suite = newsletter.tests.main()


