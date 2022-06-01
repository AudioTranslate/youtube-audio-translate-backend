

def get_attribute_dict(attrib: str):
    return {
            key.replace('xml:', '').strip(): value.strip(' "')
            for key, value in [
                prop.split("=")
                for prop in attrib.strip().split(" ")
                if prop != ""
            ]
        }
