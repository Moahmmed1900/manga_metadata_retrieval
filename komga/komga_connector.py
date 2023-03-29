import requests
from .config import KOMGA_CONFIG
from .komga_exceptions import *
from providers import MangaMetadata
from io import BytesIO

class KomgaConnector():
    KOMGA_BASE_URL = KOMGA_CONFIG["base_URL"]
    KOMGA_USER = KOMGA_CONFIG["user"]
    KOMGA_PASSWORD = KOMGA_CONFIG["password"]

    def __init__(self) -> None:
        self.current_session = requests.session()
        self.current_session.auth = (KomgaConnector.KOMGA_USER, KomgaConnector.KOMGA_PASSWORD)

        api_response = self.current_session.get(
            url=f"{KomgaConnector.KOMGA_BASE_URL}/api/v2/users/me"
        )

        if(api_response.status_code != 200):
            #Login failed; could not view API's user information.
            raise KomgaLoginFailed("Could not login, incorrect credentials.")
        
    def get_all_series(self, library_id:str, limit:int = 100) -> list[dict]:
        api_response = self.current_session.get(
            url=f"{KomgaConnector.KOMGA_BASE_URL}/api/v1/series",
            params={"library_id": library_id,
                    "size": limit}
        )

        validated_response = KomgaConnector.__validate_response(api_response)

        return validated_response.json()["content"]
    
    def get_all_libraries(self) -> list[dict]:
        api_response = self.current_session.get(
            url=f"{KomgaConnector.KOMGA_BASE_URL}/api/v1/libraries"
        )

        validated_response = KomgaConnector.__validate_response(api_response)

        return validated_response.json()
    
    def update_series_metadata(self, series_id:str, metadata: MangaMetadata, update_cover_art:bool = True) -> bool:
        """Patch the metadata of the series.
        """

        alt_title_komga_format_list = []

        for title in metadata.titles["alt_titles"]:
            key = list(title.keys())[0]
            value = title[key]
            alt_title_komga_format_list.append({
                "label": key,
                "title": value
            })

        patch_body = {
            "title": metadata.titles["main"],
            "summary": metadata.summary,
            "tags": metadata.tags,
            "genres": metadata.genres,
            "alternateTitles": alt_title_komga_format_list
        }

        api_response = self.current_session.patch(
            url=f"{KomgaConnector.KOMGA_BASE_URL}/api/v1/series/{series_id}/metadata",
            json=patch_body,
            
        )

        validated_response = KomgaConnector.__validate_response(api_response)

        if(update_cover_art):
            # Now updating the cover.
            ready_to_upload_image = KomgaConnector.__validate_cover(metadata)

            api_response = self.current_session.post(
                url=f"{KomgaConnector.KOMGA_BASE_URL}/api/v1/series/{series_id}/thumbnails",
                params={"selected": True},
                files={
                    "file": ready_to_upload_image.getvalue()
                }
            )

            validated_response = KomgaConnector.__validate_response(api_response)

        return True



    @staticmethod
    def __validate_response(response:requests.Response) -> requests.Response:
        if(response.status_code == 403):
            #Forbidden response from the API.
            raise KomgaForbidden(f"{response.json()['message']}, URL: {response.url}")
        
        if(response.status_code == 401):
            #Unauthorized response from the API.
            raise KomgaUnauthorized(f"{response.json()['message']}, URL: {response.url}")
        
        if(response.status_code == 400):
            #BadRequest response from the API.
            raise KomgaBadRequest(f"{response.json()['violations']}, URL: {response.url}")
        
        if(response.status_code == 200 or response.status_code == 204):
            return response
        
        raise KomgaExceptions(f"Invalid response from Komga. {response.status_code}, message: {response.json()}")
    
    @staticmethod
    def __validate_cover(metadata: MangaMetadata) -> BytesIO:
            img_file = BytesIO()

            #Checking file size, thumbnails must not exceed 1MB.
            metadata.cover_art.save(img_file, 'JPEG', optimize = True)

            if(img_file.tell() > 900000):
                #It exceed 1MB approx. . Hence, compress incrementally until it is less than 1 MB.
                for quality in reversed(range(100)):
                    img_file = BytesIO()
                    metadata.cover_art.save(img_file, 'JPEG', optimize = True, quality=quality)

                    if(img_file.tell() < 900000):
                        break
                
            return img_file
    
    def __del__(self):
        api_response = self.current_session.get(
            url=f"{KomgaConnector.KOMGA_BASE_URL}/api/v1/users/logout"
        )

        if(api_response.status_code != 204):
            #Login failed; could not view API's user information.
            raise KomgaLoginFailed("Could not logout from session.")
