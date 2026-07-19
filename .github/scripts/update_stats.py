#!/usr/bin/env python3
import os
import json
from collections import defaultdict
from datetime import datetime
import re
import urllib.request
import urllib.error

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER = 'cranberrymuffin'
README_PATH = 'README.md'

FRAMEWORK_PATTERNS = {
    'React': ['react', 'next.js', 'next', 'jsx', 'tsx'],
    'Three.js': ['three.js', 'three', '3js'],
    'React Three Fiber': ['react-three-fiber', 'r3f'],
    'Node.js': ['node.js', 'nodejs', 'node', 'express'],
    'Django': ['django'],
    'Flask': ['flask'],
    'PeerJS': ['peerjs', 'peer.js', 'peer'],
}

# Languages to exclude from the reported top languages
EXCLUDE_LANGUAGES = {'HTML', 'CSS', 'Dockerfile'}

TOOL_BADGES = {
    'GitHub': 'GitHub-181717?style=flat&logo=github&logoColor=white',
    'VS Code': 'VS%20Code-007ACC?style=flat&logo=visualstudiocode&logoColor=white',
    'Git': 'Git-F05032?style=flat&logo=git&logoColor=white',
}

def make_api_request(endpoint):
    headers = {
        'Accept': 'application/vnd.github+json',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    req = urllib.request.Request(
        f'https://api.github.com{endpoint}',
        headers=headers
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code}")
        return None

def get_user_repos():
    repos = []
    page = 1
    while True:
        data = make_api_request(
            f'/users/{GITHUB_USER}/repos?per_page=100&page={page}&type=owner'
        )
        if not data or len(data) == 0:
            break
        repos.extend([r for r in data if not r['fork']])
        page += 1
    return repos

def get_repo_languages(owner, repo):
    data = make_api_request(f'/repos/{owner}/{repo}/languages')
    return data or {}

def analyze_repositories():
    repos = get_user_repos()
    language_count = defaultdict(int)
    
    for repo in repos:
        languages = get_repo_languages(GITHUB_USER, repo['name'])
        for lang in languages.keys():
            # Skip excluded languages (HTML/CSS)
            if lang in EXCLUDE_LANGUAGES:
                continue
            language_count[lang] += 1
    
    return language_count

def generate_stats_section():
    language_count = analyze_repositories()
    top_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    section = "## 📊 Languages & Tools\n\n"
    section += "### Top Languages\n"
    for lang, count in top_languages:
        lang_param = lang.lower().replace('#', 'sharp').replace('+', 'plus').replace(' ', '-')
        section += f"- **{lang}** - [View Repositories](https://github.com/{GITHUB_USER}?tab=repositories&language={lang_param}) | **{count} repo{'s' if count != 1 else ''}**\n"
    
    section += "\n### Frameworks & Libraries\n"
    badges = {
        'React': 'React-20232A?style=flat&logo=react&logoColor=61DAFB',
        'Three.js': 'Three.js-000000?style=flat&logo=three.js&logoColor=white',
        'React Three Fiber': 'React%20Three%20Fiber-000000?style=flat&logo=react&logoColor=61DAFB',
        'Node.js': 'Node.js-339933?style=flat&logo=nodedotjs&logoColor=white',
        'Django': 'Django-092E20?style=flat&logo=django&logoColor=white',
        'Flask': 'Flask-000000?style=flat&logo=flask&logoColor=white',
        'PeerJS': 'PeerJS-FF4081?style=flat',
    }
    
    for framework, badge_url in badges.items():
        section += f"![{framework}](https://img.shields.io/badge/{badge_url})\n"
    
    section += "\n### Mobile Development\n"
    section += "![iOS](https://img.shields.io/badge/iOS-000000?style=flat&logo=apple&logoColor=white)\n"
    section += "![Android](https://img.shields.io/badge/Android-3DDC84?style=flat&logo=android&logoColor=white)\n"
    
    section += "\n### Tools & Platforms\n"
    for tool, badge_url in TOOL_BADGES.items():
        section += f"![{tool}](https://img.shields.io/badge/{badge_url})\n"
    
    return section

def update_readme():
    if not os.path.exists(README_PATH):
        print(f"{README_PATH} not found!")
        return
    
    with open(README_PATH, 'r') as f:
        content = f.read()
    
    stats_section = generate_stats_section()
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    start_marker = '<!-- LANGUAGES_AND_TOOLS_START -->'
    end_marker = '<!-- LANGUAGES_AND_TOOLS_END -->'
    
    if start_marker not in content or end_marker not in content:
        print("Markers not found in README.md")
        return
    
    before = content[:content.index(start_marker) + len(start_marker)]
    after = content[content.index(end_marker):]
    
    # Replace the timestamp using regex
    after = re.sub(r'\*Last updated: \d{4}-\d{2}-\d{2}\*', f'*Last updated: {timestamp}*', after)
    
    new_content = f"{before}\n{stats_section}\n{after}"
    
    with open(README_PATH, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated README.md with fresh stats!")

if __name__ == '__main__':
    update_readme()
