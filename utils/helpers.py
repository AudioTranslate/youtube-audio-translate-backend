
def get_attribute_dict(attrib: str):
    return {
            key.replace('xml:', '').strip(): value.strip(' "')
            for key, value in [
                prop.split("=")
                for prop in attrib.strip().split(" ")
                if prop != ""
            ]
        }

def format_vtt_timestamp_to_ms(timestamp:str) -> int:
    h, m = tuple(map(int, timestamp.split(':')[:2]))
    s, ms = tuple(map(int, timestamp.split(':')[-1].split('.')))
    h *= 3600000
    m *= 60000
    s *= 1000
    return h + m + s + ms
    