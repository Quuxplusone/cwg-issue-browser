# CWG issue browser

This is a little Heroku app, written in Python, that caches the
text of

    http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html
    http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_closed.html
    http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_defects.html

and serves snippets of it on demand, so that your Web browser doesn't
have to fetch the entire 4.3MB page every single time — and worse,
render it! (This can be slow even on a good day, and downright prohibitive
if you're on mobile with a flaky connection.)

The app is live at [cwg-issue-browser.herokuapp.com](https://cwg-issue-browser.herokuapp.com/).


Deploying to Heroku
-------------------

To build and deploy to localhost with Heroku:

    easy_install pip
    pip install -r requirements.txt
    brew tap heroku/brew && brew install heroku
    heroku local
    open http://localhost:5000/

To build and deploy to the web with Heroku:

    brew tap heroku/brew && brew install heroku
    heroku create cwg-issue-browser
    git push heroku master
    heroku open

To make `git push heroku` work, make sure you have this section in your
`.git/config`:

    [remote "heroku"]
        url = https://git.heroku.com/cwg-issue-browser.git
        fetch = +refs/heads/*:refs/remotes/heroku/*
