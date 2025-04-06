import os
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import boto3

app = Flask(__name__)

# Folders configuration for HTML templates
TEMPLATE_FOLDER = 'templates'  # generated video pages will be saved here
VIDEOS_HTML_PATH = os.path.join(TEMPLATE_FOLDER, 'videos.html')
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB limit

# S3 configuration - hardcoded credentials (for testing ONLY)
S3_BUCKET = "your-s3-bucket-name"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Upload video route using S3 for file storage
@app.route('/upload-video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        video_name = request.form['videoName']
        description = request.form.get('description', '')
        video_file = request.files['video']

        if video_file:
            original_filename = video_file.filename
            
            # Generate a unique filename to avoid conflicts in S3
            base, ext = os.path.splitext(original_filename)
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            video_filename = f"{base}_{random_suffix}{ext}"
            
            try:
                # Upload file object directly to S3
                s3.upload_fileobj(video_file, S3_BUCKET, video_filename)
            except Exception as e:
                print("Error uploading to S3:", e)
                return "Error uploading file", 500

            # Generate the S3 URL for the uploaded video
            video_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{video_filename}"

            # Get current timestamp for display if needed
            video_creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Generate HTML content for the video page
            html_filename = f"Mt-{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.html"
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>{video_name} - MyTube</title>
                <link href="{{{{ url_for('static', filename='style.css') }}}}" rel="stylesheet" type="text/css">
            </head>
            <body>
                <h1>MyTube</h1>
                <video src="{video_url}" controls></video>
                <h2>{video_name}</h2>
                <p>Uploader: {name}</p>
                <p>Description: {description}</p>
            </body>
            </html>
            """

            # Save the generated HTML file in the templates folder
            new_template_path = os.path.join(TEMPLATE_FOLDER, html_filename)
            with open(new_template_path, 'w', encoding='utf-8') as file:
                file.write(html_content)

            # Update videos.html by inserting a new anchor at the start of the "videos" div
            try:
                with open(VIDEOS_HTML_PATH, 'r', encoding='utf-8') as file:
                    videos_html = file.read()

                # Create a new anchor element for the uploaded video page
                new_anchor_html = f'<a href="/video/{html_filename}">{video_name}</a><br>\n'
                start_tag = '<div class="videos">'
                videos_html = videos_html.replace(start_tag, f'{start_tag}\n    {new_anchor_html}')

                with open(VIDEOS_HTML_PATH, 'w', encoding='utf-8') as file:
                    file.write(videos_html)
            except Exception as e:
                print("Error updating videos.html:", e)

            return redirect(url_for('videos'))

    return render_template('upload-video.html')

# Videos page (renders videos.html from the templates folder)
@app.route('/videos')
def videos():
    return render_template('videos.html')

# Route to render a generated video page from the templates folder
@app.route('/video/<filename>')
def video_page(filename):
    return render_template(filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/tos')
def tos():
    return render_template('tos.html')  # Ensure tos.html exists in the templates folder

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Default to 5001 if no port is specified
    app.run(host='0.0.0.0', port=port)
