%
% Boucle de commande d'un quadcopter
%           Mineur Drones 2019
% Condomines Jean-Philippe - Hattenberger Gautier
%            

%% Matlab/PPRZ/Optitrack
%Data acquisition

%Positions
pos_new=squeeze(position.signals.values)';
time_pos = position.time;
x=pos_new(:,1);
y=pos_new(:,2);
z=pos_new(:,3);
% Test plot3(x,y,z);

%Angles
angles_new=squeeze(angles.signals.values)';
phi=angles_new(:,1);
theta=angles_new(:,2);
psi=angles_new(:,3);

%Commande
time_com=c_roll.time;
cc_roll=c_roll.signals.values;
cc_pitch=c_pitch.signals.values;
cc_yaw=c_yaw.signals.values;
cc_throttle=throttle.signals.values;

%Plots

plot(throttle.time,(-throttle.signals.values+9600)/2)
%plot(rad2deg(th_roll/9600))




% Caution %
%Save Workspace in file ".mat" 
%save 'dataBebop_520.mat'
%
%save 'dataBebop_623.mat'
%
%save 'dataBebop_720.mat'
%
%save 'dataBebop_823.mat'




