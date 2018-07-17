from geopy.geocoders import Nominatim
import pyperclip

geolocator = Nominatim()

run = True
while run:
	data = input('Location: ')
	if data == "":
		run = False
	try:
		location = geolocator.geocode(data)
		locstr = "["+location.raw["lat"]+", "+location.raw["lon"]+"]"
	except:
		locstr = "Location not found"
	print(locstr)
	pyperclip.copy(locstr)
	print('   Data copied to clipboard.')