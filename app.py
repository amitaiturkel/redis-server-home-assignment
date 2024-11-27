from flask import Flask
from flask_restx import Api
from routes.health_routes import health_ns  # Import namespaces directly
from routes.echo_routes import echo_ns
from scheduler import start_scheduler

# Initialize Flask app
app = Flask(__name__)
@app.route('/')
def index():
    return "Server is running!" 


# Initialize Flask-RESTx API with Swagger UI configuration
api = Api(app, title="Custom title", version="2.5.0", description="Here's a longer description of the custom **OpenAPI** schema",doc="/docs")

# Register namespaces with the API
api.add_namespace(echo_ns, path='/echoAtTime')
api.add_namespace(health_ns, path='/health')


if __name__ == '__main__':
    
    start_scheduler()
    app.run(port=3000)
