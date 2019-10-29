import click
from mephisto.cli.server import app
from click_default_group import DefaultGroup

@click.group(cls=DefaultGroup, default='web', default_if_no_args=True)
def cli():
	pass

@cli.command('web')
def web():
	"""Launch a local webserver with the Mephisto UI"""
	app.run(debug=False)

if __name__ == '__main__':
	cli()
	
