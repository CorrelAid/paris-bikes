## Dash application for paris-bikes repo

To start the Dash application server locally, from root of this repo, execute:

```
python dash_app/application.py
```

and navigate to http://localhost:5000 in your browser.

- Add web components to the folder: `components/`
- At the moment, `chloropleth.py` uses the code from notebooks, but it should be refactored to use the `paris_bikes` package.
