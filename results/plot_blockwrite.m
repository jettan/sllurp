clear

% Uncomment the parameter to plot.
%s = 4; % efficiency
%s = 5; % throughput
s = 6; % success operations per second

% Read CSV files.

x = [1:32];
d2 = csvread('bwr_measurements/20cm/result.csv',1);
d3 = csvread('bwr_measurements/30cm/result.csv',1);
%d4 = csvread('bwr_measurements/40cm/result.csv',1);
d5 = csvread('bwr_measurements/50cm/result.csv',1);
d6 = csvread('bwr_measurements/60cm/result.csv',1);
d7 = csvread('bwr_measurements/70cm/result.csv',1);

fontSize = 10;
fontSizeAxes = 8;
fontWeight = 'normal';
figurePosition = [440 378 370 300];   % [x y width height]
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

hold on
scatter (x,d2(:,s),'filled');
scatter (x,d3(:,s),'filled')
%scatter (x,d4(:,s),'filled')
scatter (x,d5(:,s),'filled')
scatter (x,d6(:,s),'filled')
scatter (x,d7(:,s),'filled')


%legend('20cm','30 cm','40 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
legend('20cm','30 cm','50 cm','60 cm','70 cm','FontSize',fontSize,'FontWeight',fontWeight);
axis([0,32,-inf,inf]);
set(gca, 'xtick',[1,4,8,12,16,20,24,28,32]);
grid minor;

h = xlabel('WordCount');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

h = ylabel('Number of OPS');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

