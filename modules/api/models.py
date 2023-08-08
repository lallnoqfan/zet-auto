from io import BytesIO
from typing import List, Tuple

from PIL import Image
from pydantic import BaseModel


class ImageFile(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    name:      str = 'image.png'
    extension: str = 'png'
    image:     Image.Image

    def to_field(self) -> Tuple[str, Tuple[str, BytesIO, str]]:
        byte_io = BytesIO()
        self.image.save(byte_io, self.extension)
        byte_io.seek(0)
        return 'file[]', (self.name, byte_io, f'image/{self.extension}')


class Post(BaseModel):
    num:      int
    number:   int
    comment:  str
    datetime: str
    sage:     bool


class DvachThread(BaseModel):
    posts:   List[Post] = []
