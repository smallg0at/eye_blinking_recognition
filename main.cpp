#include <iostream>
#include <opencv2/opencv.hpp>
#include <string.h>
#include <vector>
#include <math.h>

using namespace std;
using namespace cv;

class tracked_eye{
    public:
    // unsigned long long age = 0;
    unsigned short deadticks = 0;
    unsigned int referenced = 0;
    int cx = 0;
    int cy = 0;

    void init(int, int);
    bool update(int, int, int, int);
    void noref_warning(){
        deadticks++;
    };
    void reset(){
        referenced = 0;
        // age++;
    }
};

void tracked_eye::init(int cx, int cy){
    this->cx = cx;
    this->cy = cy;
}

bool tracked_eye::update(int x, int y, int w, int h){
    if(sqrt(pow(cx-(x+w/2),2)+pow(cy-(y+h/2),2)) < 100){
    cx = x+w/2; cy=y+h/2; deadticks = 0; referenced=1;
    return true;
    }
    else {return false;}
}



string eye_cascade = "haarcascade_eye_tree_eyeglasses.xml";


int main(int argc, char const *argv[])
{
    vector<tracked_eye> eye_list;
    VideoCapture cap(0);

    while(true){
        Mat frame, grey;
        cap >> frame;
        grey = cvtColor(frame, grey, COLOR_BGR2GRAY);
        eyes = 

        imshow("frame", frame);
        if(waitKey(1)==27){
            cout<<"Terminating..."<<endl;
            return 0;
        }
    }
    

    /* code */
    return 0;
}
