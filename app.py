import os
import random
import string
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Folders configuration
UPLOAD_FOLDER = 'uploads'
TEMPLATE_FOLDER = 'templates'  # generated video pages will be saved here
VIDEOS_HTML_PATH = os.path.join(TEMPLATE_FOLDER, 'videos.html')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB limit

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve uploaded video files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Upload video route with error handling for duplicate filenames
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
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            
            # Check if a file with the same name already exists.
            # If so, rename the file by appending a random 6-character string.
            if os.path.exists(video_path):
                base, ext = os.path.splitext(original_filename)
                random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                video_filename = f"{base}_{random_suffix}{ext}"
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            else:
                video_filename = original_filename

            # Save video file
            video_file.save(video_path)

            # Generate a random string for the HTML filename (8 characters)
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            html_filename = f"Mt-{random_string}.html"

            # Get current timestamp for display (if needed)
            video_creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Generate URL for the uploaded video file using our route
            video_url = url_for('uploaded_file', filename=video_filename)

            # Generate HTML content for the video page (without the comment section)
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
    app.run(debug=True)
    