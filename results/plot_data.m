clear

% PARAMETER TO PLOT.
%s = 1; %payload,
%s = 2; %messages_sent,
%s = 3; %messages_resent
%s = 4; %resend_ratio,
%s = 5; %success_reports,
%s = 6; %total_reports,
s = 7;  %efficiency,
%s = 8;  %success_opm,
%s = 9;% total_opm,
%s = 10; %runtime,
%s = 11; %time_per_message,
%s = 12; %messages_per_second,
%s = 13; %time_per_op,
%s = 14; %success_ops,
%s = 15; %total_ops,
%s = 16; %goodput,
%s = 17; %throughput

d2 = csvread('wisent/20cm/result.csv',1);
d3 = csvread('wisent/30cm/result.csv',1);
d4 = csvread('wisent/40cm/result.csv',1);
d5 = csvread('wisent/50cm/result.csv',1);
d6 = csvread('wisent/60cm/result.csv',1);

r2 = reshape(d2,5,16,17);
r3 = reshape(d3,5,16,17);
r4 = reshape(d4,5,16,17);
r5 = reshape(d5,5,16,17);
r6 = reshape(d6,5,16,17);

a = [];
for j=1:5,
    a = [a 1:16];
end

data = [r2(:,:,s),r3(:,:,s),r4(:,:,s),r5(:,:,s),r6(:,:,s)];
l = [repmat({'20'},1,16), repmat({'30'},1,16),repmat({'40'},1,16),repmat({'50'},1,16),repmat({'60'},1,16)];
h = boxplot(data,{a,l},'colors',repmat('rbgmk',1,16),'factorgap',[5 2],'labelverbosity','minor', 'factorseparator',1, 'plotstyle','compact', 'outliersize',0.1, 'medianstyle', 'line');
legend(findobj(gca,'Tag','Box'),'60cm','50cm','40cm','30cm','20cm', 'Location','northwest');
set(findobj(gca,'Type','text'),'FontSize',8)
xlabel('Message payload size (words)')
%ylabel('Efficiency')