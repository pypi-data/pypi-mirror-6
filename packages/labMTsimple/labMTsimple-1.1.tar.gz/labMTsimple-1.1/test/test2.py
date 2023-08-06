import os
# print __file__
# print os.path.dirname(__file__)
# print os.path.abspath(__file__)
# print os.path.realpath(__file__)
relpath = os.path.abspath(__file__).split('/')[1:-1]
relpath.append('data')
relpath.append('labMT1.txt')
fileName = ''
for pathp in relpath:
  fileName += '/' + pathp
print fileName

