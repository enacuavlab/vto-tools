/*
Copyright © 2012 NaturalPoint Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */


#include <stdio.h>
#include <inttypes.h>
#include <string>
#include <map>
#include <assert.h>
#include <chrono>
#include <thread>
#include <vector>


#pragma warning( disable : 4996 )

#ifdef VDEBUG
#undef VDEBUG
#endif
// #define VDEBUG

#ifndef ORIGINAL_SDK
#include <cstring>
#include <cstdlib>
#include <vector>

using std::min;

// non-standard/optional extension of C; define an unsafe version here
// to not change example code below
int strcpy_s(char *dest, size_t destsz, const char *src)
{
    strcpy(dest, src);
    return 0;
}

template <size_t size>
int strcpy_s(char (&dest)[size], const char *src)
{
    return strcpy_s(dest, size, src);
}

template <typename... Args>
int sprintf_s(char *buffer, size_t bufsz, const char *format, Args... args)
{
    return sprintf(buffer, format, args...);
}

#endif

#define MAX_NAMELENGTH              256

// NATNET message ids
#define NAT_FRAMEOFDATA             7


// SAME STRUCTURE AS MAIN
#define MAX_BODIES  6
struct rigidbody_t {
  uint32_t id;
  float pos[3];
  float ori[4];
};
struct rigidbodies_t {
  uint32_t fr;
  uint32_t nb;
  struct rigidbody_t bodies[MAX_BODIES];
};
struct rigidbodies_t bodies;
// SAME STRUCTURE AS MAIN


int gNatNetVersion[4] = { 0,0,0,0 };


// Packet unpacking functions
char * Unpack(char * pPacketIn);
char * MyUnpack(char * pPacketIn,int major,int minor,void *data);
char* UnpackPacketHeader(char* ptr, int& messageID, int& nBytes, int& nBytesTotal);
// Frame data
char * UnpackFrameData(char* inptr, int nBytes, int major, int minor,void *data);
char * UnpackFramePrefixData(char * ptr, int major, int minor, void *data);
char * UnpackMarkersetData(char * ptr, int major, int minor);
char * UnpackRigidBodyData(char * ptr, int major, int minor, void *data);
char * UnpackSkeletonData(char * ptr, int major, int minor);
char * UnpackLabeledMarkerData(char* ptr, int major, int minor);
char * UnpackForcePlateData(char * ptr, int major, int minor);
char * UnpackDeviceData(char * ptr, int major, int minor);
char * UnpackFrameSuffixData(char * ptr, int major, int minor);





/*
* MakeAlnum
* For now, make sure the string is printable ascii.  
*/ 
void MakeAlnum(char* szName, int len)
{
    int i = 0, i_max = len;
    szName[len - 1] = 0;
    while ((i < len) && (szName[i] != 0))
    {
        if (szName[i] == 0)
        {
            break;
        }
        if (isalnum(szName[i]) == 0)
        {
            szName[i] = ' ';
        }
        ++i;
    }
}


// Funtion that assigns a time code values to 5 variables passed as arguments
// Requires an integer from the packet as the timecode and timecodeSubframe
bool DecodeTimecode(unsigned int inTimecode, unsigned int inTimecodeSubframe, int* hour, int* minute, int* second, int* frame, int* subframe)
{
	bool bValid = true;

	*hour = (inTimecode>>24)&255;
	*minute = (inTimecode>>16)&255;
	*second = (inTimecode>>8)&255;
	*frame = inTimecode&255;
	*subframe = inTimecodeSubframe;

	return bValid;
}

// Takes timecode and assigns it to a string
bool TimecodeStringify(unsigned int inTimecode, unsigned int inTimecodeSubframe, char *Buffer, int BufferSize)
{
	bool bValid;
	int hour, minute, second, frame, subframe;
	bValid = DecodeTimecode(inTimecode, inTimecodeSubframe, &hour, &minute, &second, &frame, &subframe);

	sprintf_s(Buffer,BufferSize,"%2d:%2d:%2d:%2d.%d",hour, minute, second, frame, subframe);
	for(unsigned int i=0; i<strlen(Buffer); i++)
		if(Buffer[i]==' ')
			Buffer[i]='0';

	return bValid;
}

void DecodeMarkerID(int sourceID, int* pOutEntityID, int* pOutMemberID)
{
    if (pOutEntityID)
        *pOutEntityID = sourceID >> 16;

    if (pOutMemberID)
        *pOutMemberID = sourceID & 0x0000ffff;
}








char * UnpackFrameData(char * inptr, int nBytes, int major, int minor, void *data)
{
    char * ptr = inptr;
    printf("MoCap Frame Begin\n---------------- - \n" );

//    ptr = UnpackFramePrefixData(ptr, major, minor);
    ptr = UnpackFramePrefixData(ptr, major, minor, data);

    ptr = UnpackMarkersetData(ptr, major, minor);

//    ptr = UnpackRigidBodyData(ptr, major, minor);
    ptr = UnpackRigidBodyData(ptr, major, minor, data);

    ptr = UnpackSkeletonData(ptr, major, minor);

    ptr = UnpackLabeledMarkerData(ptr, major, minor);

    ptr = UnpackForcePlateData(ptr, major, minor);

    ptr = UnpackDeviceData(ptr, major, minor);

    ptr = UnpackFrameSuffixData(ptr, major, minor);

    printf("MoCap Frame End\n---------------- - \n" );
        return ptr;
}

char* UnpackFramePrefixData(char* ptr, int major, int minor, void *data)
{
    memcpy(&((*((rigidbodies_t *)data)).fr), ptr, 4);

    // Next 4 Bytes is the frame number
    int frameNumber = 0; memcpy(&frameNumber, ptr, 4); ptr += 4;
    printf("Frame # : %d\n", frameNumber);

    return ptr;
}



char* UnpackMarkersetData(char* ptr, int major, int minor)
{
    // First 4 Bytes is the number of data sets (markersets, rigidbodies, etc)
    int nMarkerSets = 0; memcpy(&nMarkerSets, ptr, 4); ptr += 4;
    printf("Marker Set Count : %3.1d\n", nMarkerSets);

    // Loop through number of marker sets and get name and data
    for (int i = 0; i < nMarkerSets; i++)
    {
        // Markerset name
        char szName[MAX_NAMELENGTH];
        strcpy_s(szName, ptr);
        int nDataBytes = (int)strlen(szName) + 1;
        ptr += nDataBytes;
        MakeAlnum(szName, MAX_NAMELENGTH);
        printf("Model Name       : %s\n", szName);

        // marker data
        int nMarkers = 0; memcpy(&nMarkers, ptr, 4); ptr += 4;
        printf("Marker Count     : %3.1d\n", nMarkers);

        for (int j = 0; j < nMarkers; j++)
        {
            float x = 0; memcpy(&x, ptr, 4); ptr += 4;
            float y = 0; memcpy(&y, ptr, 4); ptr += 4;
            float z = 0; memcpy(&z, ptr, 4); ptr += 4;
            printf("  Marker %3.1d : [x=%3.2f,y=%3.2f,z=%3.2f]\n", j, x, y, z);
        }
    }

    // Loop through unlabeled markers
    int nOtherMarkers = 0; memcpy(&nOtherMarkers, ptr, 4); ptr += 4;
    // OtherMarker list is Deprecated
    printf("Unlabeled Markers Count : %d\n", nOtherMarkers);
    for (int j = 0; j < nOtherMarkers; j++)
    {
        float x = 0.0f; memcpy(&x, ptr, 4); ptr += 4;
        float y = 0.0f; memcpy(&y, ptr, 4); ptr += 4;
        float z = 0.0f; memcpy(&z, ptr, 4); ptr += 4;

        // Deprecated
        printf("  Marker %3.1d : [x=%3.2f,y=%3.2f,z=%3.2f]\n", j, x, y, z);
    }

    return ptr;
}


char* UnpackRigidBodyData(char* ptr, int major, int minor, void *data)
{
    memcpy(&((*((rigidbodies_t *)data)).nb), ptr, 4);

    // Loop through rigidbodies
    int nRigidBodies = 0;
    memcpy(&nRigidBodies, ptr, 4); ptr += 4;
    printf("Rigid Body Count : %3.1d\n", nRigidBodies);

    for (int j = 0; j < nRigidBodies; j++)
    {
         memcpy(&((*((rigidbodies_t *)data)).bodies[j]),ptr,8*4);

        // Rigid body position and orientation 
        int ID = 0; memcpy(&ID, ptr, 4); ptr += 4;
        float x = 0.0f; memcpy(&x, ptr, 4); ptr += 4;
        float y = 0.0f; memcpy(&y, ptr, 4); ptr += 4;
        float z = 0.0f; memcpy(&z, ptr, 4); ptr += 4;
        float qx = 0; memcpy(&qx, ptr, 4); ptr += 4;
        float qy = 0; memcpy(&qy, ptr, 4); ptr += 4;
        float qz = 0; memcpy(&qz, ptr, 4); ptr += 4;
        float qw = 0; memcpy(&qw, ptr, 4); ptr += 4;
        printf("  RB: %3.1d ID : %3.1d\n",j, ID);
        printf("    pos: [%3.2f,%3.2f,%3.2f]\n", x, y, z);
        printf("    ori: [%3.2f,%3.2f,%3.2f,%3.2f]\n", qx, qy, qz, qw);

        // Marker positions removed as redundant (since they can be derived from RB Pos/Ori plus initial offset) in NatNet 3.0 and later to optimize packet size
        if (major < 3)
        {
            // Associated marker positions
            int nRigidMarkers = 0;  memcpy(&nRigidMarkers, ptr, 4); ptr += 4;
            printf("Marker Count: %d\n", nRigidMarkers);
            int nBytes = nRigidMarkers * 3 * sizeof(float);
            float* markerData = (float*)malloc(nBytes);
            memcpy(markerData, ptr, nBytes);
            ptr += nBytes;

            // NatNet Version 2.0 and later
            if (major >= 2)
            {
                // Associated marker IDs
                nBytes = nRigidMarkers * sizeof(int);
                int* markerIDs = (int*)malloc(nBytes);
                memcpy(markerIDs, ptr, nBytes);
                ptr += nBytes;

                // Associated marker sizes
                nBytes = nRigidMarkers * sizeof(float);
                float* markerSizes = (float*)malloc(nBytes);
                memcpy(markerSizes, ptr, nBytes);
                ptr += nBytes;

                for (int k = 0; k < nRigidMarkers; k++)
                {
                    printf("  Marker %d: id=%d  size=%3.1f  pos=[%3.2f,%3.2f,%3.2f]\n",
					k, markerIDs[k], markerSizes[k],
					markerData[k * 3], markerData[k * 3 + 1], markerData[k * 3 + 2]);
                }

                if (markerIDs)
                    free(markerIDs);
                if (markerSizes)
                    free(markerSizes);

            }
            // Print marker positions for all rigid bodies
            else
            {
                int k3;
                for (int k = 0; k < nRigidMarkers; k++)
                {
                    k3 = k * 3;
                    printf("  Marker %d: pos = [%3.2f,%3.2f,%3.2f]\n",
					k, markerData[k3], markerData[k3 + 1], markerData[k3 + 2]);
                }
            }

            if (markerData)
                free(markerData);
        }

        // NatNet version 2.0 and later
        if ((major >= 2) ||(major == 0))
        {
            // Mean marker error
            float fError = 0.0f; memcpy(&fError, ptr, 4); ptr += 4;
            printf("    Mean marker err: %3.2f\n", fError);
        }

        // NatNet version 2.6 and later
        if (((major == 2) && (minor >= 6)) || (major > 2) || (major == 0))
        {
            // params
            short params = 0; memcpy(&params, ptr, 2); ptr += 2;
            bool bTrackingValid = params & 0x01; // 0x01 : rigid body was successfully tracked in this frame
            printf("    Tracking Valid: %s\n", (bTrackingValid) ? "True" : "False");
        }

    } // Go to next rigid body

    return ptr;
}


char* UnpackSkeletonData(char* ptr, int major, int minor)
{
    // Skeletons (NatNet version 2.1 and later)
    if (((major == 2) && (minor > 0)) || (major > 2))
    {
        int nSkeletons = 0;
        memcpy(&nSkeletons, ptr, 4); ptr += 4;
        printf("Skeleton Count : %d\n", nSkeletons);

        // Loop through skeletons
        for (int j = 0; j < nSkeletons; j++)
        {
            // skeleton id
            int skeletonID = 0;
            memcpy(&skeletonID, ptr, 4); ptr += 4;
            printf("  Skeleton %d ID=%d : BEGIN\n", j, skeletonID);

            // Number of rigid bodies (bones) in skeleton
            int nRigidBodies = 0;
            memcpy(&nRigidBodies, ptr, 4); ptr += 4;
            printf("  Rigid Body Count : %d\n", nRigidBodies);

            // Loop through rigid bodies (bones) in skeleton
            for (int k = 0; k < nRigidBodies; k++)
            {
                // Rigid body position and orientation
                int ID = 0; memcpy(&ID, ptr, 4); ptr += 4;
                float x = 0.0f; memcpy(&x, ptr, 4); ptr += 4;
                float y = 0.0f; memcpy(&y, ptr, 4); ptr += 4;
                float z = 0.0f; memcpy(&z, ptr, 4); ptr += 4;
                float qx = 0; memcpy(&qx, ptr, 4); ptr += 4;
                float qy = 0; memcpy(&qy, ptr, 4); ptr += 4;
                float qz = 0; memcpy(&qz, ptr, 4); ptr += 4;
                float qw = 0; memcpy(&qw, ptr, 4); ptr += 4;
                printf("    RB: %3.1d ID : %3.1d\n",k, ID);
                printf("      pos: [%3.2f,%3.2f,%3.2f]\n", x, y, z);
                printf("      ori: [%3.2f,%3.2f,%3.2f,%3.2f]\n", qx, qy, qz, qw);

                // Mean marker error (NatNet version 2.0 and later)
                if (major >= 2)
                {
                    float fError = 0.0f; memcpy(&fError, ptr, 4); ptr += 4;
                    printf("    Mean marker error: %3.2f\n", fError);
                }

                // Tracking flags (NatNet version 2.6 and later)
                if (((major == 2) && (minor >= 6)) || (major > 2) || (major == 0))
                {
                    // params
                    short params = 0; memcpy(&params, ptr, 2); ptr += 2;
                    bool bTrackingValid = params & 0x01; // 0x01 : rigid body was successfully tracked in this frame
                }
            } // next rigid body
            printf("  Skeleton %d ID=%d : END\n", j, skeletonID);

        } // next skeleton
    }

    return ptr;
}


char* UnpackLabeledMarkerData(char* ptr, int major, int minor)
{
    // labeled markers (NatNet version 2.3 and later)
// labeled markers - this includes all markers: Active, Passive, and 'unlabeled' (markers with no asset but a PointCloud ID)
    if (((major == 2) && (minor >= 3)) || (major > 2))
    {
        int nLabeledMarkers = 0;
        memcpy(&nLabeledMarkers, ptr, 4); ptr += 4;
        printf("Labeled Marker Count : %d\n", nLabeledMarkers);

        // Loop through labeled markers
        for (int j = 0; j < nLabeledMarkers; j++)
        {
            // id
            // Marker ID Scheme:
            // Active Markers:
            //   ID = ActiveID, correlates to RB ActiveLabels list
            // Passive Markers: 
            //   If Asset with Legacy Labels
            //      AssetID 	(Hi Word)
            //      MemberID	(Lo Word)
            //   Else
            //      PointCloud ID
            int ID = 0; memcpy(&ID, ptr, 4); ptr += 4;
            int modelID, markerID;
            DecodeMarkerID(ID, &modelID, &markerID);


            // x
            float x = 0.0f; memcpy(&x, ptr, 4); ptr += 4;
            // y
            float y = 0.0f; memcpy(&y, ptr, 4); ptr += 4;
            // z
            float z = 0.0f; memcpy(&z, ptr, 4); ptr += 4;
            // size
            float size = 0.0f; memcpy(&size, ptr, 4); ptr += 4;

            // NatNet version 2.6 and later
            if (((major == 2) && (minor >= 6)) || (major > 2) || (major == 0))
            {
                // marker params
                short params = 0; memcpy(&params, ptr, 2); ptr += 2;
                bool bOccluded = (params & 0x01) != 0;     // marker was not visible (occluded) in this frame
                bool bPCSolved = (params & 0x02) != 0;     // position provided by point cloud solve
                bool bModelSolved = (params & 0x04) != 0;  // position provided by model solve
                if ((major >= 3) || (major == 0))
                {
                    bool bHasModel = (params & 0x08) != 0;     // marker has an associated asset in the data stream
                    bool bUnlabeled = (params & 0x10) != 0;    // marker is 'unlabeled', but has a point cloud ID
                    bool bActiveMarker = (params & 0x20) != 0; // marker is an actively labeled LED marker
                }

            }

            // NatNet version 3.0 and later
            float residual = 0.0f;
            if ((major >= 3) || (major == 0))
            {
                // Marker residual
                memcpy(&residual, ptr, 4); ptr += 4;
            }

            printf("  ID  : [MarkerID: %d] [ModelID: %d]\n", markerID, modelID);
            printf("    pos : [%3.2f,%3.2f,%3.2f]\n", x, y, z);
            printf("    size: [%3.2f]\n", size);
            printf("    err:  [%3.2f]\n", residual);
        }
    }

    return ptr;
}


char* UnpackForcePlateData(char* ptr, int major, int minor)
{
    // Force Plate data (NatNet version 2.9 and later)
    if (((major == 2) && (minor >= 9)) || (major > 2))
    {
        int nForcePlates;
        const int kNFramesShowMax = 4;
        memcpy(&nForcePlates, ptr, 4); ptr += 4;
        printf("Force Plate Count: %d\n", nForcePlates);
        for (int iForcePlate = 0; iForcePlate < nForcePlates; iForcePlate++)
        {
            // ID
            int ID = 0; memcpy(&ID, ptr, 4); ptr += 4;

            // Channel Count
            int nChannels = 0; memcpy(&nChannels, ptr, 4); ptr += 4;

            printf("Force Plate %3.1d ID: %3.1d Num Channels: %3.1d\n", iForcePlate, ID, nChannels);

            // Channel Data
            for (int i = 0; i < nChannels; i++)
            {
                printf("  Channel %d : ", i);
                int nFrames = 0; memcpy(&nFrames, ptr, 4); ptr += 4;
                printf("  %3.1d Frames - Frame Data: ", nFrames);

                // Force plate frames
                int nFramesShow = min(nFrames, kNFramesShowMax);
                for (int j = 0; j < nFrames; j++)
                {
                    float val = 0.0f;  memcpy(&val, ptr, 4); ptr += 4;
                    if(j < nFramesShow)
                        printf("%3.2f   ", val);
                }
                if (nFramesShow < nFrames)
                {
                    printf(" showing %3.1d of %3.1d frames", nFramesShow, nFrames);
                }
                printf("\n");
            }
        }
    }

    return ptr;
}


char* UnpackDeviceData(char* ptr, int major, int minor)
{
    // Device data (NatNet version 3.0 and later)
    if (((major == 2) && (minor >= 11)) || (major > 2))
    {
        const int kNFramesShowMax = 4;
        int nDevices;
        memcpy(&nDevices, ptr, 4); ptr += 4;
        printf("Device Count: %d\n", nDevices);
        for (int iDevice = 0; iDevice < nDevices; iDevice++)
        {
            // ID
            int ID = 0; memcpy(&ID, ptr, 4); ptr += 4;

            // Channel Count
            int nChannels = 0; memcpy(&nChannels, ptr, 4); ptr += 4;

            printf("Device %3.1d      ID: %3.1d Num Channels: %3.1d\n",iDevice, ID,nChannels);

            // Channel Data
            for (int i = 0; i < nChannels; i++)
            {
                printf("  Channel %d : ", i);
                int nFrames = 0; memcpy(&nFrames, ptr, 4); ptr += 4;
                printf("  %3.1d Frames - Frame Data: ", nFrames);
                // Device frames
                int nFramesShow = min(nFrames, kNFramesShowMax);
                for (int j = 0; j < nFrames; j++)
                {
                    float val = 0.0f;  memcpy(&val, ptr, 4); ptr += 4;
                    if (j < nFramesShow)
                        printf("%3.2f   ", val);
                }
                if (nFramesShow < nFrames)
                {
                    printf(" showing %3.1d of %3.1d frames", nFramesShow, nFrames);
                }
                printf("\n");
            }
        }
    }

    return ptr;
}


char* UnpackFrameSuffixData(char* ptr, int major, int minor)
{

    // software latency (removed in version 3.0)
    if (major < 3)
    {
        float softwareLatency = 0.0f; memcpy(&softwareLatency, ptr, 4);	ptr += 4;
        printf("software latency : %3.3f\n", softwareLatency);
    }

    // timecode
    unsigned int timecode = 0; 	memcpy(&timecode, ptr, 4);	ptr += 4;
    unsigned int timecodeSub = 0; memcpy(&timecodeSub, ptr, 4); ptr += 4;
    char szTimecode[128] = "";
    TimecodeStringify(timecode, timecodeSub, szTimecode, 128);

    // timestamp
    double timestamp = 0.0f;

    // NatNet version 2.7 and later - increased from single to double precision
    if (((major == 2) && (minor >= 7)) || (major > 2))
    {
        memcpy(&timestamp, ptr, 8); ptr += 8;
    }
    else
    {
        float fTemp = 0.0f;
        memcpy(&fTemp, ptr, 4); ptr += 4;
        timestamp = (double)fTemp;
    }
    printf("Timestamp : %3.3f\n", timestamp);

    // high res timestamps (version 3.0 and later)
    if ((major >= 3) || (major == 0))
    {
        uint64_t cameraMidExposureTimestamp = 0;
        memcpy(&cameraMidExposureTimestamp, ptr, 8); ptr += 8;
        printf("Mid-exposure timestamp         : %" PRIu64"\n", cameraMidExposureTimestamp);

        uint64_t cameraDataReceivedTimestamp = 0;
        memcpy(&cameraDataReceivedTimestamp, ptr, 8); ptr += 8;
        printf("Camera data received timestamp : %" PRIu64"\n", cameraDataReceivedTimestamp);

        uint64_t transmitTimestamp = 0;
        memcpy(&transmitTimestamp, ptr, 8); ptr += 8;
        printf("Transmit timestamp             : %" PRIu64"\n", transmitTimestamp);
    }

    // frame params
    short params = 0;  memcpy(&params, ptr, 2); ptr += 2;
    bool bIsRecording = (params & 0x01) != 0;                  // 0x01 Motive is recording
    bool bTrackedModelsChanged = (params & 0x02) != 0;         // 0x02 Actively tracked model list has changed


    // end of data tag
    int eod = 0; memcpy(&eod, ptr, 4); ptr += 4;
    /*End Packet*/

    return ptr;
}

char * UnpackPacketHeader(char * ptr, int &messageID, int& nBytes, int& nBytesTotal)
{
    // First 2 Bytes is message ID
    memcpy(&messageID, ptr, 2); ptr += 2;

    // Second 2 Bytes is the size of the packet
    memcpy(&nBytes, ptr, 2); ptr += 2;
    nBytesTotal = nBytes + 4;
    return ptr;
}


// *********************************************************************
//
//  Unpack:
//      Receives pointer to bytes that represent a packet of data
//
//      There are lots of print statements that show what
//      data is being stored
//
//      Most memcpy functions will assign the data to a variable.
//      Use this variable at your descretion. 
//      Variables created for storing data do not exceed the 
//      scope of this function. 
//
// *********************************************************************
char * Unpack(char * pData)
{
}

char * MyUnpack(char * pData,int major, int minor, void *data)
{
    // Checks for NatNet Version number. Used later in function. 
    // Packets may be different depending on NatNet version.
    
//    int major = gNatNetVersion[0];
//    int minor = gNatNetVersion[1];

    char *ptr = pData;

    printf("Begin Packet\n-------\n");
    printf("NatNetVersion %d %d %d %d\n", 
        gNatNetVersion[0], gNatNetVersion[1],
        gNatNetVersion[2], gNatNetVersion[3] );


    int messageID = 0;
    int nBytes = 0;
    int nBytesTotal = 0;
    ptr = UnpackPacketHeader(ptr, messageID, nBytes, nBytesTotal);

    switch (messageID)
    {
    case NAT_FRAMEOFDATA:
        // FRAME OF MOCAP DATA packet
    {
        printf("Message ID  : %d NAT_FRAMEOFDATA\n", messageID);
        printf("Packet Size : %d\n", nBytes);
        ptr = UnpackFrameData(ptr, nBytes, major, minor, data);
    }
    break;
    default:
    {
        printf("Unrecognized Packet Type.\n");
        printf("Message ID  : %d\n", messageID);
        printf("Packet Size : %d\n", nBytes);
    }
    break;
    }
    
    printf("End Packet\n-------------\n");
    
    // check for full packet processing
    long long nBytesProcessed = (long long)ptr - (long long)pData;
    if (nBytesTotal != nBytesProcessed) {
        printf("WARNING: %d expected but %lld bytes processed\n",
            nBytesTotal, nBytesProcessed);
        if (nBytesTotal > nBytesProcessed) {
            int count = 0, countLimit = 8*25;// put on 8 byte boundary
            printf("Sample of remaining bytes:\n");
            char* ptr_start = ptr;
            int nCount = nBytesProcessed;
            char tmpChars[9] = { "        " };
            int charPos = ((long long)ptr % 8);
            char tmpChar;
            // add spaces for first row
            if (charPos > 0)
            {
                for (int i = 0; i < charPos; ++i)
                {
                    printf("   ");
                    if (i == 4)
                    {
                        printf("    ");
                    }
                }
            }
            countLimit = countLimit - (charPos+1);
            while (nCount < nBytesTotal)
            {
                tmpChar = ' ';
                if (isalnum(*ptr)) {
                    tmpChar = *ptr;
                }
                tmpChars[charPos] = tmpChar;
                printf("%2.2x ", (unsigned char)*ptr);
                ptr += 1;
                charPos = (long long)ptr % 8;
                if (charPos == 0)
                {
                    printf("    ");
                    for (int i = 0; i < 8; ++i)
                    {
                        printf("%c", tmpChars[i]);
                    }
                    printf("\n");
                }
                else if (charPos == 4)
                {
                    printf("    ");
                }
                if (++count > countLimit)
                {
                    break;
                }
                ++nCount;
            }
            if ((long long)ptr % 8)
            {
                printf("\n");
            }
        }
    }
    // return the beginning of the possible next packet
    // assuming no additional termination
    ptr = pData + nBytesTotal;
    return ptr;
}
