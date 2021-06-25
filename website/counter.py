import numpy as np
import cv2
import pandas as pd

# from . import db
from datetime import datetime
from .models import Customer

# draw horizontal line for detection
def detection_line(y_pos,frame):
    width = frame.shape[1]
    cv2.line(frame, (0,y_pos), (width,y_pos ), (0,255,0), 2)

def compute_people(video, user_id, db):
    cap = cv2.VideoCapture(video)

    frames_count, fps, width, height = cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    width = int(width)
    height = int(height)

    size = (width, height)

    # creates a pandas data frame with the number of rows the same length as frame count
    df = pd.DataFrame(index=range(int(frames_count)))
    df.index.name = "Frames"

    framenumber = 0  # keeps track of current frame
    exiting = 0  # keeps track of people that exited
    entering = 0  # keeps track of people that entered
    PersonIDs = []  # blank list to add people ids
    has_crossed = []  # blank list to add people ids that have crossed
    totalpeople = 0  # keeps track of total people

    object_detector = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold=40, detectShadows=False)

    while True:
        has_frame, frame = cap.read()

        if has_frame:

            mask = object_detector.apply(frame)
            _, mask2 = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
            kernel = np.ones((5,5),np.uint8)
            opening = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel)
            contours, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            lineypos = 130
            cv2.line(frame, (0, lineypos), (width, lineypos), (255, 0, 0), 2)

            lineypos2 = 140
            detection_line(lineypos2,frame)
            
            minarea = 1000
            maxarea = 10000

            # vectors for the x and y locations of contour centroids in current frame
            cxx = np.zeros(len(contours))
            cyy = np.zeros(len(contours))

            for i in range(len(contours)):  # cycles through all contours in current frame
                area = cv2.contourArea(contours[i])  # area of contour
                if minarea < area < maxarea:  # area threshold for contour
                    # calculating centroids of contours
                    cnt = contours[i]
                    M = cv2.moments(cnt)
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    x, y, w, h = cv2.boundingRect(cnt)

                    # creates a rectangle around contour
                    cv2.drawMarker(frame, (cx, cy), (255, 255, 255), cv2.MARKER_STAR, markerSize=5, thickness=1, line_type=cv2.LINE_AA)
                    #cv2.putText(frame, str(area), (cx + 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 0, 255), 1)

                    cxx[i] = cx
                    cyy[i] = cy

            # eliminates zero entries (centroids that were not added)
            cxx = cxx[cxx != 0]
            cyy = cyy[cyy != 0]

            # empty list to later check which centroid indices were added to dataframe
            minx_index2 = []
            miny_index2 = []

            # maximum allowable radius for current frame centroid to be considered the same centroid from previous frame
            maxrad = 50

            # The section below keeps track of the centroids and assigns them to old carids or new carids

            if len(cxx):  # if there are centroids in the specified area

                if not PersonIDs:  # if carids is empty

                    for i in range(len(cxx)):  # loops through all centroids

                        PersonIDs.append(i)  # adds a persons id to the empty list personids
                        df[str(PersonIDs[i])] = ""  # adds a column to the dataframe corresponding to a personid

                        # assigns the centroid values to the current frame (row) and carid (column)
                        df.at[int(framenumber), str(PersonIDs[i])] = [cxx[i], cyy[i]]

                        totalpeople = PersonIDs[i] + 1  # adds one count to total persons

                else:  # if there are already person ids

                    dx = np.zeros((len(cxx), len(PersonIDs)))  # new arrays to calculate deltas
                    dy = np.zeros((len(cyy), len(PersonIDs)))  # new arrays to calculate deltas

                    for i in range(len(cxx)):  # loops through all centroids

                        for j in range(len(PersonIDs)):  # loops through all recorded person ids

                            # acquires centroid from previous frame for specific personid
                            oldcxcy = df.iloc[int(framenumber - 1)][str(PersonIDs[j])]

                            # acquires current frame centroid that doesn't necessarily line up with previous frame centroid
                            curcxcy = np.array([cxx[i], cyy[i]])

                            if not oldcxcy:  # checks if old centroid is empty in case person leaves screen and new person shows

                                continue  # continue to next personid

                            else:  # calculate centroid deltas to compare to current frame position later

                                dx[i, j] = oldcxcy[0] - curcxcy[0]
                                dy[i, j] = oldcxcy[1] - curcxcy[1]

                    for j in range(len(PersonIDs)):  # loops through all current person ids
                        sumsum = np.abs(dx[:, j]) + np.abs(dy[:, j])  # sums the deltas wrt to person ids

                        # finds which index personid had the min difference and this is true index
                        correctindextrue = np.argmin(np.abs(sumsum))
                        minx_index = correctindextrue
                        miny_index = correctindextrue

                        # acquires delta values of the minimum deltas in order to check if it is within radius later on
                        mindx = dx[minx_index, j]
                        mindy = dy[miny_index, j]

                        if mindx == 0 and mindy == 0 and np.all(dx[:, j] == 0) and np.all(dy[:, j] == 0):
                            # checks if minimum value is 0 and checks if all deltas are zero since this is empty set
                            # delta could be zero if centroid didn't move

                            continue  # continue to next personid

                        else:

                            # if delta values are less than maximum radius then add that centroid to that specific personid
                            if np.abs(mindx) < maxrad and np.abs(mindy) < maxrad:

                                # adds centroid to corresponding previously existing personid
                                df.at[int(framenumber), str(PersonIDs[j])] = [cxx[minx_index], cyy[miny_index]]
                                minx_index2.append(minx_index)  # appends all the indices that were added to previous personids
                                miny_index2.append(miny_index)

                    for i in range(len(cxx)):  # loops through all centroids

                        # if centroid is not in the minindex list then another car needs to be added
                        if i not in minx_index2 and miny_index2:

                            df[str(totalpeople)] = ""  # create another column with total persons
                            totalpeople = totalpeople + 1  # adds one to the total person count
                            t = totalpeople - 1  # t is a placeholder to total persons
                            PersonIDs.append(t)  # append to list of persons ids
                            df.at[int(framenumber), str(t)] = [cxx[i], cyy[i]]  # add centroid to the new person id

                        elif curcxcy[0] and not oldcxcy and not minx_index2 and not miny_index2:
                            # checks if current centroid exists but previous centroid does not
                            # new car to be added in case minx_index2 is empty

                            df[str(totalpeople)] = ""  # create another column with total persons
                            totalpeople = totalpeople + 1  # adds one to the total person count
                            t = totalpeople - 1  # t is a placeholder to total persons
                            PersonIDs.append(t)  # append to list of person ids
                            df.at[int(framenumber), str(t)] = [cxx[i], cyy[i]]  # add centroid to the new person id

            # The section below labels the centroids on screen

            currentpeople = 0  # current persons on screen
            currentpeopleindex = []  # current persons on screen personid index

            for i in range(len(PersonIDs)):  # loops through all personids

                if df.at[int(framenumber), str(PersonIDs[i])] != '':
                    # checks the current frame to see which person ids are active
                    # by checking in centroid exists on current frame for certain person id

                    currentpeople = currentpeople + 1  # adds another to current persons on screen
                    currentpeopleindex.append(i)  # adds person ids to current persons on screen

            for i in range(currentpeople):  # loops through all current person ids on screen

                # grabs centroid of certain personid for current frame

                curcent = df.iloc[int(framenumber)][str(PersonIDs[currentpeopleindex[i]])]

                # grabs centroid of certain personid for previous frame
                oldcent = df.iloc[int(framenumber - 1)][str(PersonIDs[currentpeopleindex[i]])]

                if curcent:  # if there is a current centroid

                    if oldcent:  # checks if old centroid exists
                        # adds radius box from previous centroid to current centroid for visualization
                        xstart = oldcent[0] - maxrad
                        ystart = oldcent[1] - maxrad
                        xwidth = oldcent[0] + maxrad
                        yheight = oldcent[1] + maxrad

                        now = datetime.now()
                        # checks if old centroid is on or below line and curcent is on or above line
                        # to count persons and that person hasn't been counted yet
                        if oldcent[1] >= lineypos2 and curcent[1] <= lineypos2 and PersonIDs[currentpeopleindex[i]] not in has_crossed:
                            if area > 10000:
                                exiting = exiting + 2
                                customer = Customer(date=now, status="exit", user_id=user_id)
                                customer2 = Customer(date=now, status="exit", user_id=user_id)
                                # db.session.add(customer)
                                # db.session.add(customer2)
                                
                            else:
                                exiting = exiting + 1
                                customer = Customer(date=now, status="exit", user_id=user_id)
                                # db.session.add(customer)

                            cv2.line(frame, (0, lineypos2), (width, lineypos2), (0, 0, 255), 5)
                            has_crossed.append(
                                currentpeopleindex[i])  # adds person id to list of count of persons to prevent double counting

                        # checks if old centroid is on or above line and curcent is on or below line
                        # to count persons and that person hasn't been counted yet
                        elif oldcent[1] <= lineypos2 and curcent[1] >= lineypos2 and PersonIDs[currentpeopleindex[i]] not in has_crossed:
                            if area > 10000:
                                entering = entering + 2
                                customer = Customer(date=now, status="entry", user_id=user_id)
                                customer2 = Customer(date=now, status="entry", user_id=user_id)
                                # db.session.add(customer)
                                # db.session.add(customer2)
                            else:
                                entering = entering + 1
                                customer = Customer(date=now, status="entry", user_id=user_id)
                                # db.session.add(customer)
                            
                            print(customer)

                            cv2.line(frame, (0, lineypos2), (width, lineypos2), (0, 0, 125), 5)
                            has_crossed.append(currentpeopleindex[i])

                        # db.session.commit()
        
            cv2.putText(frame, "Entry Count: " + str(entering), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 0), 1)

            cv2.putText(frame, "Exit Count: " + str(exiting), (0, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),1)    

            cv2.putText(frame, "Count of People Inside: " + str(entering-exiting), (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 0, 0), 1)

            cv2.putText(frame, "Frame: " + str(framenumber) + ' of ' + str(frames_count), (0, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


            # adds to framecount
            framenumber = framenumber + 1

            # k = cv2.waitKey(30) & 0xff
            # if k == 27:
            #     break
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
    # else:  # if video is finished then break loop
    #     break

    # cap.release()
# cv2.destroyAllWindows()

# saves dataframe to csv file for later analysis
# df.to_csv('People.csv', sep=',')