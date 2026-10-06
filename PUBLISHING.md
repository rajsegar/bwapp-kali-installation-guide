# GitHub Publication Instructions

The public repository is **rajsegar/bwapp-kali-installation-guide**:

https://github.com/rajsegar/bwapp-kali-installation-guide

The instructions below explain how to upload a copy to another empty repository or publish the accompanying Medium draft. Change the owner and repository name if you use your own destination.

Suggested description: “Installing bWAPP on Kali with Docker, fixing Debian Bullseye security package 404s, and reusable PDF lab notes.”

## Upload through GitHub

1. Create an empty repository named bwapp-kali-installation-guide under your account.
2. Choose the visibility you want. Do not initialise a separate README if uploading this package.
3. Extract the ZIP. In GitHub, choose Add file → Upload files and upload the contents of the extracted folder, keeping docs/ and scripts/.
4. Use the commit message: “Add bWAPP Kali installation guide and archive fix”.

## Push from Kali instead

After creating the empty repository, extract the ZIP and enter its bwapp-kali-installation-guide folder. The following commands assume the connected rajsegar account and the repository name above:

```bash
git init -b main
git add .
git commit -m "Add bWAPP Kali installation guide and archive fix"
git remote add origin https://github.com/rajsegar/bwapp-kali-installation-guide.git
git push -u origin main
```

If Git asks for an author identity, configure your preferred Git name and email before committing. Authenticate through GitHub's supported login method; do not put account tokens into documentation or remote URLs. The remote URL above points to the published guide. For a new copy, use the URL of the empty repository you created.

## Medium publication

Use docs/medium-article.md or the editable Medium article document. Paste the title, subtitle, and article into a new Medium story. Convert each command block to a code block, check links and formatting, and add the suggested tags. The delivered article is a draft; it has not been published to Medium.
