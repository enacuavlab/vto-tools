#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string>

#include <NatNetTypes.h>
#include <NatNetCAPI.h>
#include <NatNetClient.h>

#include <mutex>
#include <Ivy/ivy.h>

void NATNET_CALLCONV DataHandler(sFrameOfMocapData* data, void* pUserData);
NatNetClient* g_pClient = NULL;
sNatNetClientConnectParams g_connectParams;
int g_analogSamplesPerMocapFrame = 0;
sServerDescription g_serverDescription;


///home/pprz/Projects/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py  -ac 114 114  -s 192.168.1.230 -f 10
//
// export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{insert lib folder directory here}
// ./natnetunicast 884
/*

LD_LIBRARY_PATH="/home/pprz/Projects/vto-tools/Natnet/SDK4-CPP/lib" \
/home/pprz/Projects/vto-tools/Natnet/SDK4-CPP/samples/SampleClient/build/natnetunicast2ivy 884

*/

static pthread_mutex_t data_mutex; // mutex for ivy send
struct data_t {
  int ac;
  double x;
  double y;
  double z;
  double qx;
  double qy;
  double qz;
  double qw;
} data_ivy,data_mocap;

void ivysnd() {

  pthread_mutex_lock(&data_mutex);
  memcpy(&data_ivy, &data_mocap, sizeof(data_t));
  pthread_mutex_unlock(&data_mutex);
  IvySendMsg("%d REMOTE_GPS_LOCAL %f %f %f %f %f %f %f", 
    data_ivy.ac,data_ivy.x,data_ivy.y,data_ivy.z,data_ivy.qx,data_ivy.qy,data_ivy.qz,data_ivy.qw);

/*
  IvySendMsg("%d NPS_SENSORS_SCALED %f %f %f %f %f %f",

             msg = PprzMessage("datalink", "REMOTE_GPS_LOCAL")
            msg['ac_id'] = id_dict[i]
            msg['pad'] = 0
            msg['enu_x'] = pos[0]
            msg['enu_y'] = pos[1]
            msg['enu_z'] = pos[2]
            msg['enu_xd'] = vel[0]
            msg['enu_yd'] = vel[1]
            msg['enu_zd'] = vel[2]
            msg['tow'] = int(1000. * stamp) # TODO convert to GPS itow ?
            # convert quaternion to psi euler angle
            dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
            dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
            msg['course'] = 180. * np.arctan2(dcm_1_0, dcm_0_0) / 3.14
            ivy.send(msg)
*/
}


int main( int argc, char* argv[] )
{

  std::string y="127.255.255.255";
  const char *ivy_bus=y.c_str();
  IvyInit ("natnetunicast2ivy", "natnetunicast2ivy READY", NULL, NULL, NULL, NULL);
  IvyStart(ivy_bus);

  int ac_id=atoi(argv[1]);

  g_pClient = new NatNetClient();
  g_pClient->SetFrameReceivedCallback( DataHandler, g_pClient );

  g_connectParams.serverAddress = "192.168.1.231";
  g_connectParams.connectionType = ConnectionType_Unicast;

  g_pClient->Disconnect();
  ErrorCode retCode = g_pClient->Connect( g_connectParams );
  if (retCode != ErrorCode_OK)
  {
    printf("Unable to connect to server.  Error code: %d. Exiting.\n", retCode);
    return 1;
  }

  memset( &g_serverDescription, 0, sizeof( g_serverDescription ) );
  retCode = g_pClient->GetServerDescription( &g_serverDescription );
  if ( retCode != ErrorCode_OK || ! g_serverDescription.HostPresent )
  {
    printf("Unable to connect to server. Host not present. Exiting.\n");
    return 1;
  }
  printf("Application: %s (ver. %d.%d.%d.%d)\n", g_serverDescription.szHostApp, g_serverDescription.HostAppVersion[0],
    g_serverDescription.HostAppVersion[1], g_serverDescription.HostAppVersion[2], g_serverDescription.HostAppVersion[3]);
  printf("NatNet Version: %d.%d.%d.%d\n", g_serverDescription.NatNetVersion[0], g_serverDescription.NatNetVersion[1],
    g_serverDescription.NatNetVersion[2], g_serverDescription.NatNetVersion[3]);
    printf("Server IP:%s\n", g_connectParams.serverAddress );

  void* response;
  int nBytes;

  sleep(1);
  g_pClient->SendMessageAndWait("SubscribeToData,AllTypes,None", &response, &nBytes);
  sleep(1);

  std::string x="SubscribeByID,RigidBody,"+std::to_string(ac_id);
  const char *cmd=x.c_str();
  g_pClient->SendMessageAndWait(cmd, &response, &nBytes);

  sleep(1);
  g_pClient->SendMessageAndWait("Disconnect", &response, &nBytes);

  while (true) {
    usleep(1);
  }
}


// DataHandler receives data from the server
// This function is called by NatNet when a frame of mocap data is available
void NATNET_CALLCONV DataHandler(sFrameOfMocapData* data, void* pUserData)
{
    NatNetClient* pClient = (NatNetClient*) pUserData;

    // Software latency here is defined as the span of time between:
    //   a) The reception of a complete group of 2D frames from the camera system (CameraDataReceivedTimestamp)
    // and
    //   b) The time immediately prior to the NatNet frame being transmitted over the network (TransmitTimestamp)
    //
    // This figure may appear slightly higher than the "software latency" reported in the Motive user interface,
    // because it additionally includes the time spent preparing to stream the data via NatNet.
    const uint64_t softwareLatencyHostTicks = data->TransmitTimestamp - data->CameraDataReceivedTimestamp;
    const double softwareLatencyMillisec = (softwareLatencyHostTicks * 1000) / static_cast<double>(g_serverDescription.HighResClockFrequency);

    // Transit latency is defined as the span of time between Motive transmitting the frame of data, and its reception by the client (now).
    // The SecondsSinceHostTimestamp method relies on NatNetClient's internal clock synchronization with the server using Cristian's algorithm.
    const double transitLatencyMillisec = pClient->SecondsSinceHostTimestamp( data->TransmitTimestamp ) * 1000.0;
    
    int i=0;
    printf("FrameID : %d\n", data->iFrame);
    printf("Timestamp : %3.2lf\n", data->fTimestamp);
    printf("Software latency : %.2lf milliseconds\n", softwareLatencyMillisec);

    // Only recent versions of the Motive software in combination with ethernet camera systems support system latency measurement.
    // If it's unavailable (for example, with USB camera systems, or during playback), this field will be zero.
    const bool bSystemLatencyAvailable = data->CameraMidExposureTimestamp != 0;

    if ( bSystemLatencyAvailable )
    {
        // System latency here is defined as the span of time between:
        //   a) The midpoint of the camera exposure window, and therefore the average age of the photons (CameraMidExposureTimestamp)
        // and
        //   b) The time immediately prior to the NatNet frame being transmitted over the network (TransmitTimestamp)
        const uint64_t systemLatencyHostTicks = data->TransmitTimestamp - data->CameraMidExposureTimestamp;
        const double systemLatencyMillisec = (systemLatencyHostTicks * 1000) / static_cast<double>(g_serverDescription.HighResClockFrequency);

        // Client latency is defined as the sum of system latency and the transit time taken to relay the data to the NatNet client.
        // This is the all-inclusive measurement (photons to client processing).
        const double clientLatencyMillisec = pClient->SecondsSinceHostTimestamp( data->CameraMidExposureTimestamp ) * 1000.0;

        // You could equivalently do the following (not accounting for time elapsed since we calculated transit latency above):
        //const double clientLatencyMillisec = systemLatencyMillisec + transitLatencyMillisec;

        printf( "System latency : %.2lf milliseconds\n", systemLatencyMillisec );
        printf( "Total client latency : %.2lf milliseconds (transit time +%.2lf ms)\n", clientLatencyMillisec, transitLatencyMillisec );
    }
    else
    {
        printf( "Transit latency : %.2lf milliseconds\n", transitLatencyMillisec );
    }

    // FrameOfMocapData params
    bool bIsRecording = ((data->params & 0x01)!=0);
    bool bTrackedModelsChanged = ((data->params & 0x02)!=0);
    if(bIsRecording)
        printf("RECORDING\n");
    if(bTrackedModelsChanged)
        printf("Models Changed.\n");
	

    // timecode - for systems with an eSync and SMPTE timecode generator - decode to values
	int hour, minute, second, frame, subframe;
    NatNet_DecodeTimecode( data->Timecode, data->TimecodeSubframe, &hour, &minute, &second, &frame, &subframe );
	// decode to friendly string
	char szTimecode[128] = "";
    NatNet_TimecodeStringify( data->Timecode, data->TimecodeSubframe, szTimecode, 128 );
	printf("Timecode : %s\n", szTimecode);

	// Rigid Bodies
	printf("Rigid Bodies [Count=%d]\n", data->nRigidBodies);
	for(i=0; i < data->nRigidBodies; i++)
	{
        // params
        // 0x01 : bool, rigid body was successfully tracked in this frame
        bool bTrackingValid = data->RigidBodies[i].params & 0x01;

		printf("Rigid Body [ID=%d  Error=%3.2f  Valid=%d]\n", data->RigidBodies[i].ID, data->RigidBodies[i].MeanError, bTrackingValid);
		printf("\tx\ty\tz\tqx\tqy\tqz\tqw\n");
		printf("\t%3.2f\t%3.2f\t%3.2f\t%3.2f\t%3.2f\t%3.2f\t%3.2f\n",
			data->RigidBodies[i].x,
			data->RigidBodies[i].y,
			data->RigidBodies[i].z,
			data->RigidBodies[i].qx,
			data->RigidBodies[i].qy,
			data->RigidBodies[i].qz,
			data->RigidBodies[i].qw);

                pthread_mutex_lock(&data_mutex);
		data_mocap.ac=data->RigidBodies[i].ID;
		data_mocap.x=data->RigidBodies[i].x;
		data_mocap.y=data->RigidBodies[i].y;
		data_mocap.z=data->RigidBodies[i].z;
		data_mocap.qx=data->RigidBodies[i].qx;
		data_mocap.qy=data->RigidBodies[i].qy;
		data_mocap.qz=data->RigidBodies[i].qz;
		data_mocap.qw=data->RigidBodies[i].qw;
                pthread_mutex_unlock(&data_mutex);
	}

	// Skeletons
	printf("Skeletons [Count=%d]\n", data->nSkeletons);
	for(i=0; i < data->nSkeletons; i++)
	{
		sSkeletonData skData = data->Skeletons[i];
		printf("Skeleton [ID=%d  Bone count=%d]\n", skData.skeletonID, skData.nRigidBodies);
		for(int j=0; j< skData.nRigidBodies; j++)
		{
			sRigidBodyData rbData = skData.RigidBodyData[j];
			printf("Bone %d\t%3.2f\t%3.2f\t%3.2f\t%3.2f\t%3.2f\t%3.2f\t%3.2f\n",
				rbData.ID, rbData.x, rbData.y, rbData.z, rbData.qx, rbData.qy, rbData.qz, rbData.qw );
		}
	}

	// labeled markers - this includes all markers (Active, Passive, and 'unlabeled' (markers with no asset but a PointCloud ID)
    bool bOccluded;     // marker was not visible (occluded) in this frame
    bool bPCSolved;     // reported position provided by point cloud solve
    bool bModelSolved;  // reported position provided by model solve
    bool bHasModel;     // marker has an associated asset in the data stream
    bool bUnlabeled;    // marker is 'unlabeled', but has a point cloud ID that matches Motive PointCloud ID (In Motive 3D View)
	bool bActiveMarker; // marker is an actively labeled LED marker

	printf("Markers [Count=%d]\n", data->nLabeledMarkers);
	for(i=0; i < data->nLabeledMarkers; i++)
	{
        bOccluded = ((data->LabeledMarkers[i].params & 0x01)!=0);
        bPCSolved = ((data->LabeledMarkers[i].params & 0x02)!=0);
        bModelSolved = ((data->LabeledMarkers[i].params & 0x04) != 0);
        bHasModel = ((data->LabeledMarkers[i].params & 0x08) != 0);
        bUnlabeled = ((data->LabeledMarkers[i].params & 0x10) != 0);
		bActiveMarker = ((data->LabeledMarkers[i].params & 0x20) != 0);

        sMarker marker = data->LabeledMarkers[i];

        // Marker ID Scheme:
        // Active Markers:
        //   ID = ActiveID, correlates to RB ActiveLabels list
        // Passive Markers: 
        //   If Asset with Legacy Labels
        //      AssetID 	(Hi Word)
        //      MemberID	(Lo Word)
        //   Else
        //      PointCloud ID
        int modelID, markerID;
        NatNet_DecodeID( marker.ID, &modelID, &markerID );
		
        char szMarkerType[512];
        if (bActiveMarker)
            strcpy(szMarkerType, "Active");
        else if(bUnlabeled)
            strcpy(szMarkerType, "Unlabeled");
        else
            strcpy(szMarkerType, "Labeled");

        printf("%s Marker [ModelID=%d, MarkerID=%d] [size=%3.2f] [pos=%3.2f,%3.2f,%3.2f]\n",
            szMarkerType, modelID, markerID, marker.size, marker.x, marker.y, marker.z);
	}

    // force plates
    printf("Force Plate [Count=%d]\n", data->nForcePlates);
    for(int iPlate=0; iPlate < data->nForcePlates; iPlate++)
    {
        printf("Force Plate %d\n", data->ForcePlates[iPlate].ID);
        for(int iChannel=0; iChannel < data->ForcePlates[iPlate].nChannels; iChannel++)
        {
            printf("\tChannel %d:\t", iChannel);
            if(data->ForcePlates[iPlate].ChannelData[iChannel].nFrames == 0)
            {
                printf("\tEmpty Frame\n");
            }
            else if(data->ForcePlates[iPlate].ChannelData[iChannel].nFrames != g_analogSamplesPerMocapFrame)
            {
                printf("\tPartial Frame [Expected:%d   Actual:%d]\n", g_analogSamplesPerMocapFrame, data->ForcePlates[iPlate].ChannelData[iChannel].nFrames);
            }
            for(int iSample=0; iSample < data->ForcePlates[iPlate].ChannelData[iChannel].nFrames; iSample++)
                printf("%3.2f\t", data->ForcePlates[iPlate].ChannelData[iChannel].Values[iSample]);
            printf("\n");
        }
    }

    // devices
    printf("Device [Count=%d]\n", data->nDevices);
    for (int iDevice = 0; iDevice < data->nDevices; iDevice++)
    {
        printf("Device %d\n", data->Devices[iDevice].ID);
        for (int iChannel = 0; iChannel < data->Devices[iDevice].nChannels; iChannel++)
        {
            printf("\tChannel %d:\t", iChannel);
            if (data->Devices[iDevice].ChannelData[iChannel].nFrames == 0)
            {
                printf("\tEmpty Frame\n");
            }
            else if (data->Devices[iDevice].ChannelData[iChannel].nFrames != g_analogSamplesPerMocapFrame)
            {
                printf("\tPartial Frame [Expected:%d   Actual:%d]\n", g_analogSamplesPerMocapFrame, data->Devices[iDevice].ChannelData[iChannel].nFrames);
            }
            for (int iSample = 0; iSample < data->Devices[iDevice].ChannelData[iChannel].nFrames; iSample++)
                printf("%3.2f\t", data->Devices[iDevice].ChannelData[iChannel].Values[iSample]);
            printf("\n");
        }
    }
}
