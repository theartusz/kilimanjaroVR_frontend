# Deploy new version
1. Navigate to `app` folder
2. Run `flyctl deploy` 


# Local development
1. navigate to app directory
2. execute `flask --app app --debug run`

# Config
Password and username to Mongodb are stored in flyio secrets `flyctl secrets set <your-secret>`