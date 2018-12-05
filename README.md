The repository contains a dash/plotly/python based dashboard:

- Data from 88 weather stations is available on a daily basis
- Interactive visualizations: select a weather station from the map and a component from the drop-down menu. The figures are zoomable, hover-able and downloadable.

The application is packed inside a docker container. A Nginx server is also setup so that the application can be easily tested and deployed.

# The data

Data is obtained from the [open data](https://datosabiertos.jcyl.es/web/jcyl/set/es/medio-ambiente/calidad-aire-historico-horario/1284808467480) portal from the governement of Castilla y León (Spain). The data consists of air quality measurements from 88 stations scattered in the region.

For the purpose of this project, data is aggregated by day in order to make the csv files smaller. Hourly data is also available and could be used too.

# How to run locally

The easiest way is to run the docker compose:

1. First of all, install [Docker](https://www.docker.com/)
1. Clone or download the repository `git clone https://github.com/jsga/Air_quality_CyL_dashboard.git`.
2. Make sure your terminal is located in the main folder `cd Air_quality_CyL_dashboard`.
3. Spin up the dockers: `sh run_docker.sh` this will kill existing docker processes and run new ones
4. Go to [http://localhost:8000/](http://localhost:8000/) and enjoy.

Without installing docker you can also run the dash app. This is quite nice for dev process.

1. Clone or download the repository `git clone https://github.com/jsga/Air_quality_CyL_dashboard.git`.
2. Make sure your terminal is located in the main folder of the app `cd Air_quality_CyL_dashboard/dash`.
3. Create a Python3 `virtualenv virtualenv -p python3 venv`
4. Activate the virtualenv `source venv/bin/activate`
5. Install the requirements `pip install -r requirements.txt`
6. Run the app: `python3 app.py`

