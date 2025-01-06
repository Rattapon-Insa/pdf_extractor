from app import create_app

# Create Flask app
app = create_app()

# Firebase Cloud Function entry point
def main(request):
    return app(request)
