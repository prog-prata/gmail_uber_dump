import json

EMPTY_JSON = []

def open_file(filename) -> dict:
    """Connects to the database, returns dict data"""
    try:
        with open(filename, "r") as data_file:
            return json.loads(data_file.read())
    except (json.JSONDecodeError, FileNotFoundError):
        return EMPTY_JSON
    
def read_uber_mail(filename):
    db = open_file(filename)
    return_data = []
    for data in db:
        return_data.append(
            {
                "id": data["id"],
                "email": data["email"],
                "total": data["total"],
                "distance": data["distance"],
                **data,
            }
        )
    return return_data

def read_credentials(filename):
    data = open_file(filename)
    return { data["user"], data["password"]}

def append(actualdata, toappend):
    for data in actualdata:
        if data["id"] == toappend["id"]:
            return False
    actualdata.append(toappend)
    return actualdata

def save_file(filename, data):
    with open(filename, "w") as database_file:
        database_file.write(json.dumps(data, indent=4))