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

        if self.results.multi_hand_landmarks and draw:  
            for hands_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img,hands_lms,self.mp_hands.HAND_CONNECTIONS)
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
                x1,y1,x2,y2 = coords
                cv2.line(img,(x1,y1),(x2,y2),(255,0,255),2)
                if dist < 40 and not clicked :
                    pyautogui.click()
                    pyautogui.sleep(0.2)
                    clicked = True
                    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

                    
            
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
                            pyautogui.scroll(-int(delta_y*2))# *2 make scroll smoother/faster
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





