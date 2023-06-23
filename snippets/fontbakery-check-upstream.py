"""Run Fontbakery on an upstream repo using the googlefonts profile.

In order to post an issue back to the upstream repo, you will need to add
a github access token.

Example:

python snippets/fontbakery-check-upstream.py \
    https://www.github.com/googlefonts/comfortaa /fonts/TTF \
    --post_issue --gh_token $MY_GH_TOKEN \
    --footnote "Please ignore checkXX"
"""
import requests
import argparse
import subprocess
import tempfile
import os
import json
import shutil
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_gh_url_to_api_url(url):
    return url.replace("https://github.com/", "https://api.github.com/repos/")


def download_file(url, dst_path):
    """Download a file from a url"""
    request = requests.get(url, stream=True)
    with open(dst_path, "wb") as downloaded_file:
        request.raw.decode_content = True
        shutil.copyfileobj(request.raw, downloaded_file)


def download_fonts(gh_url, dst):
    """Download fonts from a github dir"""
    font_paths = []
    r = requests.get(gh_url)
    for item in r.json():
        if item["name"].endswith(".ttf"):
            f = item["download_url"]
            dl_path = os.path.join(dst, os.path.basename(f))
            download_file(f, dl_path)
            font_paths.append(dl_path)
    return font_paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_url")
    parser.add_argument("font_dir", help="path to ttfs e.g /fonts/ttf")
    parser.add_argument(
        "--post_issue",
        action="store_true",
        default=False,
        help="Post FontBakery report to repo",
    )
    parser.add_argument("-gh", "--gh_token", help="Your github access token")
    parser.add_argument("-ft", "--footnote", help="text to include after report")
    args = parser.parse_args()

    tmp = tempfile.mkdtemp()
    gh_report = os.path.join(tmp, "report.md")

    logger.info("Downloading fonts from repo {}".format(args.repo_url))
    fonts_dir_url = args.repo_url + "/contents" + args.font_dir
    fonts_dir_url = convert_gh_url_to_api_url(fonts_dir_url)
    fonts = download_fonts(fonts_dir_url, tmp)

    logger.info("Running fonts through FontBakery")
    # Ignore check 28 since this is an upstream repo
    cmd = (
        ["fontbakery", "check-googlefonts"]
        + fonts
        + ["--ghmarkdown", gh_report]
        + ["-x", "com.google.fonts/check/has_license"]
        + ["-l", "FAIL"]
    )

    subprocess.call(cmd)

    if args.post_issue and args.gh_token:
        issue_url = convert_gh_url_to_api_url(args.repo_url)
        issue_url += "/issues"
        logger.info(f"Posting issue to {issue_url}")
        headers = {"Authorization": f"token {args.gh_token}"}
        body = open(gh_report, "r").read()
        if args.footnote:
            body += f"\n" f"\n" f"{args.footnote}"
        payload = {"title": "FontBakery Report", "body": body}
        r = requests.post(issue_url, json.dumps(payload), headers=headers)
        logger.info("Issue posted {}".format(r.json()["html_url"]))
    elif args.post_issue and not args.gh_token:
        logger.info("Failed to post issue!\n" "\n" "Include your Github api token.")

    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
