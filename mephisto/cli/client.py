import click
from mephisto.cli.server import app

@click.group()
def cli():
	pass

@cli.command()
def web():
	app.run(debug=False)

if __name__ == '__main__':
	web()
	
