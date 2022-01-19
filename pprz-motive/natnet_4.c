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
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>


#define MAX_NAMELENGTH 256
#define NAT_FRAMEOFDATA 7

#define min(x, y) (((x) < (y)) ? (x) : (y))


// SAME STRUCTURE AS MAIN
#define MAX_BODIES  6
struct rigidbody_t {
  bool val;
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


char * MyUnpack(char * pPacketIn,int major,int minor,void *data);
char * UnpackFrameData(char* inptr, int nBytes, void *data);
char * UnpackMarkersetData(char * ptr);
char * UnpackRigidBodyData(char * ptr, void *data);
char * UnpackSkeletonData(char * ptr);
char * UnpackLabeledMarkerData(char* ptr);
char * UnpackForcePlateData(char * ptr);
char * UnpackDeviceData(char * ptr);
char * UnpackFrameSuffixData(char * ptr);


char * UnpackFrameData(char * inptr, int nBytes, void *data)
{
    char * ptr = inptr;
    memcpy(&((*((struct rigidbodies_t *)data)).fr), ptr, 4); ptr += 4; // Frame number
    ptr = UnpackMarkersetData(ptr);
    ptr = UnpackRigidBodyData(ptr, data);
    ptr = UnpackSkeletonData(ptr);
    ptr = UnpackLabeledMarkerData(ptr);
    ptr = UnpackForcePlateData(ptr);
    ptr = UnpackDeviceData(ptr);
    ptr = UnpackFrameSuffixData(ptr);
    return ptr;
}


char* UnpackMarkersetData(char* ptr)
{
  int nMarkerSets = 0; memcpy(&nMarkerSets, ptr, 4); ptr += 4;
  for (int i = 0; i < nMarkerSets; i++) {
    char szName[MAX_NAMELENGTH];
    strcpy(szName, ptr);
    int nDataBytes = (int)strlen(szName) + 1;
    ptr += nDataBytes;
    int nMarkers = 0; memcpy(&nMarkers, ptr, 4); ptr += 4;
    ptr += nMarkers*4*3;
  }
  int nOtherMarkers = 0; memcpy(&nOtherMarkers, ptr, 4); ptr += 4;
  ptr += nOtherMarkers*4*3;
  return ptr;
}


char* UnpackRigidBodyData(char* ptr, void *data)
{
  memcpy(&((*((struct rigidbodies_t *)data)).nb), ptr, 4);
  int nRigidBodies = 0;
  memcpy(&nRigidBodies, ptr, 4); ptr += 4;
  for (int j = 0; j < nRigidBodies; j++) {
    struct rigidbody_t *tmp = &((*((struct rigidbodies_t *)data)).bodies[j]);
    memcpy(&(tmp->id),ptr,4); ptr += 4;
    memcpy(&(tmp->pos),ptr,3*4); ptr += 3*4;
    memcpy(&(tmp->ori),ptr,4*4); ptr += 4*4;
    ptr += 4; // Mean marker error
    short params = 0; memcpy(&params, ptr, 2); ptr += 2;
    bool bTrackingValid = params & 0x01;
    memcpy(&(tmp->val),&bTrackingValid,1);
  } 
  return ptr;
}


char* UnpackSkeletonData(char* ptr)
{
  int nSkeletons = 0;
  memcpy(&nSkeletons, ptr, 4); ptr += 4;
  for (int j = 0; j < nSkeletons; j++) {
    int skeletonID = 0;
    memcpy(&skeletonID, ptr, 4); ptr += 4;
    int nRigidBodies = 0;
    memcpy(&nRigidBodies, ptr, 4); ptr += 4;
    ptr += (38*nRigidBodies);
  }
  return ptr;
}


char* UnpackLabeledMarkerData(char* ptr)
{
  int nLabeledMarkers = 0;
  memcpy(&nLabeledMarkers, ptr, 4); ptr += 4;
  ptr += nLabeledMarkers * 26 ;
  return ptr;
}


char* UnpackForcePlateData(char* ptr)
{
  int nForcePlates;
  const int kNFramesShowMax = 4;
  memcpy(&nForcePlates, ptr, 4); ptr += 4;
  for (int iForcePlate = 0; iForcePlate < nForcePlates; iForcePlate++) {
    ptr += 4;
    int nChannels = 0; memcpy(&nChannels, ptr, 4); ptr += 4;
    for (int i = 0; i < nChannels; i++) {
      int nFrames = 0; memcpy(&nFrames, ptr, 4); ptr += 4;
      int nFramesShow = min(nFrames, kNFramesShowMax);
      ptr += 4*nFrames;
    }
  }
  return ptr;
}


char* UnpackDeviceData(char* ptr)
{
  const int kNFramesShowMax = 4;
  int nDevices;
  memcpy(&nDevices, ptr, 4); ptr += 4;
  for (int iDevice = 0; iDevice < nDevices; iDevice++) {
    ptr += 4;
    int nChannels = 0; memcpy(&nChannels, ptr, 4); ptr += 4;
    for (int i = 0; i < nChannels; i++) {
      int nFrames = 0; memcpy(&nFrames, ptr, 4); ptr += 4;
      int nFramesShow = min(nFrames, kNFramesShowMax);
      ptr  += 4*nFrames;
    }
  }
  return ptr;
}


char* UnpackFrameSuffixData(char* ptr)
{
  ptr += 8;
  double timestamp = 0.0f;
  memcpy(&timestamp, ptr, 8); ptr += 8;
  //printf("Timestamp : %3.3f\n", timestamp);
  ptr += 30;
  return ptr;
}


char * MyUnpack(char * pData,int major, int minor, void *data)
{
    char *ptr = pData;

    int messageID = 0;
    int nBytes = 0;
    int nBytesTotal = 0;

    // First 2 Bytes is message ID
    memcpy(&messageID, ptr, 2); ptr += 2;

    // Second 2 Bytes is the size of the packet
    memcpy(&nBytes, ptr, 2); ptr += 2;
    nBytesTotal = nBytes + 4;

    if (messageID == NAT_FRAMEOFDATA) ptr = UnpackFrameData(ptr, nBytes, data);
    
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
