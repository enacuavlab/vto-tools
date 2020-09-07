#include <iostream>
#include <opencv2/opencv.hpp>
#include <chrono>
#include <quirc.h>

#define COMPUTE_FPS 0

cv::Mat last_img;

typedef struct
{
    int type;
    std::string data;
    std::vector <cv::Point> location;
} decodedObject;

// Find and decode barcodes and QR codes
void decode(cv::Mat &img, std::vector<decodedObject>&decodedObjects)
{
    struct quirc *qr;
    // Convert image to grayscale
    cv::Mat imGray;
    cv::cvtColor(img, imGray,cv::COLOR_BGR2GRAY);

    uint8_t *image;
    int w = img.size().width;
    int h= img.size().height;

    qr = quirc_new();
    if (!qr)
    {
        perror("Failed to allocate memory");
        abort();
    }

    if (quirc_resize(qr, w, h) < 0) {
        perror("Failed to allocate video memory");
        abort();
    }

    image = quirc_begin(qr, &w, &h);

    /* Fill out the image buffer here.
     * image is a pointer to a w*h bytes.
    * One byte per pixel, w pixels per line, h lines in the buffer.
    */
    memcpy(image,imGray.data,h*w);

    quirc_end(qr);
    int num_codes;
    int i;

/* We've previously fed an image to the decoder via
* quirc_begin/quirc_end.
*/

    num_codes = quirc_count(qr);
    for (i = 0; i < num_codes; i++)
    {
        struct quirc_code code;
        struct quirc_data data;
        quirc_decode_error_t err;

        quirc_extract(qr, i, &code);

        /* Decoding stage */
        err = quirc_decode(&code, &data);
        if (!err)
        {
            decodedObject obj;
            obj.type=data.data_type;
            for (int charNum=0; charNum < data.payload_len; ++charNum)
            {
                if (data.payload[charNum]<=127)
                    obj.data+=(char)data.payload[charNum];
            }
            for (int j=0;j<4;++j)
            {
                obj.location.push_back(cv::Point(code.corners[j].x,code.corners[j].y));
            }
            decodedObjects.push_back(obj);
        }
    }
    quirc_destroy(qr);
}

// Display barcode and QR code location
void display(cv::Mat &im, std::vector<decodedObject>&decodedObjects)
{
#if COMPUTE_FPS == 1
    static int frames=0;
    static auto lastFrameTime = std::chrono::high_resolution_clock::now();
    static std::chrono::duration<double> duration;
#endif
    // Loop over all decoded objects
    for(int i = 0; i < decodedObjects.size(); i++)
    {
        std::vector<cv::Point> points = decodedObjects[i].location;
        std::vector<cv::Point> hull;

        // If the points do not form a quad, find convex hull
        if(points.size() > 4)
            convexHull(points, hull);
        else
            hull = points;

        // Number of points in the convex hull
        int n = hull.size();

        if (n)
        {
            cv::Point mid(0, 0);
            for (int j = 0; j < n; j++)
            {
                mid += hull[j];
                line(im, hull[j], hull[(j + 1) % n], cv::Scalar(100, 255, 100), 10);
            }
            mid /= n;
            //cv::putText(im, decodedObjects[i].data, mid, cv::FONT_HERSHEY_PLAIN, 2.0, cv::Scalar(255, 0, 0), 4);
        }
    }
#if COMPUTE_FPS == 1
    ++frames;
    if (frames==10)
    {
        auto now = std::chrono::high_resolution_clock::now();
        duration = now - lastFrameTime;
        lastFrameTime = now;
        frames=0;
    }
    std::stringstream sstr;
    sstr.precision(4);
    sstr << 10 / duration.count() << " fps";
    cv::putText(im, sstr.str(), cv::Point(10, 20), cv::FONT_HERSHEY_PLAIN, 1.0, cv::Scalar(255, 0, 0), 2);
#endif

    // Display results
    imshow("Video", im);
}

void clearList(int state, void* userdata)
{
    (void)userdata;
    std::cout << "Button callback "  << state << std::endl;
}

void clickCallback(int event, int x, int y, int flags, void* userdata)
{
  static int nbImgs = 0;
  if  (event == cv::EVENT_LBUTTONDOWN) {
    std::cout << "Left button of the mouse is clicked - position (" << x << ", " << y << ")" << std::endl;
    std::ostringstream stringStream;
    stringStream << "/home/pprz/Projects/vto-tools/QrCodes/JPOQrCodeDemo/imgs_saved/img" << nbImgs << ".jpg";
    imwrite(stringStream.str(), last_img);
    nbImgs++;
  }
}


int main (int argc, char** argv)
{
    cv::namedWindow("Video", CV_WINDOW_NORMAL);
    cv::resizeWindow("Video",1280,720);
    cv::moveWindow("Video", 0, 0);

    cv::setMouseCallback("Video", clickCallback, NULL);

    cv::Mat frame;
    cv::VideoCapture cap;
    if (argc==2)
    {
      std::cout << "Opening " << argv[1] << "...";
      std::cout.flush();
        cap=cv::VideoCapture (argv[1]);
	std::cout << "Done !" << std::endl;
    }
    else
    {
        cap=cv::VideoCapture ("/dev/video0");
    }

    if (!cap.isOpened())
    {
        std::cerr << "Could not open camera !" << std::endl;
        exit(EXIT_FAILURE);
    }
    bool end = false;

    std::map<std::string,decodedObject> knownObjects;
    static std::map<char,std::string> tagToName = {
      {'L',"LICORNES"},
      {'l',"LICORNES"},
      {'F',"FEES"},
      {'f',"FEES"},
      {'E',"ELFES"},
      {'e',"ELFES"},
      {'R',"RENNES DE RECHANGE"},
      {'r',"RENNES DE RECHANGE"},
      {'B',"BONNETS ROUGES"},
      {'b',"BONNETS ROUGES"},
    };

    while(!end)
    {
        cap >> frame;
        last_img = frame;

        // Variable for decoded objects
        std::vector<decodedObject> decodedObjects;

        decode(frame, decodedObjects);

        for (auto obj: decodedObjects)
        {
            if (knownObjects.find(obj.data)==knownObjects.end())
            {
                std::string &packName=obj.data;
                knownObjects[obj.data]=obj;
		std::cout << "Repérage d'un carton de " << tagToName[obj.data[0]] << std::endl;
            }
        }

	std::map<char,int> inventaire;
	for (auto code :knownObjects)
	  {
	    auto name = code.first;
	    inventaire[name[0]]+=1;
	  }
	int offset_y=40;
	for (auto obj: inventaire)
	  {
	    std::stringstream sstr;
	    sstr << tagToName[obj.first] << " : " <<  obj.second;
	    cv::putText(frame, sstr.str(), cv::Point(10, offset_y), cv::FONT_HERSHEY_PLAIN, 3.0, cv::Scalar(100, 255, 100), 2);
	    offset_y+=40;
	  }

	display(frame, decodedObjects);

        auto c=cv::waitKey(10);
        if (c=='q' or c=='Q')
        {
            end=true;
        }
    }
    cv::destroyAllWindows();
      
    std::map<char,int> inventaire;
    for (auto code :knownObjects)
      {
	auto name = code.first;
	inventaire[name[0]]+=1;
      }
    std::cout << "Inventaire :" << std::endl;
    for (auto obj: inventaire)
      {
	std::cout << "\t" << tagToName[obj.first] << " : " <<  obj.second << std::endl;
      }

    return EXIT_SUCCESS;
}
