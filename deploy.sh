#!/bin/sh

DEPLOY_BRANCH="deploy-`uuidgen`"

git stash
git checkout -b ${DEPLOY_BRANCH}
git add -f public/dist/
git commit -m "Build"
git push --delete origin gh-pages
git subtree push --prefix public origin gh-pages
git checkout -
git stash pop
git branch -D ${DEPLOY_BRANCH}
