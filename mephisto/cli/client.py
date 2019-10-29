import click
from server import app

@click.command()
def web():
	app.run(debug=False)

if __name__ == '__main__':
	web()
	
