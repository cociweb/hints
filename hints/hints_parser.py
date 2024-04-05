import os
import requests
import json
import logging


_LOGGER = logging.getLogger(__name__)

def fetch_data_from_api(api_url, token, data_dir):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(f"{api_url}/api/hints_parser", headers=headers)
        response_data = response.json()

        # Extract entity and area data
        entities = response_data.get("entity", [])
        areas = response_data.get("area", [])
        _LOGGER.info("Trying to fetch data from the endpoint REST Api!")

        # Save entity data to entities.txt
#        with open(os.path.join(data_dir, "entities.txt"), "w") as entities_file:
#            for entity in entities:
#                entities_file.write(json.dumps(entity) + "\n")

        # Save area data to areas.txt
#        with open(os.path.join(data_dir, "areas.txt"), "w") as areas_file:
#            for area in areas:
#                areas_file.write(json.dumps(area) + "\n")

        with open(os.path.join(data_dir, "entities.txt"), "w", encoding='utf-8') as json_file:
            json.dump(entities, json_file, ensure_ascii=False, indent=4)
            _LOGGER.debug("Entities data are fetched from the endpoint REST Api!")

        with open(os.path.join(data_dir, "areas.txt"), "w", encoding='utf-8') as json_file:
            json.dump(areas, json_file, ensure_ascii=False, indent=4)
            _LOGGER.debug("Areas data are fetched from the endpoint REST Api!")

        _LOGGER.info("Data saved successfully from the endpoint REST Api!")

    except Exception as e:
        _LOGGER.error(f"Error fetching endpoint REST Api data: {e}")