!synclient HorizTwoFingerScroll=0

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
% f2(x) = b2 + a2/x^c

cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
yLabelName = 'f2(x)';

x0 = [170, 0,-30];
f2 = @(x,xdata)x(1)./(xdata.^x(2))+x(3);
hold on

optimoptions(@lsqcurvefit,'Algorithm','levenberg-marquardt','MaxFunEvals',1500);

[X2,resnorm] = lsqcurvefit(f2,x0,xdata,tot2)
[X3,resnorm] = lsqcurvefit(f2,x0,xdata,tot3)
[X4,resnorm] = lsqcurvefit(f2,x0,xdata,tot4)
[X5,resnorm] = lsqcurvefit(f2,x0,xdata,tot5)
[X6,resnorm] = lsqcurvefit(f2,x0,xdata,tot6)

plot(xdata,f2(X2,xdata))
plot(xdata,f2(X3,xdata))
plot(xdata,f2(X4,xdata))
plot(xdata,f2(X5,xdata))
plot(xdata,f2(X6,xdata))

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
set(gca, 'xlim',[0 32]);
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
G = @(x,xdata)-x(1)*xdata+x(2);

hold on

[x2,resnorm] = lsqcurvefit(G,x0,xdata,d2(:,:,s))
[x3,resnorm] = lsqcurvefit(G,x0,xdata,d3(:,:,s))
[x4,resnorm] = lsqcurvefit(G,x0,xdata,d4(:,:,s))
[x5,resnorm] = lsqcurvefit(G,x0,xdata,d5(:,:,s))
[x6,resnorm] = lsqcurvefit(G,x0,xdata(1:19),d6(:,1:19,s))

plot(xdata,G(x2,xdata))
plot(xdata,G(x3,xdata))
plot(xdata,G(x4,xdata))
plot(xdata,G(x5,xdata))
plot(xdata(1:19),G(x6,xdata(1:19)))

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

f1 = @(e,t,xdata)(-e(1)*xdata+e(2)).*(t(1)./(xdata.^t(2))+t(3));

plot(xdata,f1(x2,X2,xdata))
plot(xdata,f1(x3,X3,xdata))
plot(xdata,f1(x4,X4,xdata))
plot(xdata,f1(x5,X5,xdata))
plot(xdata,f1(x6,X6,xdata))

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

% Plot h(x).

cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
yLabelName = 'h(x)';
hold on

T = @(e,t,xdata)((-e(1)*xdata+e(2)).*(t(1)./(xdata.^t(2))+t(3))).*xdata*2;

plot(xdata,T(x2,X2,xdata))
plot(xdata,T(x3,X3,xdata))
plot(xdata,T(x4,X4,xdata))
plot(xdata,T(x5,X5,xdata))
plot(xdata,T(x6,X6,xdata))

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
