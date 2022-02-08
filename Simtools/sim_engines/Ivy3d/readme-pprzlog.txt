--------------------------------------------------------------------------------
1) Configuration

airframe xml file:
  <module name="flight_recorder"/>

telemetry xml file:
  <process name="FlightRecorder">
    <mode name="default">
      <message name="AUTOPILOT_VERSION"        period="11.1"/>
      <message name="DL_VALUE"                 period="1.1"/>
      <message name="ROTORCRAFT_STATUS"        period="1.2"/>
      <message name="ROTORCRAFT_FP"            period="0.25"/>
      <message name="INS_REF"                  period="5.1"/>
      <message name="ROTORCRAFT_NAV_STATUS"    period="1.6"/>
      <message name="WP_MOVED"                 period="1.3"/>
      <message name="GPS_INT"                  period=".1"/>
      <message name="INS"                      period=".1"/>
      <message name="I2C_ERRORS"               period="4.1"/>
      <message name="UART_ERRORS"              period="3.1"/>
      <message name="ENERGY"                   period="2.5"/>
      <message name="DATALINK_REPORT"          period="5.1"/>
      <message name="STATE_FILTER_STATUS"      period="3.2"/>
      <message name="AIR_DATA"                 period="1.3"/>
      <message name="SURVEY"                   period="2.5"/>
      <message name="IMU_GYRO_SCALED"          period=".075"/>
      <message name="IMU_ACCEL_SCALED"         period=".075"/>
      <message name="IMU_MAG_SCALED"           period=".2"/>
      <message name="LIDAR"                    period="0.05"/>
    </mode>
  </process>

--------------------------------------------------------------------------------
2) Recording

on ground:
  20_12_08__09_18_56.data
  20_12_08__09_18_56.log

on board:
  FLIGHT_RECORDER / fr_0001.LOG


--------------------------------------------------------------------------------
3) Postprocessing onboard logs

paparazzi/sw/logalizer/sd2log ./fr_0001.LOG
=> paparazzi/var/logs/
  20_12_08__09_36_27_SD_no_GPS.data
  20_12_08__09_36_27_SD_no_GPS.log
  20_12_08__09_36_27_SD_no_GPS.tlm


--------------------------------------------------------------------------------
4) Displaying

paparazzi/sw/logalizer/logplotter ./record/onground/20_12_08__09_18_56.log
paparazzi/sw/logalizer/logplotter ./postproc/20_12_08__09_36_27_SD_no_GPS.log

paparazzi/sw/logalizer/play ./record/onground/20_12_08__09_18_56.log
paparazzi/sw/logalizer/play ./postproc/20_12_08__09_36_27_SD_no_GPS.log

=> 
  Paparazzi replay sent  'replay116 ROTORCRAFT_FP -378 -248 7 -5242 0 -5242 -305 139 34 0 0 7 34 0 0'
  Paparazzi replay sent  'time116 13.916000'
