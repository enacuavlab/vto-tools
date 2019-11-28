//
// Created by garciafa on 24/10/2019.
//
#include <cstdlib>
#include <opencv2/opencv.hpp>
#include <quirc.h>

int main(int argc, char** argv)
{
    if (argc!=2)
    {
        std::cerr << "Usage : " << argv[0] << " <file>" << std::endl;
        exit(EXIT_FAILURE);
    }

    cv::Mat img=cv::imread(argv[1]);

    // Convert image to grayscale
    cv::Mat imGray;
    cv::cvtColor(img, imGray,cv::COLOR_BGR2GRAY);

    struct quirc *qr;

    qr = quirc_new();
    if (!qr)
    {
        perror("Failed to allocate memory");
        abort();
    }

    uint8_t *image;
    int w = img.size().width;
    int h= img.size().height;

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
        if (err)
            printf("DECODE FAILED: %s\n", quirc_strerror(err));
        else
        {
            std::cout << "Type : " << data.data_type << std::endl;
            // Read a code that starts with img: as a 20x20 gray image
            if (!strncmp("img:", (char *) data.payload, 4))
            {
                printf("This is an image\n");
                cv::Mat decoded(cv::Size(20, 20), CV_8UC1);
                memcpy(decoded.data, data.payload + 4, 20 * 20);
                cv::imshow("Image", decoded);
                cv::waitKey(0);
            }
            else
            {
                printf("Data: \"%s\"\n", data.payload);
            }
        }
    }

    quirc_destroy(qr);

    return EXIT_SUCCESS;
}