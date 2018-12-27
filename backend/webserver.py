from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

import cgi

class webServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Enter the name of the restaurant</h2><input name="new" type="text" ><input type="submit" value="Add"> </form>'''
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

				if myRestaurantQuery:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += myRestaurantQuery.name
					output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'><h2>Are you sure you want to delete?</h2><input type="submit" value="Delete"> </form>''' % restaurantIDPath
					output += "</body></html>"
					self.wfile.write(output)								
					return	


			if self.path.endswith("/edit"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

				if myRestaurantQuery:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += myRestaurantQuery.name
					output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><h2>Enter the name of the restaurant</h2><input name="edit" type="text" ><input type="submit" value="update"> </form>''' % restaurantIDPath
					output += "</body></html>"
					self.wfile.write(output)								
					return	

			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output  = ""
				output += "<html><body>"
				output += "<a href = '/restaurants/new' > Add a new restaurant </a>"
				output += "</br></br>"
				output += "<h2> Restaurants </h2>"
				
				for restaurant in restaurants:
					output += restaurant.name
					output += "</br>"
					output += "<a href ='/restaurants/%s/edit' > Edit </a>" % restaurant.id
					output += "</br>"
					output += "<a href ='/restaurants/%s/delete'> Delete </a>" % restaurant.id
					output += "</br></br></br>"

				output += "</body></html>"
				self.wfile.write(output)
				# print output
				return
			
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)
	
	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('new')
					restaurant = Restaurant(name=messagecontent[0])
					session.add(restaurant)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
			
			if self.path.endswith("/edit"):
				restaurantIDPath = self.path.split("/")[2]
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('edit')
					myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

					if myRestaurantQuery != []:
						myRestaurantQuery.name = messagecontent[0]
						session.add(myRestaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

				myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery != []:
					session.delete(myRestaurantQuery)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webServerHandler)
		print "Web Server running on port %s"  % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()

if __name__ == '__main__':
	main()