from .provider import Provider
from .provider_exceptions import *
from .manga_metadata import MangaMetadata

import requests
from requests import Response
from PIL import Image
from io import BytesIO

class MangaUpdates(Provider):
    """Provider class implementation for MangaDex website.
    LINK: https://www.mangaupdates.com/
    """

    PROVIDER_NAME = "MangaUpdates"
    BASE_URL = "https://api.mangaupdates.com"

    def __init__(self, id_token:str) -> None:
        """Initializing object for one manga.
        This is recommended for retrieving full metadata.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.
        """
        self.id_token = id_token

    def get_metadata(self) -> MangaMetadata:
        manga_info = MangaUpdates.__get_manga_info(self.id_token)

        cover_art = MangaUpdates.__get_cover_from_url(
            manga_info["image"]["url"]["original"]
        )

        return MangaMetadata(
            provider=MangaUpdates.PROVIDER_NAME,
            id_token=self.id_token,
            titles=MangaUpdates.__extract_titles_from_response(manga_info),
            tags=MangaUpdates.__extract_tags_from_response(manga_info),
            genres=MangaUpdates.__extract_genres_from_response(manga_info),
            summary=MangaUpdates.__extract_summary_from_response(manga_info),
            cover_art=cover_art
        )

    @staticmethod
    def search_manga(name: str, page_limit:int = 1, per_page_limit:int = 10) -> list[str]:
        """Query the site and get matched mangas identification token.

        Args:
            name (str): Name of manga to be queried.
            page_limit (int, optional): Limit pages returned by MangaUpdates. Defaults to 1.
            per_page_limit (int, optional): Limit mangas per page returned by MangaUpdates. Defaults to 10.

        Returns:
            list[str]: list of identification tokens.
        """
        try:
            api_response:Response = requests.post(
                f"{MangaUpdates.BASE_URL}/v1/series/search",
                json={
                    "search": name,
                    "page": page_limit,
                    "perpage": per_page_limit
                }
            )

        except Exception as e:
            raise ProviderExceptions(e, MangaUpdates.PROVIDER_NAME)
        
        if(api_response.status_code != 200):
            #Failed API request.
            raise ProviderExceptions(f"API response for 'search_manga' was ({api_response.status_code}).", MangaUpdates.PROVIDER_NAME)
        

        return [manga["record"]["series_id"] for manga in api_response.json()["results"]]
        
    @staticmethod
    def get_titles(id_token: str) -> list[dict]:
        manga_info = MangaUpdates.__get_manga_info(id_token)
        
        return MangaUpdates.__extract_titles_from_response(manga_info)
        
    @staticmethod
    def get_tags(id_token: str) -> list[str]:
        manga_info = MangaUpdates.__get_manga_info(id_token)
        
        return MangaUpdates.__extract_tags_from_response(manga_info)
    
    @staticmethod
    def get_genres(id_token: str) -> list[str]:
        manga_info = MangaUpdates.__get_manga_info(id_token)
        
        return MangaUpdates.__extract_genres_from_response(manga_info)

    @staticmethod
    def get_summary(id_token: str) -> str:
        manga_info = MangaUpdates.__get_manga_info(id_token)
        
        return MangaUpdates.__extract_summary_from_response(manga_info)

    @staticmethod
    def get_cover(id_token: str) -> Image.Image:

        manga_info = MangaUpdates.__get_manga_info(id_token)

        image_url = manga_info["image"]["url"]["original"]

        return MangaUpdates.__get_cover_from_url(image_url)
    
    @staticmethod
    def __get_manga_info(id_token) -> dict:
        api_response:Response = requests.get(
            f"{MangaUpdates.BASE_URL}/v1/series/{id_token}"
        )

        if(api_response.status_code != 200):
            raise MangaNotFoundError(f"API response for '__get_manga_info' was ({api_response.status_code}).", MangaUpdates.PROVIDER_NAME)

        return api_response.json()
    
    @staticmethod
    def __extract_titles_from_response(response:dict) -> list[dict]:
        titles_dict = {}

        try:
            titles_dict["main"] = response["title"]

            titles_dict["alt_titles"] = []
            for title in response["associated"]:
                titles_dict["alt_titles"].append(title)

            return titles_dict
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract titles from response. ({e})", MangaUpdates.PROVIDER_NAME)
        
    @staticmethod
    def __extract_tags_from_response(response:dict) -> list[str]:
        """Extract tags that are considered "categories" in mangaUpdates.
        """
        tags_list = []

        try:
            tags_dict = response["categories"]

            for tag in tags_dict:
                tags_list.append(tag["category"])

            return tags_list
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract tags from response. ({e})", MangaUpdates.PROVIDER_NAME)
        
    @staticmethod
    def __extract_genres_from_response(response:dict) -> list[str]:
        """Extract tags that are considered "genre" in mangaUpdates.
        """
        tags_list = []

        try:
            tags_dict = response["genres"]

            for tag in tags_dict:
                tags_list.append(tag["genre"])

            return tags_list
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract tags from response. ({e})", MangaUpdates.PROVIDER_NAME)
        
    @staticmethod
    def __extract_summary_from_response(response:dict) -> str:
        try:

            return response["description"]
        
        except Exception as e:
            raise ProviderExceptions(f"Could not extract summary from response. ({e})", MangaUpdates.PROVIDER_NAME)
        
    @staticmethod
    def __get_cover_from_url(url:str) -> Image.Image:
        api_response = requests.get(url)

        if(api_response.status_code != 200):
            raise ProviderExceptions(f"Invalid cover URL. {url}")

        return Image.open(BytesIO(api_response.content)).convert("RGB")
        
        

