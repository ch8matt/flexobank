import toml
import json

# Load the configuration file
config = toml.load("config.toml")

def get_tickers():
    with open(config["tickers_json_path"], 'r') as file:
        data = json.load(file)
        return data["tickers"]