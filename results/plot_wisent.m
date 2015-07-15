clear
close all;

% Uncomment the parameter to plot.
%s = 1; %payload,
%s = 2; %messages_sent,
%s = 3; %messages_resent
%s = 4; %resend_ratio,
%s = 5; %success_reports,
%s = 6; %total_reports,
%s = 7;  %efficiency,
%s = 8;  %success_opm,
%s = 9;% total_opm,
%s = 10; %runtime,
%s = 11; %time_per_message,
%s = 12; %messages_per_second,
%s = 13; %time_per_op,
%s = 14; %success_ops,
%s = 15; %total_ops,
%s = 16; %goodput,
s = 17; %throughput

% Read CSV files.
d2 = csvread('wisent/20cm/result.csv',1);
d3 = csvread('wisent/30cm/result.csv',1);
d4 = csvread('wisent/40cm/result.csv',1);
d5 = csvread('wisent/50cm/result.csv',1);
d6 = csvread('wisent/60cm/result.csv',1);

% Reshape matrices.
r2 = reshape(d2,5,16,17);
r3 = reshape(d3,5,16,17);
r4 = reshape(d4,5,16,17);
r5 = reshape(d5,5,16,17);
r6 = reshape(d6,5,16,17);

fontSize = 10;
fontSizeAxes = 8;
fontWeight = 'normal';
figurePosition = [440 378 560 300];   % [x y width height]
hFig = figure;
set(hFig, 'Position', figurePosition)
set(gcf,'Renderer','painters');

data = [r2(:,:,s),r3(:,:,s),r4(:,:,s),r5(:,:,s),r6(:,:,s)];

% Boxplot grouping stuff.
a = [];
for j=1:5,
    a = [a 1:16];
end
l = [repmat({'20'},1,16), repmat({'30'},1,16),repmat({'40'},1,16),repmat({'50'},1,16),repmat({'60'},1,16)];

% Boxplot.
b = boxplot(data,{a,l},'colors',repmat('rbgmk',1,16),'factorgap',[5 2], ...
'labelverbosity','minor', 'factorseparator',1);
set(findobj(get(b(1), 'parent'), 'type', 'text'), 'FontSize', fontSize, ...
    'FontWeight', fontWeight);

% Recolor boxes. 
colors = repmat('kmgbr',1,16);
h = findobj(gca,'Tag','Box');
for j=1:length(h)
   patch(get(h(j),'XData'),get(h(j),'YData'), colors(j),'FaceAlpha',1,'EdgeColor','none');
end

delete(findobj(gca,'Type','text','String','20'));
delete(findobj(gca,'Type','text','String','30'));
delete(findobj(gca,'Type','text','String','40'));
delete(findobj(gca,'Type','text','String','50'));
delete(findobj(gca,'Type','text','String','60'));

h = xlabel('Message payload size (words)');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);


h = ylabel('Throughput [B/sec]');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);


% Turn on legend.
h = legend(findobj(gca,'Tag','Box'),'60 cm','50 cm','40 cm','30 cm','20 cm', 'Location','northwest');
set(h,'FontSize',fontSize);
set(h,'fontweight', fontWeight);

set(findobj('type','axes'),'fontsize',fontSizeAxes)

txt=findobj(gca,'Type','text');
set(txt,'FontSize',fontSize);
set(txt,'VerticalAlignment','Middle');
set(hFig, 'paperpositionmode', 'auto');
