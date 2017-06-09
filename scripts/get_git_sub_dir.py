#https://github.com/mfbx9da4/git-sub-dir/blob/master/get_git_sub_dir.py
'''download a github repo subfolder
Usage:
    python get_git_sub_dir.py path/to/sub/dir
'''
import base64
import json
from urllib.request import urlopen
from urllib.request import Request
import os
import argparse


GITHUB_REPOS_API_BASE_URL = 'https://api.github.com/repos/'
#https://api.github.com/repos/opencv/opencv/contents/samples/python
USERNAME = ""
PASSWORD = ""


def read_url(url, private_=False):
    '''func'''
    if private_:
        request = Request(url)
        base64string = base64.encodestring(
            '%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        html = urlopen(request).read()
    else:
        html = urlopen(url).read()
    return html.decode('utf-8')


def write_file(item, dir_name, private_=False):
    '''func'''
    name = item['name']
    res = read_url(item['download_url'], private_)
    print(os.path.join(dir_name, name))
    with open(os.path.join(dir_name, name), 'w') as f:
        f.write(res)


def write_files(url, dir_name, recurse=True, private=False):
    '''func'''
    print('url', url)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    github_dir = json.loads(read_url(url, private))
    for item in github_dir:
        if item['type'] == 'file':
            write_file(item, dir_name, private)
        elif item['type'] == 'dir' and recurse:
            write_files(item['url'], dir_name=os.path.join(
                dir_name, item['name']))


if __name__ == '__main__':

    cmdline = argparse.ArgumentParser(
        description='Checkout a subfolder from a git repo.\n' \
        'Example:\n' \
        'get_git_sub_dir.py c:\development\python\cv2samples -i -r -own opencv -repo opencv -subfolder samples/python'
        )
    # position argument
    cmdline.add_argument('path', help='path to download to')
    cmdline.add_argument('-r', '--recurse', help='Recurse through subfolders', action='store_true')
    cmdline.add_argument('-p', '--private', help='Checkout private repo', action='store_true')
    cmdline.add_argument('-i', '--ignore', help='Ignore if current dir exists', action='store_true')
    cmdline.add_argument('-own' '--own', help='Owner name, eg opencv')
    cmdline.add_argument('-repo', help='Repo name, eg opencv')
    cmdline.add_argument('-subfolder', '--subfolder', help='web subfolder of the repo, eg samples/python')
    args = cmdline.parse_args()

    target_path = os.path.normpath(args.path)
    if os.path.exists(target_path) and not args.ignore:
        raise FileExistsError('Directory %s already exists' % target_path)

    #https://api.github.com/repos/opencv/opencv/contents/samples/python
    rel_path = args.subfolder.lstrip('/').rstrip('/')
    repo_path = '{0}{1}/{2}/contents/{3}'.format(GITHUB_REPOS_API_BASE_URL, args.own__own, args.repo, args.subfolder) #no ficken idea why this is own__own

    if args.private:
        USERNAME = input("username: ")
        PASSWORD = input("password: ")

    write_files(repo_path, target_path, recurse=args.recurse, private=args.private)

    print('Downloaded to %s' % target_path)
