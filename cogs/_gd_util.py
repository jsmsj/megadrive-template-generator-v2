import requests
from requests.structures import CaseInsensitiveDict


class GD:
    def __init__(self,link) -> None:
        self.link = link
    
    def get_general_details(self):
        url = "http://gdrivesize.jsmsj.repl.co/checksize"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        data = "{" + '"link"' + ":" + f'"{self.link}"' + "}"
        try:
            resp = requests.post(url, headers=headers, data=data)
            return resp.json()
        except Exception as e:
            raise ValueError(f"Unable to get size, error: {e}")

