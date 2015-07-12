clear

% Read CSV files.
xdata = [1:32]';
d2 = csvread('bwr_measurements/20cm/result.csv',1);
d3 = csvread('bwr_measurements/30cm/result.csv',1);
d5 = csvread('bwr_measurements/50cm/result.csv',1);
d6 = csvread('bwr_measurements/60cm/result.csv',1);
d7 = csvread('bwr_measurements/70cm/result.csv',1);

% Setup figure properties.
fontSize = 10;
fontSizeAxes = 8;
fontWeight = 'normal';
figurePosition = [440 378 370 300];   % [x y width height]


%%%%%%%%%%%%%%%%%

% Plot number of OPS
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

hold on
s = 6; % Number of OPS.
yLabelName = 'Number of OPS';

scatter (xdata,d2(:,s),'filled');
scatter (xdata,d3(:,s),'filled')
scatter (xdata,d5(:,s),'filled')
scatter (xdata,d6(:,s),'filled')
scatter (xdata,d7(:,s),'filled')

legend('20cm','30 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;

% Number of OPS curve fitting shenanigans.
cFig = figure;
set(cFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

x0 = [20, 3, 100];
hold on

ydata = d2(:,s);
F = @(x,xdata)-x(1)*log(x(2)*xdata)+x(3);
[x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
plot(xdata,F(x,xdata))

ydata = d3(:,s);
F = @(x,xdata)-x(1)*log(x(2)*xdata)+x(3);
[x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
plot(xdata,F(x,xdata))

ydata = d5(:,s);
F = @(x,xdata)-x(1)*log(x(2)*xdata)+x(3);
[x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
plot(xdata,F(x,xdata))

ydata = d6(:,s);
F = @(x,xdata)-x(1)*log(x(2)*xdata)+x(3);
[x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
plot(xdata,F(x,xdata))

x7 = [1:23]';
ydata = d7(1:23,s);
F = @(x,xdata)-x(1)*log(x(2)*xdata)+x(3);
[x,resnorm] = lsqcurvefit(F,x0,x7,ydata)
plot(x7,F(x,x7))

legend('20cm','30 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

hold off;

    %%%%%%%%%%%%%

    % Plot Efficiency
    hFig = figure;
    set(hFig, 'Position', figurePosition)
    set(gcf,'Renderer','painters');

    hold on
    s = 4; % Efficiency.
    yLabelName = 'Efficiency';

    scatter (xdata,d2(:,s),'filled');
    scatter (xdata,d3(:,s),'filled')
    scatter (xdata,d5(:,s),'filled')
    scatter (xdata,d6(:,s),'filled')
    scatter (xdata,d7(:,s),'filled')

    legend('20cm','30 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
    axis([0,32,-inf,inf]);
    set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
    grid minor;

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

    x0 = [0.1, 0];
    hold on

    ydata = d2(:,s);
    F = @(x,xdata)(-x(1)*xdata)+x(2);
    [x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
    plot(xdata,F(x,xdata))

    ydata = d3(:,s);
    F = @(x,xdata)(-x(1)*xdata)+x(2);
    [x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
    plot(xdata,F(x,xdata))

    ydata = d5(:,s);
    F = @(x,xdata)(-x(1)*xdata)+x(2);
    [x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
    plot(xdata,F(x,xdata))

    ydata = d6(:,s);
    F = @(x,xdata)(-x(1)*xdata)+x(2);
    [x,resnorm] = lsqcurvefit(F,x0,xdata,ydata)
    plot(xdata,F(x,xdata))

    ydata = d7(1:23,s);
    F = @(x,xdata)(-x(1)*xdata)+x(2);
    [x,resnorm] = lsqcurvefit(F,x0,x7,ydata)
    plot(x7,F(x,x7))

    legend('20cm','30 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
    axis([0,32,-inf,inf]);
    set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
    grid minor;

    h = xlabel('WordCount');
    set(h,'FontSize',fontSize);
    set(h,'fontweight', fontWeight);

    h = ylabel(yLabelName);
    set(h,'FontSize',fontSize);
    set(h,'fontweight', fontWeight);

    hold off;
    
    %%%%%%%%%%%%%

% Plot Throughput
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

hold on
s = 5; % Throughput.
yLabelName = 'Throughput [B/sec]';

scatter (xdata,d2(:,s),'filled');
scatter (xdata,d3(:,s),'filled')
scatter (xdata,d5(:,s),'filled')
scatter (xdata,d6(:,s),'filled')
scatter (xdata,d7(:,s),'filled')

legend('20cm','30 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel(yLabelName);
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);
hold off;

%TODO: Curve fitting on throughput.

