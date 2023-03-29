from .provider import Provider
from .provider_exceptions import *
from .manga_metadata import MangaMetadata

import requests
from requests import Response
from PIL import Image
from io import BytesIO

class MangaDex(Provider):
    """Provider class implementation for MangaDex website.
    LINK: https://mangadex.org/
    """

    PROVIDER_NAME = "MangaDex"
    BASE_URL = "https://api.mangadex.org"

    def __init__(self, id_token:str) -> None:
        """Initializing object for one manga.
        This is recommended for retrieving full metadata.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.
        """
        self.id_token = id_token

    def get_metadata(self) -> MangaMetadata:
        manga_info = MangaDex.__get_manga_info(self.id_token)

        filename = MangaDex.__extract_filename_from_response(manga_info)

        api_response = requests.get(
            f"https://uploads.mangadex.org/covers/{self.id_token}/{filename}"
        )

        cover_art = Image.open(BytesIO(api_response.content)).convert("RGB")

        return MangaMetadata(
            provider=MangaDex.PROVIDER_NAME,
            id_token=self.id_token,
            titles=MangaDex.__extract_titles_from_response(manga_info),
            tags=MangaDex.__extract_tags_from_response(manga_info),
            genres=MangaDex.__extract_genres_from_response(manga_info),
            summary=MangaDex.__extract_summary_from_response(manga_info),
            cover_art=cover_art
        )

    @staticmethod
    def search_manga(name: str) -> list[str]:
        try:
            api_response:Response = requests.get(
                f"{MangaDex.BASE_URL}/manga",
                params={"title": name,
                        "order[relevance]":"desc"
                    }
            )

        except Exception as e:
            raise ProviderExceptions(e, MangaDex.PROVIDER_NAME)
        
        if(api_response.status_code != 200):
            #Failed API request.
            raise ProviderExceptions(f"API response for 'search_manga' was ({api_response.status_code}).", MangaDex.PROVIDER_NAME)
        

        return [manga["id"] for manga in api_response.json()["data"]]
        
    @staticmethod
    def get_titles(id_token: str) -> list[dict]:
        manga_info = MangaDex.__get_manga_info(id_token)
        
        return MangaDex.__extract_titles_from_response(manga_info)
        
    @staticmethod
    def get_tags(id_token: str) -> list[str]:
        manga_info = MangaDex.__get_manga_info(id_token)
        
        return MangaDex.__extract_tags_from_response(manga_info)
    
    @staticmethod
    def get_genres(id_token: str) -> list[str]:
        manga_info = MangaDex.__get_manga_info(id_token)
        
        return MangaDex.__extract_genres_from_response(manga_info)

    @staticmethod
    def get_summary(id_token: str) -> str:
        manga_info = MangaDex.__get_manga_info(id_token)
        
        return MangaDex.__extract_summary_from_response(manga_info)

    @staticmethod
    def get_cover(id_token: str) -> Image.Image:

        manga_info = MangaDex.__get_manga_info(id_token)

        filename = MangaDex.__extract_filename_from_response(manga_info)

        api_response = requests.get(
            f"https://uploads.mangadex.org/covers/{id_token}/{filename}"
        )

        if(api_response.status_code != 200):
            raise ProviderExceptions("Invalid cover URL. {https://uploads.mangadex.org/covers/{id_token}/{filename}")

        return Image.open(BytesIO(api_response.content)).convert("RGB")
    
    @staticmethod
    def __get_manga_info(id_token) -> dict:
        api_response:Response = requests.get(
            f"{MangaDex.BASE_URL}/manga/{id_token}?includes[]=cover_art"
        )

        if(api_response.status_code != 200):
            raise MangaNotFoundError(f"API response for '__get_manga_info' was ({api_response.status_code}).", MangaDex.PROVIDER_NAME)

        return api_response.json()
    
    @staticmethod
    def __extract_titles_from_response(response:dict) -> list[dict]:
        titles_dict = {}

        try:
            titles_dict["main"] = response["data"]["attributes"]["title"]["en"]

            titles_dict["alt_titles"] = []
            for title in response["data"]["attributes"]["altTitles"]:
                titles_dict["alt_titles"].append(title)

            return titles_dict
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract titles from response. ({e})", MangaDex.PROVIDER_NAME)
        
    @staticmethod
    def __extract_tags_from_response(response:dict) -> list[str]:
        """Extract tags that are considered "format" and "theme" in mangaDex.
        """
        tags_list = []

        try:
            tags_dict = response["data"]["attributes"]["tags"]

            for tag in tags_dict:
                if(tag["attributes"]["group"] == "format" or tag["attributes"]["group"] == "theme"):
                    tags_list.append(tag["attributes"]["name"]["en"])

            return tags_list
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract tags from response. ({e})", MangaDex.PROVIDER_NAME)
        
    @staticmethod
    def __extract_genres_from_response(response:dict) -> list[str]:
        """Extract tags that are considered "genre" in mangaDex.
        """
        tags_list = []

        try:
            tags_dict = response["data"]["attributes"]["tags"]

            for tag in tags_dict:
                if(tag["attributes"]["group"] == "genre"):
                    tags_list.append(tag["attributes"]["name"]["en"])

            return tags_list
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract tags from response. ({e})", MangaDex.PROVIDER_NAME)
        
    @staticmethod
    def __extract_summary_from_response(response:dict) -> str:
        try:

            return response["data"]["attributes"]["description"]["en"]
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract summary from response. ({e})", MangaDex.PROVIDER_NAME)
        
    @staticmethod
    def __extract_filename_from_response(response:dict) -> str:
        filename = None
        try:
            for relationship in response["data"]["relationships"]:
                if(relationship["type"] == "cover_art"):
                    filename = relationship["attributes"]["fileName"]
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract cover filename from response. ({e})", MangaDex.PROVIDER_NAME)
        
        if(not filename):
            #There is no cover art
            raise ProviderExceptions(f"Could not extract cover filename from response. Maybe no cover art?", MangaDex.PROVIDER_NAME)
        
        return filename
        
        

