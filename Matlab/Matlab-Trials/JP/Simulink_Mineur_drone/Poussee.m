%Trace de ft(mg)
clear all
load('dataBebop_520');
th1 = (-throttle.signals.values+9600)/2;
load('dataBebop_623');
th2 = (-throttle.signals.values+9600)/2;
load('dataBebop_720');
th3 = (-throttle.signals.values+9600)/2;
load('dataBebop_823');
th4 = (-throttle.signals.values+9600)/2;

th11=mean(th1(3e4:7e4));
th22=mean(th2(3e4:7e4));
th33=mean(th3(3e4:7e4));
th44=mean(th4(3e4:7e4));

m=[520 623 720 823];

plot(th1)
hold on
plot(th2)
hold on
plot(th3)
hold on
plot(th4)
