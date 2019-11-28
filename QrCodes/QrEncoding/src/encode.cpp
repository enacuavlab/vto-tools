#include <cstdlib>
#include <string>
#include <qrencode.h>
#include <iostream>
#include <opencv2/opencv.hpp>

cv::Mat QrCodeToCvMt (QRcode * qrCode,int size, std::array<uint8_t,3> bgColor)
{
    int codeSize = qrCode->width;
    int imgSize = size;
    int border = size/10;
    int pixelSize = 0.8*size/codeSize;

    std::cout << size << " " << border << " " << pixelSize << std::endl;
    std::cout << (int)bgColor[0] << " " << (int)bgColor[1] << " " << (int)bgColor[2] << std::endl;
    auto bgColorCv = cv::Scalar(bgColor[0],bgColor[1],bgColor[2]);

    cv::Mat img(imgSize,imgSize,CV_8UC3,bgColorCv);
    cv::rectangle(img,cv::Point(0,0),cv::Point(imgSize,imgSize),bgColorCv,CV_FILLED);

    for (int row=0;row<qrCode->width;row++)
    {
        for (int col = 0; col < qrCode->width; col++)
        {
            if (qrCode->data[row+codeSize*col] & 0x01)
            {

                cv::rectangle(img,
                              cv::Point(pixelSize * row + border, pixelSize * col + border),
                              cv::Point(pixelSize * row + pixelSize- 1 + border, pixelSize * col + pixelSize - 1 + border),
                              cv::Scalar(0,0,0),CV_FILLED);
            }
        }
    }

    return img;
}

int main (int argc, char** argv)
{
    if (argc!=3 && argc!=5)
    {
        std::cerr << "usage : " << argv[0] << " <text> <file> [<b,g,r> <size>]" << std::endl;
        exit(EXIT_FAILURE);
    }
    std::string data(argv[1]);

    std::array<uint8_t,3> bgColor={255,255,255};
    size_t size=600;
    if (argc==5)
    {
        size = atoi(argv[4]);
        std::stringstream sstr(argv[3]);
        char c;
        int col;
        for (int i=0;i<3;++i)
        {
            sstr >> col;
            bgColor[i]=col;
            if (i!=2)
                sstr>>c;
        }
    }

    auto qrCode = QRcode_encodeString8bit(data.c_str(), 0, QR_ECLEVEL_L);

    /*
    auto input = QRinput_new2(0,QR_ECLEVEL_L);
    cv::Mat toEncode=cv::imread("signature.jpg",cv::IMREAD_COLOR);
    cv::cvtColor(toEncode,toEncode,CV_BGR2GRAY);
    cv::resize(toEncode,toEncode,cv::Size(20,20));
    int dataSize = 20*20;
    auto *data = (uint8_t*)malloc(dataSize* sizeof(uint8_t)+4);
    memcpy(data,"img:",4);
    memcpy(data+4,toEncode.data,dataSize);
    QRinput_append(input,QR_MODE_8,dataSize+4,data);
    std::cout << (uint)data[5] << std::endl;

    auto qrCode = QRcode_encodeInput(input);
    */
    cv::Mat img = QrCodeToCvMt(qrCode,size,bgColor);

    //cv::imshow("QrCode",img);
    //cv::waitKey(0);

    cv::imwrite(argv[2],img);

    return EXIT_SUCCESS;
}