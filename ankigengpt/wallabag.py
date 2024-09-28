from dataclasses import dataclass
from datetime import datetime
from typing import Generator

import requests

from ankigengpt.logging import logger


@dataclass
class WallabagTag:
    id: str
    label: str
    slug: str


@dataclass
class WallabagEntry:
    id: str
    title: str
    content: str
    url: str
    hashed_url: str
    annotations: list
    archived: bool
    tags: list[WallabagTag]


@dataclass
class WallabagAnnotation:
    id: str
    text: str
    quote: str
    ranges: list
    created_at: datetime


class WallabagConnector:
    def __init__(
        self, url: str, user: str, password: str, client_id: str, client_secret: str
    ):
        self.url = url
        self.user = user
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token: str = self._get_oauth_token()

    @property
    def _session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
        )
        return session

    def _get_oauth_token(self):
        logger.info("Getting wallabag oauth token")
        response = requests.post(
            self.url + "/oauth/v2/token",
            {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.user,
                "password": self.password,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    def get(self, endpoint: str, params: dict = {}) -> requests.Response:
        url = self.url + endpoint
        logger.debug(f'Getting "{url}" with params: {params}')
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response

    def get_entry(self, id: int) -> WallabagEntry:
        entry = self.get(f"/api/entries/{id}").json()
        return WallabagEntry(
            id=entry["id"],
            title=entry["title"],
            url=entry["url"],
            hashed_url=entry["hashed_url"],
            content=entry["content"],
            annotations=entry["annotations"],
            tags=[WallabagTag(**tag) for tag in entry["tags"]],
            archived=True if entry["is_archived"] == 1 else False,
        )

    def get_annotations(
        self, entry_id: str
    ) -> Generator[WallabagAnnotation, None, None]:
        data = self.get(f"/api/annotations/{entry_id}.json").json()
        for item in data["rows"]:
            yield WallabagAnnotation(
                id=item["id"],
                text=item["text"],
                quote=item["quote"],
                created_at=datetime.strptime(item["created_at"], "%y-%m-%dT%H:%M+%S"),
                ranges=item["ranges"],
            )
