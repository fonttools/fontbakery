#!/bin/sh
# Script is used to add or overwrite "secure" section in travis.yaml of your
# project. When using script you must be inside of project directory.
#
# Usage: fontbakery-travis-secure.sh -u githubusername -e your@email
#
while test $# -gt 0; do
    case $1 in
        -u | --user)
            shift
            if test $# -gt 0; then
                githubUserName=$1
            else
                echo "not github user specified"
                exit 1
            fi
            shift
            ;;
        -e | --email)
            shift
            if test $# -gt 0; then
                githubUserEmail=$1
            else
                echo "no email specified"
                exit 1
            fi
            shift
            ;;
        -t | --token)
            shift
            if test $# -gt 0; then
                token=$1
            else
                echo "no email specified"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z $githubUserName ]; then
    >&2 echo "$0: specify --user argument"
    exit 1
fi

if [ -z $githubUserEmail ]; then
    >&2 echo "$0: specify --email argument"
    exit 1
fi

if [ -z $token ]; then
    data=`curl -u $githubUserName -d '{"scopes":["public_repo"],"note":"CI: fontbakery-cli"}' -s "https://api.github.com/authorizations"`
    token=`python -c "import json,sys;print(json.loads('''${data}''')['token'])"`
    if [ $? -eq 0 ]; then
        travis login --github-token ${token}
        echo Copy this token for next using:
        echo
        echo "       ${token}"
        echo
    fi
fi

if [ $token ]; then
    echo travis encrypt GIT_NAME="${githubUserName}" GIT_EMAIL="${githubUserEmail}" GH_TOKEN="${token}" --add --no-interactive -x
    travis encrypt GIT_NAME="${githubUserName}" GIT_EMAIL="${githubUserEmail}" GH_TOKEN="${token}" --add --no-interactive -x
fi
