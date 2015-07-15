clear
close all;

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

%d2 = csvread('bwr_measurements/20cm/result.csv',1);
%d3 = csvread('bwr_measurements/30cm/result.csv',1);
%d5 = csvread('bwr_measurements/50cm/result.csv',1);
%d6 = csvread('bwr_measurements/60cm/result.csv',1);
%d7 = csvread('bwr_measurements/70cm/result.csv',1);

% Setup figure properties.
fontSize = 10;
fontSizeAxes = 8;
fontWeight = 'normal';
figurePosition = [440 378 370 300];   % [x y width height]


%%%%%%%%%%%%%%%%%
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
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;

% Efficiency curve fitting shenanigans.
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
s = 4;
yLabelName = 'Efficiency';

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

% Now use found parameters to plot OPS as double check.
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
s = 2; % Total operations.
yLabelName = 'Number of OPS';
hold on;

O2 = d2(:,:,s).*((-x2(1)*xdata+x2(2))./10);
O3 = d3(:,:,s).*((-x3(1)*xdata+x3(2))./10);
O4 = d4(:,:,s).*((-x4(1)*xdata+x4(2))./10);
O5 = d5(:,:,s).*((-x5(1)*xdata+x5(2))./10);
O6 = d6(:,:,s).*((-x6(1)*xdata+x6(2))./10);

plot(xdata,O2);
plot(xdata,O3);
plot(xdata,O4);
plot(xdata,O5);
plot(xdata,O6);

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
set(gca,'ylim',[0 140]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;

% And plot throughput as triple check.

cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
s = 2; % Total operations.
yLabelName = 'Throughput';
hold on;

T2 = d2(:,:,s).*((-x2(1)*xdata.^2+x2(2)*xdata)./10);
T3 = d3(:,:,s).*((-x3(1)*xdata.^2+x3(2)*xdata)./10);
T4 = d4(:,:,s).*((-x4(1)*xdata.^2+x4(2)*xdata)./10);
T5 = d5(:,:,s).*((-x5(1)*xdata.^2+x5(2)*xdata)./10);
T6 = d6(:,:,s).*((-x6(1)*xdata.^2+x6(2)*xdata)./10);

plot(xdata,T2);
plot(xdata,T3);
plot(xdata,T4);
plot(xdata,T5);
plot(xdata,T6);

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
set(gca,'ylim',[0 inf]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% OPS curve fitting shenanigans.
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
s = 6;
yLabelName = 'Number of OPS';

x0 = [0, 140];
hold on

ydata = d2(:,:,s);
F2 = @(x,xdata)x(1)./(xdata+1)+x(2);
[x2,resnorm] = lsqcurvefit(F2,x0,xdata,ydata)
plot(xdata,F2(x2,xdata))

ydata = d3(:,:,s);
F3 = @(x,xdata)x(1)./(xdata+1)+x(2);
[x3,resnorm] = lsqcurvefit(F3,x0,xdata,ydata)
plot(xdata,F3(x3,xdata))

ydata = d4(:,:,s);
F4 = @(x,xdata)x(1)./(xdata+1)+x(2);
[x4,resnorm] = lsqcurvefit(F4,x0,xdata,ydata)
plot(xdata,F4(x4,xdata))

ydata = d5(:,:,s);
F5 = @(x,xdata)x(1)./(xdata+1)+x(2);
[x5,resnorm] = lsqcurvefit(F5,x0,xdata,ydata)
plot(xdata,F5(x5,xdata))

ydata = d6(:,:,s);
F6 = @(x,xdata)x(1)./(xdata+1)+x(2);
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

% Now use found parameters to plot efficiency as double check.
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');
s = 2; % Total operations.
yLabelName = 'Efficiency';
hold on;

E2 = (10*(x2(1)./(xdata+1)+x2(2)))./d2(:,:,s);
E3 = (10*(x3(1)./(xdata+1)+x3(2)))./d3(:,:,s);
E4 = (10*(x4(1)./(xdata+1)+x4(2)))./d4(:,:,s);
E5 = (10*(x5(1)./(xdata+1)+x5(2)))./d5(:,:,s);
E6 = (10*(x6(1)./(xdata+1)+x6(2)))./d6(:,:,s);

scatter (xdata,E2,'x');
scatter (xdata,E3,'+')
scatter (xdata,E4,'filled','s')
scatter (xdata,E5,'filled','v')
scatter (xdata,E6,'*')

legend('20 cm','30 cm','40 cm','50 cm','60 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
set(gca,'ylim',[0 inf]);
grid minor;
box on;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;
