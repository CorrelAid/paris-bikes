# Where to build new bike parking spots in Paris?

This is the repository of the CorreAid project `paris-bikes` in collaboration with the City of Paris.
TODO ADD CONTEXT AND GOALS

## Paris Parking Demand Index

The Paris Parking Demand Index is a web app that visualizes the number of existing bicycle parking spaces in the City of Paris in relation to metrics that might indicate demand for bicycle parking, such as the number of stores or people entering the metro.
Aggregated at the IRIS level, the smallest unit of municipal infrastructure in France, this index helps determine how adequately areas are served in terms of parking facilities, while leaving flexibility as to which exact location they should be built.
All data used in this project is open data from municipal and regional open data portals.

Have a look [here TODO ADD LINK](TODO ADD LINK) at a hosted version of the Parking Demand Index.

You can also clone the repository and work with the code yourself. See section [Project setup](#-Project-setup).

## Blog article

Would you like to learn more about the project, and how we worked together as a group of volunteers to address the challenge of supporting decision-making in the City of Paris with open data? Check out the [blog article about this project TODO ADD LINK](TODO ADD LINK)!

## Contributors

TODO List of contributors incl. role/types of contributions (to also highlight non-code contributions that are not directly visible on GitHub!)

## We thank
<p>
    <img src="img/Ville_de_Paris_Logo.png" width="100">
    <img src="img/LPI_Logo.png" width="130"> 
    <img src="img/CorrelAid_Logo.png" width="130" style="margin-left:20px">
</p>

# Project setup

## Dash application

The is the web app of the Parking Demand Index. It is an interactive map, which allows you to select and combine different metrics to calculate and visualize parking demand for IRIS sectors in Paris. 

To start the Dash application server locally, from the root of this repo, execute:

```
python paris_bikes/dash_application.py
```

and navigate to http://localhost:5000 in your browser.

## Development environment

We use `python>=3.10` and [`poetry`](https://python-poetry.org/docs/basic-usage/) to manage our development environment.
`poetry` manages dependencies and makes it easy to create a virtual environment that is compatible with our package.
You can install `poetry` using `conda` or `pip`.

To setup a development environment:

```bash
poetry install
```

> If you are on Apple Silicon, you might have to install `gdal`, a dependency of `fiona`/`geopandas`.
You can do this with homebrew: `brew install gdal`

To activate the virtual environment:

```bash
poetry shell
```

## Data management

We use [DVC](https://dvc.org/) for data management and version control.
DVC is setup to store our data repository on our project's Google Drive (folder name `dvcstore`).

DVC is easy to use and follows a syntax similar to git.

**To install DVC:**

DVC is already installed if you followed the [Environment](#environment) setup.
If necessary, check [here](https://dvc.org/doc/install) for other installation methods.

**To get DVC-managed files from the remote repository:**

```bash
dvc pull
```

**To track a new data file with DVC:**

```bash
dvc add data/new_file.csv
git commit -m "Add new data file"
```

**To push new DVC-managed files to the remote repository:**

```bash
dvc push
```

**To sync DVC-managed files with the current git branch/commit:**

```bash
dvc checkout
```

A quick starting guide can be found [here](https://dvc.org/doc/start/data-management).

# Project management

## Useful links

- [Google Drive](https://drive.google.com/drive/folders/1mmsON23Bz-7xB3Y3qGHC0kqSKG6aXUVr)
- [Slack channel](https://correlaid.slack.com/archives/C03NAN24GDN)
- [Planning Mural](https://app.mural.co/t/correlaid9916/m/correlaid9916/1657610032235/e86d4422b5be6421cd132e9c47a3eb82f0d191f3)
- [Team Manifesto Mural](https://app.mural.co/t/correlaid9916/m/correlaid9916/1657265397906/558401920c32987ce75a2853aaea0e06aa6e94e2)
- [CorrelAid docs](https://docs.correlaid.org/)

## Definition of Done

How do we know that we're really done with a task and have not forgotten anything important? In this project, we use the following Definition of Done:

- **Functionality**: the code runs / has no defects
- **Code documentation**: the code itself is properly documented
- **Data documentation**: metadata of raw files should be documented in `data/metadata.md`
- **Project documentation** such as README/wiki is updated where necessary
    - scope/features of project: what does this project do? How can you run it?
    - setup of project
        - data requirements (files, folders)
        - software requirements (packages, other tooling)
    - developer documentation: things like the definition of done, agreed upon standards, ...
- **Peer Review**: someone else has had a look at the code and tested it on their machine
- **Git**: the code is ready to be merged to the main branch or is already on the main branch
- **Clean Repository**: old, outdated code and files are deleted
- **Consistent code style**: code is styled consistently and linted using `black`
- **Unit tests**
    - existing unit tests pass
    - if possible: new code is properly tested
    - unit test coverage >xx%

See [here](https://github.com/CorrelAid/definition-of-done) for more details.
