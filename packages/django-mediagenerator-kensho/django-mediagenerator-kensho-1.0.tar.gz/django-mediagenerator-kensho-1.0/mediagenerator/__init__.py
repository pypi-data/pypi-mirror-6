

def precompile_generate_media_for_dev_server():
    """Fakes a request to our root URL to get mediagenerator middleware awake.

    Hits '/' to make mediagenerator middleware refresh its dev list.
    """
    print "Generate media is running"
	print "Don't hold your breath or you may pass out"

    # Make a mock request and hit a known URL:

    from django.test import Client
    client = Client()
    client.get('/')
