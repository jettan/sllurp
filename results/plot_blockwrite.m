clear
close all;

% Time of experiments (seconds).
t = 10;

% Read CSV files.
xdata = [1:32];
d2 = csvread('blockwrite/20cm/result.csv',1);
r2 = reshape(d2,5,32,6);
d2 = mean(r2);

d3 = csvread('blockwrite/30cm/result.csv',1);
r3 = reshape(d3,5,32,6);
d3 = mean(r3);

d4 = csvread('blockwrite/40cm/result.csv',1);
r4 = reshape(d4,5,32,6);
d4 = mean(r4);

d5 = csvread('blockwrite/50cm/result.csv',1);
r5 = reshape(d5,5,32,6);
d5 = mean(r5);

d6 = csvread('blockwrite/60cm/result.csv',1);
r6 = reshape(d6,5,32,6);
d6 = mean(r6);

% Setup figure properties.
fontSize = 10;
fontSizeAxes = 8;
fontWeight = 'normal';
figurePosition = [440 378 370 300];   % [x y width height]


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plot figures based on log data.

% Plot number of OPS
hFig = figure(1);
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');


s = 6; % Number of OPS.
yLabelName = 'Number of OPS (\psi)';


hold on;
scatter (xdata,d2(:,:,s),'x');
scatter (xdata,d3(:,:,s),'+')
scatter (xdata,d4(:,:,s),'filled','s')
scatter (xdata,d5(:,:,s),'filled','v')
scatter (xdata,d6(:,:,s),'*')
hold off


legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

%%%%%%%%%%%%%%%%%

% Efficiency
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');


s = 4; % Efficiency
yLabelName = 'Efficiency (\eta)';

hold on;
scatter (xdata,d2(:,:,s),'x');
scatter (xdata,d3(:,:,s),'+')
scatter (xdata,d4(:,:,s),'filled','s')
scatter (xdata,d5(:,:,s),'filled','v')
scatter (xdata,d6(:,:,s),'*')

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;

%%%%%%%%%%%%%%%%%

% Plot Throughput
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

hold on
s = 5; % Throughput
yLabelName = 'Throughput (\theta) [B/sec]';

scatter (xdata,d2(:,:,s),'x');
scatter (xdata,d3(:,:,s),'+')
scatter (xdata,d4(:,:,s),'filled','s')
scatter (xdata,d5(:,:,s),'filled','v')
scatter (xdata,d6(:,:,s),'*')

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
set(gca,'ylim', [0 inf]);
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;


%%%%%%%%%%%%%%%%%%%

% Plot total operations
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

hold on
s = 2; % Throughput
yLabelName = 'Total OPS';

tot2 = d2(:,:,s)./t;
tot3 = d3(:,:,s)./t;
tot4 = d4(:,:,s)./t;
tot5 = d5(:,:,s)./t;
tot6 = d6(:,:,s)./t;

scatter (xdata,tot2,'x');
scatter (xdata,tot3,'+')
scatter (xdata,tot4,'filled','s')
scatter (xdata,tot5,'filled','v')
scatter (xdata,tot6,'*')

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
set(gca,'ylim',[0 inf]);
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Now try to get some analytical solutions running.
% Use least square approach to get f2(x) = b2 + a2/x and g(x) = ax+b

% f2(x)
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
yLabelName = 'f2(x)';

x0 = [0, 1];
hold on

F2 = @(x,xdata)x(1)./(xdata)+x(2);
[X2,resnorm] = lsqcurvefit(F2,x0,xdata,tot2)
plot(xdata,F2(X2,xdata))

F3 = @(x,xdata)x(1)./(xdata)+x(2);
[X3,resnorm] = lsqcurvefit(F3,x0,xdata,tot3)
plot(xdata,F3(X3,xdata))

F4 = @(x,xdata)x(1)./(xdata)+x(2);
[X4,resnorm] = lsqcurvefit(F4,x0,xdata,tot4)
plot(xdata,F4(X4,xdata))

F5 = @(x,xdata)x(1)./(xdata)+x(2);
[X5,resnorm] = lsqcurvefit(F5,x0,xdata,tot5)
plot(xdata,F5(X5,xdata))

F6 = @(x,xdata)x(1)./(xdata)+x(2);
[X6,resnorm] = lsqcurvefit(F6,x0,xdata,tot6)
plot(xdata,F6(X6,xdata))

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,0,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

hold off;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Efficiency curve fitting shenanigans.
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
s = 4;
yLabelName = 'g(x)';

x0 = [0, 1];
hold on

ydata = d2(:,:,s);
F2 = @(x,xdata)-x(1)*xdata+x(2);
[x2,resnorm] = lsqcurvefit(F2,x0,xdata,ydata)
plot(xdata,F2(x2,xdata))

ydata = d3(:,:,s);
F3 = @(x,xdata)-x(1)*xdata+x(2);
[x3,resnorm] = lsqcurvefit(F3,x0,xdata,ydata)
plot(xdata,F3(x3,xdata))

ydata = d4(:,:,s);
F4 = @(x,xdata)-x(1)*xdata+x(2);
[x4,resnorm] = lsqcurvefit(F4,x0,xdata,ydata)
plot(xdata,F4(x4,xdata))

ydata = d5(:,:,s);
F5 = @(x,xdata)-x(1)*xdata+x(2);
[x5,resnorm] = lsqcurvefit(F5,x0,xdata,ydata)
plot(xdata,F5(x5,xdata))

ydata = d6(:,:,s);
F6 = @(x,xdata)-x(1)*xdata+x(2);
[x6,resnorm] = lsqcurvefit(F6,x0,[1:18],ydata(1:18))
plot([1:18],F6(x6,[1:18]))

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

hold off;

% Now plot f1(x) based on the found values.

cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
yLabelName = 'f1(x)';
hold on

f12 = ((-x2(1)*xdata + x2(2)).*(X2(2)*xdata + X2(1)))./xdata;
f13 = ((-x3(1)*xdata + x3(2)).*(X3(2)*xdata + X3(1)))./xdata;
f14 = ((-x4(1)*xdata + x4(2)).*(X4(2)*xdata + X4(1)))./xdata;
f15 = ((-x5(1)*xdata + x5(2)).*(X5(2)*xdata + X5(1)))./xdata;
f16 = ((-x6(1)*xdata + x6(2)).*(X6(2)*xdata + X6(1)))./xdata;

plot(xdata, f12);
plot(xdata, f13);
plot(xdata, f14);
plot(xdata, f15);
plot(xdata, f16);

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,0,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

hold off;

% And finally plot throughput: h(x) = f1(x)*x

cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
yLabelName = 'h(x)';
hold on

T2 = ((-x2(1)*xdata + x2(2)).*(X2(2)*xdata + X2(1)));
T3 = ((-x3(1)*xdata + x3(2)).*(X3(2)*xdata + X3(1)));
T4 = ((-x4(1)*xdata + x4(2)).*(X4(2)*xdata + X4(1)));
T5 = ((-x5(1)*xdata + x5(2)).*(X5(2)*xdata + X5(1)));
T6 = ((-x6(1)*xdata + x6(2)).*(X6(2)*xdata + X6(1)));

plot(xdata, T2);
plot(xdata, T3);
plot(xdata, T4);
plot(xdata, T5);
plot(xdata, T6);

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,0,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

hold off;