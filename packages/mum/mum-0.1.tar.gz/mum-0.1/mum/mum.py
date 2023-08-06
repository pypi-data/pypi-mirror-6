import click
from internet import getMessage, postMessage

def ask(msg):
	answer = raw_input(msg + " (y/n) ")
	return answer == 'y'

@click.group()
def cli():
	pass

@cli.command()
#@click.option('--verbose')
@click.argument('message')
def say(message):
	try:
		postMessage(message)
	except Exception:
		if(ask("Message failed to submit, try again?")):
			postMessage(message)

@cli.command()
def hear():
	try:
		message = getMessage()
		print(message)
	except Exception:
		pass

if __name__ == '__main__':
	cli()

