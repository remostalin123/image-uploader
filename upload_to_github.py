import os
import requests
from bs4 import BeautifulSoup
from github import Github
from telegram import Bot

# Telegram Bot Configuration
BOT_TOKEN = "7995170313:AAEytWV78cOf3gXeA2D2OqY_bsnh94HWRNc"
CHANNEL_ID = "@7920709529"

# GitHub Configuration
GITHUB_TOKEN = "your_github_token"
GITHUB_REPO = "username/repository"  # Replace with your repo name

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN)

# Function to scrape the main page
def scrape_main_page():
    response = requests.get("https://www.idlebrain.com/")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find "Glam pix" links
    glam_links = []
    for a_tag in soup.find_all('a', string=lambda text: text and text.startswith("Glam pix:")):
        link = a_tag.get('href')
        if link:
            glam_links.append(link)
    
    return glam_links

# Function to download gallery images
def download_gallery_images(gallery_url):
    response = requests.get(gallery_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    image_links = []
    for page_link in soup.find_all('a', href=True):
        if "pages/image" in page_link['href']:
            image_links.append(gallery_url.rsplit('/', 1)[0] + '/' + page_link['href'])
    
    downloaded_files = []
    for img_url in image_links:
        img_name = img_url.split('/')[-1]
        img_data = requests.get(img_url)
        with open(img_name, 'wb') as f:
            f.write(img_data.content)
        downloaded_files.append(img_name)
    
    return downloaded_files

# Function to upload images to GitHub
def upload_to_github(file_paths):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    
    public_links = []
    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            content = f.read()
        repo.create_file(
            f"images/{os.path.basename(file_path)}", 
            f"Add {os.path.basename(file_path)}", 
            content, 
            branch="main"
        )
        public_links.append(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/images/{os.path.basename(file_path)}")
    
    return public_links

# Function to post links to Telegram
def post_to_telegram(message):
    bot.send_message(chat_id=CHANNEL_ID, text=message)

# Main Execution
if __name__ == "__main__":
    # Step 1: Scrape main page
    glam_links = scrape_main_page()
    
    # Step 2: Process galleries
    for gallery_link in glam_links:
        print(f"Processing: {gallery_link}")
        downloaded_files = download_gallery_images(gallery_link)
        
        # Step 3: Upload to GitHub
        cloud_links = upload_to_github(downloaded_files)
        
        # Step 4: Post to Telegram
        message = f"Gallery: {gallery_link}\n" + "\n".join(cloud_links)
        post_to_telegram(message)
        
        # Cleanup downloaded files
        for file in downloaded_files:
            os.remove(file)
