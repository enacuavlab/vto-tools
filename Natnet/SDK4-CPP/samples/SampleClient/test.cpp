#include <stdio.h>
#include <unistd.h>

#include <NatNetCAPI.h>
#include <NatNetClient.h>

/*
This program gets data from Motive Server v3, with following settins:
Local Interface : 192.168.1.231
Transmission Type : Multicast
Labeled Markers : On
Unlabeled Markers : On
Asset Markers : On
Rigid Bodies : On
...
Command Port : 1510
Data Port : 1511
Multicast Interface : 239.255.42.99
*/

/*
make clean;make build/test

LD_LIBRARY_PATH="/home/pprz/Projects/vto-tools/Natnet/SDK4-CPP/lib" ./build/test
*/

void NATNET_CALLCONV DataHandler(sFrameOfMocapData* data, void* pUserData);
NatNetClient* g_pClient = NULL;
sNatNetClientConnectParams g_connectParams;

int main ()
{
  printf("IN");
  g_pClient = new NatNetClient();
  g_pClient->SetFrameReceivedCallback( DataHandler, g_pClient );
  g_connectParams.serverAddress = "192.168.1.231";

  g_connectParams.connectionType = ConnectionType_Multicast;
//  g_connectParams.connectionType = ConnectionType_Unicast;

  g_pClient->Disconnect();
  ErrorCode retCode = g_pClient->Connect( g_connectParams );
  if (retCode != ErrorCode_OK)
  {
    printf("Unable to connect to server.  Error code: %d. Exiting.\n", retCode);
    return 1;
  }
  while (true) {
    usleep(1);
  }
}

void NATNET_CALLCONV DataHandler(sFrameOfMocapData* data, void* pUserData)
{
/*
  printf("Rigid Bodies [Count=%d]\n", data->nRigidBodies); 
  for(int i=0; i < data->nRigidBodies; i++) {
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
  }
*/
  bool bOccluded;     // marker was not visible (occluded) in this frame
  bool bPCSolved;     // reported position provided by point cloud solve
  bool bModelSolved;  // reported position provided by model solve
  bool bHasModel;     // marker has an associated asset in the data stream
  bool bUnlabeled;    // marker is 'unlabeled', but has a point cloud ID that matches Motive PointCloud ID (In Motive 3D View)
  bool bActiveMarker; // marker is an actively labeled LED marker

  printf("Markers [Count=%d]\n", data->nLabeledMarkers);
  for(int i=0; i < data->nLabeledMarkers; i++) {
    bOccluded = ((data->LabeledMarkers[i].params & 0x01)!=0); 
    bPCSolved = ((data->LabeledMarkers[i].params & 0x02)!=0);
    bModelSolved = ((data->LabeledMarkers[i].params & 0x04) != 0);
    bHasModel = ((data->LabeledMarkers[i].params & 0x08) != 0);
    bUnlabeled = ((data->LabeledMarkers[i].params & 0x10) != 0);
    bActiveMarker = ((data->LabeledMarkers[i].params & 0x20) != 0);

    sMarker marker = data->LabeledMarkers[i];
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
}
