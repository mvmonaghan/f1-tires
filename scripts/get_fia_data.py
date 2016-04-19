from bs4 import BeautifulSoup
from urllib import urlopen

r = urlopen('http://www.fia.com/events/fia-formula-one-world-championship/season-2015/event-timing-information-1')
soup = BeautifulSoup(r)

print soup.prettify()
