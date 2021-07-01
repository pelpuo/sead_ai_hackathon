# SEAD AI Hackathon Project

[TOC]

## Team Members

- Samuel Yawson
- Edwin Kayang
- Mawunyo Avornyo
- Dominica Amanfo

## Theme

Computer Vision Application in Delivering Excellent Customer  Service in A Commercial Establishment.

## Challenge Description

The Challenge is a call to idea innovators in Ghana to compete by  creating a prototype that counts people entering and exiting a  building ( for example a commercial establishment such as a store  or a shopping mall) via a network of cameras stationed throughout  the establishment.

## Solution Description

Our solution involved the use of a motion tracking algorithm based on OpenCV, which detects colour changes in multiple frames, uses the colour changes to determine the presence of people in the frame and uses the position and area of the colour change to track the person. 

A flask app was built to deploy the model and was equipped with charts to visualize the data. It also allowed users to view the footfall statistics from previous days, and download the data to CSV.

## Tools and Libraries

- **[OpenCV](https://opencv.org/):** Used as main library for tracking the movement of people in a video
- **[Flask](https://flask.palletsprojects.com/en/2.0.x/):** Used as primary web framework to deploy model
- **[SQLAlchemy](https://www.sqlalchemy.org/):** Library used to interface with SQL database which allowed us to store footfall statistics.

## Solution Breakdown

1. Object tracking Algorithm
2. Web App

### 1. People Counter Algorithm

![Counter Algorithm](/images/algorithm.gif)

#### Steps

The algorithm first uses background subtraction to obtain the foreground which comprises of the moving individuals. The obtained result is subject to a lot of noise due to light and shadow movement. 

Thresholding is then used to filter out some of the noise but a few may remain. These are removed using the opening function in OpenCV. The opening function is comprised of two other functions: erosion and dilation. Erosion is a morphological image processing technique that takes out pixels. Dilation is then carried out to add pixels to each frame. These two operations take out a significant amount of noise from the frames obtained after background subtraction. 

Contours of each detected moving object are then found and the area of each compared to a specified range. Contours within this range are then tracked and the direction of movement past a stated y position indicated by a line gives a sense of whether a person is entering or leaving.



### 2. Web App

The flask app is a full stack website which was built using :

-  [Flask](https://flask.palletsprojects.com/en/2.0.x/) for it's backend
- HTML, CSS, Javascript and [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/) for it's frontend 
- [SQLAlchemy](https://www.sqlalchemy.org/) for it's database

#### Pages:

##### Login Page

![Login Page](/images/Login.png)

This is the first page viewed by the user when the site is accessed. Authentication was implemented using Flask-login, which verifies the user using the data stored in the database managed by [Flask-SQLAlchemy](https://pypi.org/project/Flask-SQLAlchemy/).



##### Sign Up Page

![Sign Up Page](/images/Sign_up.png)

This page is directly accessible from the login page. After details are entered, validation is done on both frontend and backend, after which the user's details are stored in the database. Password hashing was done using [Werkzeug](https://pypi.org/project/Werkzeug/).



##### Dashboard

![Dashboard](/images/Dashboard.png)

This page allows a user to feed in live camera footage or a recorded video after which the person counter algorithm performs detections in the video and returns output. If the output returned contained information about a person entering or leaving, the output is stored in the database. The line chart which was made using [Chart.js](https://www.chartjs.org/) is updated in real time whenever a new person entry is added to the database. The Cards above the chart and video feed, which also update in real time, also give information about the person count from the camera.

##### History

![History Page](/images/History.png)

This page allows a user to view the data returned by the person counter algorithm from previous days. It also has a bar chart and line chart both made with [Chart.js,](https://www.chartjs.org/) which allow a user to visualize the data. The user can also download data to CSV for further analysis.



## Setting Up the Project

#### Ensure you have the following Installed

* [Git](https://git-scm.com/)
* [Python](https://python.org/)
* [Pip](https://pypi.org/project/pip/)

#### Steps

##### On Windows:

1. Run the command in your local directory

   ```
   git clone https://github.com/pelpuo/sead_ai_hackathon.git
   ```

2. After the project has been cloned, open a terminal in the project directory

3. Ensure the python [venv](https://docs.python.org/3/library/venv.html) package is installed otherwise run:

   ```
   pip install virtualenv
   ```

4. Set up a virtual environment

   ```
   python -m venv env
   ```

5. Launch the virtual environment

   ```
   .\env\Scripts\activate
   ```

6. Install project dependencies

   ```
   pip install -r requirements.txt
   ```

7. run the following command to start the project

   ```
   py app.py
   ```

   