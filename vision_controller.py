import cv2
import mediapipe as mp
import pyautogui
import math

class HandController:
    def __init__(self,max_hands = 2,detection_con =0.7,track_con = 0.5):

        # initialize mediapipe
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode =False,
            max_num_hands = max_hands,
            min_detection_confidence = detection_con,
            min_tracking_confidence = track_con
        )
        self.screen_width,self.screen_height = pyautogui.size()
        pyautogui.FAILSAFE = True

    def find_hands(self,img,draw = True):
        img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        h,w ,_= img.shape

        if self.results.multi_hand_landmarks and draw:  
            for hands_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img,hands_lms,self.mp_hands.HAND_CONNECTIONS)
                finger_tips ={'Index':hands_lms.landmark[8],
                      'Thumb': hands_lms.landmark[4],
                      'Middle': hands_lms.landmark[12],
                      'Ring': hands_lms.landmark[16]}
                for name, landmark in finger_tips.items():
                    cx,cy = int(landmark.x*w),int(landmark.y*h) # 0.5*640
                    cv2.putText(img,name,(cx,cy-10),cv2.FONT_HERSHEY_SIMPLEX ,0.5,(255,255,255),1)#-10  for little bit top of the finger
                    # draw a circle on finger
                    cv2.circle(img,(cx,cy),10,(0,255,0),cv2.FILLED)

        return img
    def get_position(self,img,hand_no =0):
        lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h,w,c = img.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                lm_list.append([id,cx,cy,lm.x,lm.y])
        return lm_list
    
    def get_distance(self,p1,p2,lm_list):
        # Euclidean distance between two points
        x1,y1 =lm_list[p1][1],lm_list[p1][2]
        x2,y2 = lm_list[p2][1],lm_list[p2][2]
        distance = math.hypot(x2-x1,y2-y1)
        return distance,[x1,y1,x2,y2]
    
def main():
        cap = cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480)
        detector = HandController()
        smooth_x, smooth_y = 0,0
        closeness = 5
        clicked = False
        prev_y = 0
        scrolling = False
        double_click = False
        scroll_smooth = 0
        scroll_factor = 2
        scroll_closeness = 5
        while cap.isOpened():
            success, img = cap.read()
            if not success:break
            img =cv2.flip(img,1)

            #1.detect hands
            img = detector.find_hands(img)
            lm_list = detector.get_position(img)

            if len(lm_list) != 0:
                
                if len(lm_list)> 8:
                    # get the coordinates for Index Tip and Thub Tip
                    idx_x,idx_y = lm_list[8][3],lm_list[8][4]

                # Smoothing logic & Movement

                    target_x = idx_x* detector.screen_width
                    target_y = idx_y* detector.screen_height

                    smooth_x = smooth_x + (target_x - smooth_x)/closeness
                    smooth_y = smooth_y + (target_y - smooth_y)/closeness

                pyautogui.moveTo(int(smooth_x), int(smooth_y),_pause = False)

                # Check for Click (Distance beteen 4,8)
                dist,coords = detector.get_distance(4,8,lm_list)
                dist_double ,_ = detector.get_distance(4,16,lm_list)
                x1,y1,x2,y2 = coords
                
                if dist_double < 30 and not double_click:
                    pyautogui.doubleClick()
                    pyautogui.sleep(0.3)
                    double_click = True
                    clicked = True  # prevent single click

                elif dist_double >= 30:
                    double_click = False
                    

                if dist < 40 and not clicked:
                    pyautogui.click()
                    pyautogui.sleep(0.2)
                    clicked = True
                    cv2.putText(img,"click", (50,100),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
                    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),5)

                elif dist >= 40:
                    clicked = False     
                if len(lm_list)>12:
                    dist_right,_ = detector.get_distance(4,12,lm_list)
                    dist_scroll,_ = detector.get_distance(8,12,lm_list)
                    if dist_right < 30:
                        pyautogui.click(button='right')
                        pyautogui.sleep(0.2)
                        clicked =True
                    elif dist_right >= 30:
                        clicked = False
                   
                    if dist_scroll < 30:
                        current_y = lm_list[8][2]
                        if scrolling:
                            delta_y = current_y - prev_y
                            scroll_smooth = scroll_smooth +(delta_y-scroll_smooth)/scroll_closeness
                            pyautogui.scroll(-int(delta_y*scroll_factor))# *2 make scroll smoother/faster
                        prev_y = current_y
                        scrolling = True

                        cv2.putText(img,"SCROLL MODE", (50,100),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
                    else:
                        scrolling = False
                        


                cv2.imshow("AI Controller", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    main()





