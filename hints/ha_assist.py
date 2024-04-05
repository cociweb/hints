import json

def load_assist_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def split_aliases(aliases):
    return aliases.split("|") if aliases else []

def generate_entity_info(entities):
    entity_info_list = []
    for entity in entities:
        name = entity.get("name")
        alter_name = entity.get("alter_name")
        aliases = split_aliases(entity.get("aliases"))

        # Filter out null values
        combined_names = [name, alter_name] + [alias for alias in aliases if alias]
        entity_info_list.extend(combined_names)
    return entity_info_list

def generate_area_info(areas):
    area_info_list = []
    for area in areas:
        name =  area.get("name")
        aliases = split_aliases(area.get("aliases"))

        # Filter out null values
        combined_names = [name] + [alias for alias in aliases if alias]
        area_info_list.extend(combined_names)
    return area_info_list