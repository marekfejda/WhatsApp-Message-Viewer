import re
from datetime import datetime
import soundfile as sf

log_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.+?): (.+)")
html_output = """<!DOCTYPE html>
<html>
<head>
<title>Chat Log</title>
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
        margin: 0;
        padding: 20px;
        display: flex;
        justify-content: center;
        height: 100vh;
    }
    .container {
        width: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .message {
        background-color: #ffffff;
        border-radius: 10px;
        margin-bottom: 15px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        max-width: 60%;
        width: auto;
        min-width: 200px;
        display: flex;
        flex-direction: column;
    }
    .message .header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    .message .header .sender {
        font-weight: bold;
        color: #333333;
        min-width: 100px;
        max-width: 40%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .message .header .timestamp {
        color: #999999;
        font-size: 0.8em;
        flex: 1;
    }
    .message .content {
        color: #333333;
    }
    .sent {
        align-self: flex-end;
        background-color: #DCF8C6;
        text-align: right;
    }
    .received {
        align-self: flex-start;
        background-color: #E0E0E0;
    }
    .attachment-container {
        display: flex;
        justify-content: flex-end; /* Align attachments to the right by default */
        margin-bottom: 10px;
        background-color: transparent; 
    }

    .attachment-container.received {
        justify-content: flex-start; /* Align attachments to the left if received */
    }
    .attachment-preview {
        max-width: 20%;
        cursor: pointer;
    }
    .enlarged-media {
        max-width: 100%;
        max-height: 90vh;
        cursor: pointer;
    }
    .message .content {
        color: #333333;
        word-wrap: break-word;
    }
    .unsupported-file {
        background-color: #FFCDD2;
    }

</style>
<script>
    function toggleMediaSize(media) {
        if (media.classList.contains('enlarged-media')) {
            media.classList.remove('enlarged-media');
        } else {
            media.classList.add('enlarged-media');
        }
    }
</script>
</head>
<body>
<div class="container">
"""

main_user_names = ["Marek", "Your Nickname"]

def convert_opus_to_mp3(opus_file, mp3_file):
    data, samplerate = sf.read(opus_file)
    sf.write(mp3_file, data, samplerate, format='MP3')

def process_line(line):
    global html_output

    if "<attached:" in line:
        sender_start_index = line.find("]") + 2
        sender_end_index = line.find(":", line.find(":", line.find(":") + 1) + 1)
        sender = line[sender_start_index:sender_end_index].strip()

        attachment_class = "sent" if sender in main_user_names else "received"

        start_index = line.find("<attached: ") + len("<attached: ")
        end_index = line.find(">")
        file_name = line[start_index:end_index]
        file_extension = file_name.split('.')[-1].lower()

        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            html_output += f'<div class="attachment-container {attachment_class}"><img src="{file_name}" class="attachment-preview" onclick="toggleMediaSize(this)" alt="{file_name}"></div>'
        elif file_extension == 'mp4':
            html_output += f'<div class="attachment-container {attachment_class}"><video class="attachment-preview" onclick="toggleMediaSize(this)" controls><source src="{file_name}" type="video/mp4">Your browser does not support the video tag.</video></div>'
        elif file_extension == 'opus':
            mp3_file = f"{file_name.split('.')[0]}.mp3"
            convert_opus_to_mp3(file_name, mp3_file)
            html_output += f'<div class="attachment-container {attachment_class}"><audio controls><source src="{mp3_file}" type="audio/mpeg">Your browser does not support the audio tag.</audio></div>'
        else:
            html_output += f'<div class="message {attachment_class} unsupported-file">'
            html_output += f'<div class="header">'
            html_output += f'<div class="sender">{sender}</div>'
            html_output += f'</div>'
            html_output += f'<div class="content">Unsupported file type .{file_extension}: <a href="{file_name}" target="_blank">{file_name}</a></div>'
            html_output += f'</div>'
            print(f"Unsupported file type: {file_extension}. Message from: {sender}")
        return

    match = log_pattern.match(line)
    if match:
        date_str, time_str, sender, message = match.groups()
        timestamp = datetime.strptime(f"{date_str}, {time_str}", "%d/%m/%Y, %H:%M:%S")
        message_class = "sent" if sender in main_user_names else "received"

        message_with_links = re.sub(r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', message)

        html_output += f'<div class="message {message_class}">'
        html_output += f'<div class="header">'
        if message_class == "sent":
            html_output += f'<div class="timestamp">{timestamp.strftime("%d/%m/%Y, %H:%M:%S")}</div>'
            html_output += f'<div class="sender">{sender}</div>'
        else:
            html_output += f'<div class="sender">{sender}</div>'
            html_output += f'<div class="timestamp">{timestamp.strftime("%d/%m/%Y, %H:%M:%S")}</div>'
        html_output += f'</div>'
        html_output += f'<div class="content">{message_with_links}</div>'
        html_output += f'</div>'



with open("_chat.txt", 'r', encoding='utf-8') as file:
    for line in file:
        process_line(line)

html_output += "</div>\n</body>\n</html>"

html_file = "chat_log.html"
with open(html_file, 'w', encoding='utf-8') as file:
    file.write(html_output)

print(f"HTML chat log saved to {html_file}")
