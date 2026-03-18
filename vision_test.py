import cv2# handles camera and image processing
import mediapipe as mp # AI hand detection
import pyautogui # Handles mouse & keyboard control


# setup
my_hand = mp.solutions.hands # access the hand tracking module-A folder that contains everything related to hand detection (MediaPipe Hand Tracking (Hand Landmark Model))
mp_draw = mp.solutions.drawing_utils
hands = my_hand.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    min_detection_confidence=0.7
    ) # create hand detector (AI model instance)
# get monitor resolution
screen_width, screen_height = pyautogui.size()
# enable emergency stop
pyautogui.FAILSAFE = True
# open the default web cam
cap = cv2.VideoCapture(0)
 #for the shaky problem we use Weighted Moving Average
smooth_x,smooth_y = 0,0
closeness = 5 # The lower this is ,the smoother(but slower)the mouse
            

while cap.isOpened():
    
    success, img = cap.read()
    # if not successfully connected to camera program stops
    if not success:
        print("Failed to read frame")
        break
    #flip image to look like mirror
    img = cv2.flip(img,1)
    #get image dimensions
    h,w,_ = img.shape

    #convert the image color fomat bcause opencv use BGR but MediaPipe use RGB
    img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    #send image to AI model
    results = hands.process(img_rgb)

    # check wheather hand is detected
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img,hand_lms,my_hand.HAND_CONNECTIONS)
            #loop through detected hands
            finger_tips = {'Index':hand_lms.landmark[8],
                           'Thumb': hand_lms.landmark[4],
                           'Middle': hand_lms.landmark[12]
                          }

            # now converts normalized data to pixel coordinates(Camera Space)
            for name, landmark in finger_tips.items():
                cx,cy = int(landmark.x*w),int(landmark.y*h) # 0.5*640
                cv2.putText(img,name,(cx,cy-10),cv2.FONT_HERSHEY_SIMPLEX ,0.5,(255,255,255),1)#-10  for little bit top of the finger
                # draw a circle on finger
                cv2.circle(img,(cx,cy),10,(0,255,0),cv2.FILLED)

            #Screen Mapping(Screen Space)
                screen_x ,screen_y= int(landmark.x*screen_width),int(landmark.y*screen_height)

                #print(f"Index Finger at: {cx},{cy}| Screen at : {screen_width},{screen_height}")
            
            #Virtual Mouse
            # move the actual mouse
            # we use _pause = False so the code doesn't slow down
            smooth_x = smooth_x + (screen_x-smooth_x)/closeness
            smooth_y = smooth_y+ (screen_y-smooth_y)/closeness
            pyautogui.moveTo(int(smooth_x),int(smooth_y),_pause=False)

            ix,iy = int(finger_tips['Index'].x*w),int(finger_tips['Index'].y*h)
            tx,ty = int(finger_tips['Thumb'].x*w),int(finger_tips['Thumb'].y*h)
            mx,my = int(finger_tips['Middle'].x*w),int(finger_tips['Middle'].y*h)

            # calculate the Euclidean Distance
            distance = ((tx-ix)**2+(ty-iy)**2)**0.5
            # draw a line between them
            cv2.line(img,(tx,ty),(ix,iy),(255,0,255),2)


             # Right click logic
            distance_R =((tx-mx)**2+(ty-my)**2)**0.5
           
            # The 'click' & 'right click' Logic
            if distance< 35:
                cv2.line(img,(tx,ty),(ix,iy),(0,0,255),5)
                pyautogui.click()
                pyautogui.sleep(0.2) # small delay to prevent 'double clicking' accidentally

           
            elif distance_R< 35:
                cv2.line(img,(tx,ty),(mx,my),(0,0,255),5)
                pyautogui.click(button='right')
                pyautogui.sleep(0.2)

        #Display
    cv2.imshow("Coordinate Tracker",img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()# releases camera resource
cv2.destroyAllWindows() # close all opencv windows

