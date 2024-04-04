import logging
from flask import Flask, request
from models.plate_reader import PlateReader, InvalidImage
from consts import LOGGING_FORMAT, LOGGING_LEVEL, APP_HOST, APP_PORT
from image_provider_client import ImageProvider
import logging
import io


app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')


@app.route('/read_plate_numbers', methods=['POST'])
def read_plate_numbers() -> dict | tuple:
    """
    Processes an arbitrary number of images.

    Returns
    -------
    list or tuple
        In successful case returns list of plate numbers, 
        otherwise tuple of error and its code.
    """
    if 'images' not in request.form:
        logging.error('No images in request')
        return {
            'error': 'Not found images for process',
            'status_code': 400
        }

    image_ids = request.form['images'].split(',')
    processed_images = []

    for image_id in image_ids:
        image_id = image_id.strip()

        if image_id == '':
            continue
        if not image_id.isdigit():
            logging.error(f'Incorrcet image id: {image_id}')
            return {
                'error': f'Image id must consist of numbers:{image_id}',
                'status_code': 400
            }

        payload = ImageProvider.get_image(image_id.strip())

        if isinstance(payload, dict):
            logging.error(payload['error'])
            return payload

        image = io.BytesIO(payload)

        try:
            res = plate_reader.read_text(image)
        except InvalidImage:
            logging.error('Problems with reading image')
            return {
                'error': f'Problems with reading image',
                'status_code': 400
            }
            # вот тут спорно, по сути к этому моменту уже всевозможные проверки пройдены,
            # возможно, тут уже стоит кидать 5xx code

        processed_images.append(res)

    return { 'plate_numbers': processed_images }


if __name__ == '__main__':
    logging.basicConfig(
        format=LOGGING_FORMAT,
        level=LOGGING_LEVEL,
    )

    app.json.ensure_ascii = False
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
