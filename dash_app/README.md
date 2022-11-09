## Dash application for paris-bikes repo

To install dash, activate the `paris-bikes` environment and run:

```
pip install dash
pip install jupyter-dash
```

To start the application server, from root of this repo, execute:
```
python dash_app/application.py
```
navigate to http://localhost:5000 in your browser.

- Add web components to the folder: `components/`
- At the moment, `chloropleth.py` uses the code from notebooks, but it should be refactored to use the `paris_bikes` package.
