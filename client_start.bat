@echo off

git reset --hard HEAD
git clean -df
git pull
poetry run python main.py