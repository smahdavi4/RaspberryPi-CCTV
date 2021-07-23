import argparse
import os
from datetime import datetime

from flask import Flask, request, abort, make_response, jsonify

app = Flask(__name__)


def _save_image(image_file, date_obj: datetime):
    image_dir = os.path.join(app.config['save_dir'], date_obj.strftime('%Y-%m-%d'))
    os.makedirs(image_dir, exist_ok=True)
    image_name = "{date}.jpg".format(date=date_obj.strftime('%Y-%m-%d %H:%M:%S'))
    image_file.save(os.path.join(image_dir, image_name))


@app.route("/upload/<bot_token>", methods=["POST"])
def save_image(bot_token):
    if bot_token != app.config['bot_token']:
        abort(make_response(jsonify(message="Bot token invalid."), 401))
    if 'image' not in request.files:
        abort(make_response(jsonify(message="Image not set."), 400))
    if 'date' not in request.form:
        abort(make_response(jsonify(message="No date is specified for image."), 400))
    image = request.files['image']
    try:
        image_date = datetime.strptime(request.form['date'], '%d/%m/%Y %H:%M:%S')
    except ValueError as e:
        app.logger.exception(e)
        abort(make_response(jsonify(message="Invalid date format. The correct format is %d/%m/%Y %H:%M:%S"), 400))

    _save_image(image_file=image, date_obj=image_date)
    return make_response(jsonify(message="Ok."), 201)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parameters to be given to the server")
    parser.add_argument("--bot-token", type=str, required=True, help="Telegram Bot Token.")
    parser.add_argument("--save-dir", type=str, default="./images", help="Directory to save iamges")
    args = parser.parse_args()

    app.config['bot_token'] = args.bot_token
    app.config['save_dir'] = args.save_dir
    os.makedirs(args.save_dir, exist_ok=True)
    app.run(debug=False)
