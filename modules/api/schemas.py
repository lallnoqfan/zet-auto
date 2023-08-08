from typing import List, Dict

from pydantic import BaseModel
from requests_toolbelt import MultipartEncoder

from .models import ImageFile


class DvachPostingSchemaIn(BaseModel):
    task:         str = 'post'
    board:        str
    thread:       str | int = ''
    usercode:     str = ''
    code:         str = ''
    captcha_type: str = '2chcaptcha'
    email:        str = ''
    submit:       str = 'Ответ'
    name:         str = ''
    comment:      str = ''
    oekaki_image:    str = ''
    oekaki_metadata: str = ''
    makaka_id:       str = ''
    makaka_answer:   str = ''
    files: List[ImageFile] = []

    def to_dict(self) -> Dict:
        data = self.dict()  # TODO: remove deprecated method usage
        return data

    def to_data(self) -> MultipartEncoder:
        data = self.to_dict()
        del data['files']

        data = [(key, data[key]) for key in data]
        if self.files:
            data += [file.to_field() for file in self.files]

        return MultipartEncoder(fields=data)
