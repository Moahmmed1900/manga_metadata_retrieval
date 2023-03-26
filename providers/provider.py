import abc
from abc import ABC, abstractmethod
from PIL import Image



class Provider(ABC):
    """Abstract class for metadata providers.

    """
    @staticmethod
    @abstractmethod
    def search_manga(self, name:str) -> list[str]:
        """Query the site and get matched mangas identification token.

        Args:
            name (str): Name of manga to be queried.

        Returns:
            list[str]: list of identification tokens.
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_titles(self, id_token:str) -> list[dict]:
        """Get all titles of the specified manga.
        Where title["main"] is the main one and should always be available. Others are considered alt titles and optional.
        Alt titles are available in title["alt_titles"] as list of dicts as {"lable": "title"}.
        Raise ProviderExceptions.MangaNotFoundError if there is no matched manga or multiple mangas.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.

        Returns:
            list[str]: List of titles for the specified manga.
        """

        pass

    @staticmethod 
    @abstractmethod
    def get_tags(self, id_token:str) -> list[str]:
        """Get tags of the specified manga.
        Raise ProviderExceptions.MangaNotFoundError if there is no matched manga or multiple mangas.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.

        Returns:
            list[str]: List of tags for the specified manga.
        """

        pass

    @staticmethod 
    @abstractmethod
    def get_genres(self, id_token:str) -> list[str]:
        """Get genres of the specified manga.
        Raise ProviderExceptions.MangaNotFoundError if there is no matched manga or multiple mangas.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.

        Returns:
            list[str]: List of genres for the specified manga.
        """

        pass

    @staticmethod 
    @abstractmethod
    def get_summary(self, id_token:str) -> str:
        """Get the summary of the specified manga.
        Raise ProviderExceptions.MangaNotFoundError if there is no matched manga or multiple mangas.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.

        Returns:
            str: summary for the specified manga.
        """

        pass

    @staticmethod
    @abstractmethod
    def get_cover(self, id_token:str) -> Image.Image:
        """Get cover art of the specified manga.
        Raise ProviderExceptions.MangaNotFoundError if there is no matched manga or multiple mangas.

        Args:
            id_token (str): Used to uniquely identify the manga on the provider site.

        Returns:
            Image: Cover image for the specified manga.
        """

        pass