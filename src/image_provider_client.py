import requests
from consts import IMAGE_HOST, IMAGE_PORT, IMAGE_SERVER_TIMEOUT
from typing import Optional
import logging

class ImageProvider:
    """
    Image provider class.
    """
    def __init__(self, host: str = IMAGE_HOST, port: str = IMAGE_PORT) -> None:
        """
        Initialization of image provider class.

        Parameters
        ----------
        host : str
            Image provider host.
        port : int
            Image provider port.
        """
        self.host = host
        self.port = port


    def get_image(image_id: str) -> Optional[bytes]:
        """
        Get image by its id.

        Parameters
        ----------
        image_id : str
            Image id.

        Returns
        -------
        bytes
            Image or None.
        """
        try:
            path = f'http://{IMAGE_HOST}:{IMAGE_PORT}/images/{str(image_id)}'
            image = requests.get(path, timeout=IMAGE_SERVER_TIMEOUT)

            if image.status_code != 200:
                return {
                    'error': f'Some problems with your image_id: {image_id}',
                    'status_code': image.status_code
                }

            image = image.content
        except requests.exceptions.ConnectionError:
            return  {
                'error': 'Problems with images server',
                'status_code': 500
            }
        
        return image
