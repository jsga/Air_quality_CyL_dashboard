
*WORK IN PROGRESS*

The repository contains a dash/plotly/python based dashboard:

- Data from 88 weather stations is available
- Interactive map visualization: select a weather station from the map and display relevant information
- For each of the stations, a machine-learning model predicts the future values of the pollution indicators

The application is packed inside a docker container.

# The data

Data is obtained from the [open data](https://datosabiertos.jcyl.es/web/jcyl/set/es/medio-ambiente/calidad-aire-historico-horario/1284808467480) portal from the governement of Castilla y León (Spain). The data consists of air quality measurements from 88 stations scattered in the region.

# How to run locally


1. First of all, install [Docker](https://www.docker.com/)
1. Clone or download the repository `git clone https://github.com/jsga/Air_quality_CyL_dashboard.git`.
2. Make sure you are inside the main folder `cd Air_quality_CyL_dashboard`.
3. Spin up the docker: `sh run_docker.sh` this will kill existing docker processes and run new ones
4. Go to [http://localhost:8000/](http://localhost:8000/)


